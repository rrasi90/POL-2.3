"use client";

import { useAuthStore } from "./store";
import { createApiClient, type ApiClient } from "@pol/api-client";
import type { RefreshResponse } from "@pol/types";

const baseUrl = () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

let client: ApiClient | null = null;
let refreshInFlight: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch(`${baseUrl()}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });
    if (!res.ok) return false;
    const payload = (await res.json()) as { success?: boolean; data?: RefreshResponse };
    const next = payload?.success === true ? payload.data?.access_token : undefined;
    if (typeof next !== "string" || next.length === 0) return false;
    // Preserve the rehydrated profile: setSession persists user/role and a bare
    // token update would overwrite pol.auth.profile with nulls, bouncing the
    // user to /auth/login on the next RequireRole check.
    const current = useAuthStore.getState();
    useAuthStore.getState().setSession({
      accessToken: next,
      user: current.user,
      role: current.role,
    });
    return true;
  } catch {
    return false;
  }
}

export function getApi(): ApiClient {
  if (!client) {
    client = createApiClient({
      baseUrl: baseUrl(),
      getAccessToken: () => useAuthStore.getState().accessToken,
      onUnauthorized: () => {
        useAuthStore.getState().clear();
        useAuthStore.getState().markSessionExpired();
      },
      onRefresh: () => {
        if (!refreshInFlight) {
          refreshInFlight = tryRefresh().finally(() => {
            refreshInFlight = null;
          });
        }
        return refreshInFlight;
      },
    });
  }
  return client;
}
