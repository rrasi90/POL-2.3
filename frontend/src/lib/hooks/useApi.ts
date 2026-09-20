"use client";

import useSWR from "swr";
import { api } from "@/lib/api/client";
import type { PaginatedResponse } from "@/lib/types";

export function useApi<T>(path: string | null, params?: Record<string, string>) {
  return useSWR<T>(
    path,
    () => api.get<T>(path!, params),
    { revalidateOnFocus: false, shouldRetryOnError: false },
  );
}

export function usePaginatedApi<T>(
  path: string | null,
  offset = 0,
  limit = 50,
  params?: Record<string, string>,
) {
  const allParams = { ...params, offset: String(offset), limit: String(limit) };
  return useApi<PaginatedResponse<T>>(path, allParams);
}
