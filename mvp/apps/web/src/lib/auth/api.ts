"use client";

import { useAuthStore } from "./store";
import { createApiClient, type ApiClient } from "@pol/api-client";

let client: ApiClient | null = null;

export function getApi(): ApiClient {
  if (!client) {
    client = createApiClient({
      baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
      getAccessToken: () => useAuthStore.getState().accessToken,
      onUnauthorized: () => useAuthStore.getState().clear(),
    });
  }
  return client;
}
