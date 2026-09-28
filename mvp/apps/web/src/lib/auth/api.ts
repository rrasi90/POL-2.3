"use client";

import { useAuthStore } from "./store";
import { createApiClient, type ApiClient } from "@pol/api-client";
import type { RefreshResponse } from "@pol/types";

/**
 * QA branch rule: when NEXT_PUBLIC_API_BASE_URL is empty, use the same-origin
 * Next.js mock API under /api/v1. A real backend must be explicitly configured.
 */
const baseUrl = () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

let client: ApiClient | null = null;
let refreshInFlight: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  const { refreshToken } = useAuthStore.getState();
  if (!refreshToken) return false;
  try {
    const res = await fetch(`${baseUrl()}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return false;
    const payload = (await res.json()) as { success?: boolean; data?: RefreshResponse };
    const next = payload?.success === true ? payload.data?.access_token : undefined;
    if (typeof next !== "string" || next.length === 0) return false;
    useAuthStore.getState().setSession({ accessToken: next });
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
      onUnauthorized: () => useAuthStore.getState().clear(),
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
