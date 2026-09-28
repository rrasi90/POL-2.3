import * as SecureStore from "expo-secure-store";

export type ApiEnvelope<T> =
  | { success: true; data: T }
  | { success: false; error: { code: string; message: string; details?: Record<string, unknown> } };

export type RequestOptions = {
  headers?: Record<string, string>;
};

export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const BASE = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://10.0.2.2:8000";
const ACCESS_KEY = "pol.access_token";
const REFRESH_KEY = "pol.refresh_token";
const ROLE_KEY = "pol.session_role";

let accessToken: string | null = null;
let refreshInFlight: Promise<boolean> | null = null;
let online = true;
const listeners = new Set<(v: boolean) => void>();

export function setToken(token: string | null): void {
  accessToken = token;
}

export function getToken(): string | null {
  return accessToken;
}

export async function persistSession(access: string, refresh: string | null | undefined, role?: string | null): Promise<void> {
  accessToken = access;
  await SecureStore.setItemAsync(ACCESS_KEY, access, {
    keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  });
  if (refresh) {
    await SecureStore.setItemAsync(REFRESH_KEY, refresh, {
      keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
    });
  }
  if (role) {
    await SecureStore.setItemAsync(ROLE_KEY, role, {
      keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
    });
  }
}

export async function clearSession(): Promise<void> {
  accessToken = null;
  await Promise.allSettled([
    SecureStore.deleteItemAsync(ACCESS_KEY),
    SecureStore.deleteItemAsync(REFRESH_KEY),
    SecureStore.deleteItemAsync(ROLE_KEY),
  ]);
}

async function refreshAccessToken(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const refreshToken = await SecureStore.getItemAsync(REFRESH_KEY);
      if (!refreshToken) return false;
      try {
        const res = await fetch(BASE + "/api/v1/auth/refresh", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!res.ok) return false;
        const payload = (await res.json()) as ApiEnvelope<{
          access_token: string;
          refresh_token?: string | null;
        }>;
        if (payload.success === false) return false;
        if (!payload.data?.access_token) return false;
        await persistSession(payload.data.access_token, payload.data.refresh_token ?? refreshToken, await SecureStore.getItemAsync(ROLE_KEY));
        return true;
      } catch {
        return false;
      }
    })().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

export async function restoreSession(): Promise<{ restored: boolean; role: string | null }> {
  const storedAccess = await SecureStore.getItemAsync(ACCESS_KEY);
  const storedRefresh = await SecureStore.getItemAsync(REFRESH_KEY);
  const storedRole = await SecureStore.getItemAsync(ROLE_KEY);
  if (storedAccess) {
    accessToken = storedAccess;
    return { restored: true, role: storedRole };
  }
  if (storedRefresh && await refreshAccessToken()) {
    return {
      restored: Boolean(accessToken),
      role: await SecureStore.getItemAsync(ROLE_KEY),
    };
  }
  await clearSession();
  return { restored: false, role: null };
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options?: RequestOptions,
  retried = false,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers ?? {}),
  };
  if (accessToken) headers.Authorization = "Bearer " + accessToken;

  try {
    const res = await fetch(BASE + path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    setOnline(true);

    let payload: ApiEnvelope<T>;
    try {
      payload = (await res.json()) as ApiEnvelope<T>;
    } catch {
      throw new ApiError("PARSE_ERROR", "Invalid JSON response", res.status);
    }

    if (res.status === 401 && !retried && !path.startsWith("/api/v1/auth/refresh")) {
      if (await refreshAccessToken()) {
        return request<T>(method, path, body, options, true);
      }
      await clearSession();
      throw new ApiError("AUTH_EXPIRED", "نشست منقضی شده است.", 401);
    }

    if (payload.success === false) {
      throw new ApiError(payload.error.code, payload.error.message, res.status);
    }
    return payload.data;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    setOnline(false);
    throw new ApiError(
      "NETWORK",
      err instanceof Error ? err.message : "Network error",
      0,
    );
  }
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>("GET", path, undefined, options),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("POST", path, body, options),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("PATCH", path, body, options),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("PUT", path, body, options),
  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>("DELETE", path, undefined, options),
};

export async function healthz(): Promise<boolean> {
  try {
    const res = await fetch(BASE + "/healthz", { method: "GET" });
    setOnline(res.ok);
    return res.ok;
  } catch {
    setOnline(false);
    return false;
  }
}

export function isOnline(): boolean {
  return online;
}

export function subscribeOnline(fn: (v: boolean) => void): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function setOnline(v: boolean): void {
  if (online === v) return;
  online = v;
  listeners.forEach((fn) => fn(v));
}
