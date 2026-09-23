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

let accessToken: string | null = null;
let online = true;
const listeners = new Set<(v: boolean) => void>();

export function setToken(token: string | null): void {
  accessToken = token;
}

export function getToken(): string | null {
  return accessToken;
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

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options?: RequestOptions,
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
