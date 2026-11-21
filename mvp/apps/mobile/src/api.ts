import * as SecureStore from "expo-secure-store";
import { mockRequest } from "./mock/mockTransport";

export type ApiEnvelope<T> =
  | { success: true; data: T }
  | { success: false; error: { code: string; message: string; details?: Record<string, unknown> } };

export type RequestOptions = {
  headers?: Record<string, string>;
};

function userFacingError(code: string, message: string, status: number): string {
  if (status === 401 || code === "AUTH_EXPIRED") return "نشست شما منقضی شده است؛ دوباره وارد شوید.";
  if (status === 403 || /PERMISSION|FORBIDDEN|ACCESS_DENIED/i.test(code)) return "دسترسی شما برای این عملیات مجاز نیست.";
  if (status === 404 || /NOT_FOUND/i.test(code)) return "اطلاعات موردنظر پیدا نشد.";
  if (status === 409 || /CONFLICT|IDEMPOTENCY/i.test(code)) return "این عملیات با وضعیت فعلی داده‌ها تعارض دارد؛ دوباره بررسی کنید.";
  if (status === 422 || /VALIDATION|INVALID/i.test(code)) return "داده‌های واردشده معتبر نیستند.";
  if (code === "NETWORK") return "اتصال به سرویس برقرار نشد؛ اتصال اینترنت را بررسی کنید.";
  if (code === "PARSE_ERROR") return "پاسخ سرویس قابل پردازش نبود.";
  return message || "عملیات ناموفق بود.";
}

export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number,
  ) {
    super(userFacingError(code, message, status));
    this.name = "ApiError";
  }
}

export const DATA_MODE = (process.env.EXPO_PUBLIC_DATA_MODE ?? "live").toLowerCase();
const MOCK_MODE = DATA_MODE === "mock";
export function isMockMode(): boolean { return MOCK_MODE; }

export function getApiBaseUrl(): string { return BASE; }

const BASE = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://10.0.2.2:8000";
const REQUEST_TIMEOUT_MS = 20000;
const HEALTH_TIMEOUT_MS = 5000;
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
  if (MOCK_MODE) return false;
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
    if (MOCK_MODE) {
      const mockHeaders: Record<string, string> = { ...headers };
      try {
        const value = await mockRequest<T>(method, path, body, mockHeaders);
        setOnline(true);
        return value;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Mock request failed";
        if (/Mock permission denied/i.test(message)) throw new ApiError("FORBIDDEN", message, 403);
        if (/not found/i.test(message)) throw new ApiError("NOT_FOUND", message, 404);
        if (/invalid|must contain|required/i.test(message)) throw new ApiError("VALIDATION", message, 422);
        throw new ApiError("MOCK_ERROR", message, 500);
      }
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    let res: Response;
    try {
      res = await fetch(BASE + path, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timer);
    }
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
    const message =
      err instanceof Error && err.name === "AbortError"
        ? "درخواست بیش از حد طول کشید و لغو شد."
        : err instanceof Error
          ? err.message
          : "Network error";
    throw new ApiError("NETWORK", message, 0);
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
    if (MOCK_MODE) {
      await mockRequest("GET", "/healthz", undefined, accessToken ? { Authorization: "Bearer " + accessToken } : {});
      setOnline(true);
      return true;
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);
    try {
      const res = await fetch(BASE + "/healthz", { method: "GET", signal: controller.signal });
      setOnline(res.ok);
      return res.ok;
    } finally {
      clearTimeout(timer);
    }
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
