"use client";

import { useAuthStore } from "./store";
import { useEffect } from "react";

/** Mirrors session into cookies for middleware UX gate (not authorization SSoT). */
export function SessionCookieSync() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const role = useAuthStore((s) => s.role);

  useEffect(() => {
    if (typeof document === "undefined") return;
    if (accessToken) {
      document.cookie = `pol.session=1; path=/; max-age=${7 * 24 * 3600}; samesite=lax`;
      if (role) document.cookie = `pol.role=${role}; path=/; max-age=${7 * 24 * 3600}; samesite=lax`;
    } else {
      document.cookie = "pol.session=; path=/; max-age=0";
      document.cookie = "pol.role=; path=/; max-age=0";
    }
  }, [accessToken, role]);

  return null;
}
