import type { ApiResponse } from "@pol/types";

export interface ApiClientOptions {
  baseUrl: string;
  getAccessToken?: () => string | null | undefined;
  onUnauthorized?: () => void;
  /** SH-AUTH-03: invoked once on 401; return true to retry with the refreshed token. */
  onRefresh?: () => Promise<boolean>;
}

export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly details: Record<string, unknown>,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Thin HTTP client — envelope from scripts/api/errors.py (API_MAP §1). No business rules. */
export function createApiClient(opts: ApiClientOptions) {
  async function request<T>(
    method: string,
    path: string,
    body?: unknown,
    init?: RequestInit,
    retried = false,
  ): Promise<T> {
    const headers = new Headers(init?.headers);
    headers.set("Content-Type", "application/json");
    const token = opts.getAccessToken?.();
    if (token) headers.set("Authorization", `Bearer ${token}`);

    const res = await fetch(`${opts.baseUrl}${path}`, {
      ...init,
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });

    if (res.status === 401 && !retried && opts.onRefresh) {
      const refreshed = await opts.onRefresh();
      if (refreshed) return request<T>(method, path, body, init, true);
    }

    let payload: ApiResponse<T>;
    try {
      payload = (await res.json()) as ApiResponse<T>;
    } catch {
      throw new ApiError("PARSE_ERROR", "Invalid JSON response", {}, res.status);
    }

    if (payload.success === false) {
      const err = payload.error;
      if (res.status === 401) opts.onUnauthorized?.();
      throw new ApiError(err.code, err.message, err.details, res.status);
    }
    if (res.status === 401) {
      opts.onUnauthorized?.();
      throw new ApiError("UNAUTHORIZED", "Unauthorized", {}, res.status);
    }
    return payload.data;
  }

  return {
    get: <T>(path: string) => request<T>("GET", path),
    post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
    put: <T>(path: string, body?: unknown) => request<T>("PUT", path, body),
    patch: <T>(path: string, body?: unknown) => request<T>("PATCH", path, body),
    delete: <T>(path: string) => request<T>("DELETE", path),
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;
