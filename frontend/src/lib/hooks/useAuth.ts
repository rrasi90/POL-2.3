"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuthStore } from "@/store";

export function useRequireAuth() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/auth");
    }
  }, [isAuthenticated, router]);

  return { isAuthenticated, user };
}

export function useRequireRole(...roles: string[]) {
  const { isAuthenticated, user } = useRequireAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated && user && !roles.includes(user.role)) {
      router.replace(getDefaultRoute(user.role));
    }
  }, [isAuthenticated, user, roles, router]);

  return { isAuthenticated, user, hasRole: user ? roles.includes(user.role) : false };
}

export function getDefaultRoute(role: string): string {
  switch (role) {
    case "ADMIN_SUPER": return "/admin";
    case "OPS_AGENT": return "/ops";
    case "FIELD_ACTIVATOR": return "/field";
    case "VENDOR_OWNER":
    case "VENDOR_STAFF": return "/vendor";
    case "RETAILER_OWNER":
    case "RETAILER_STAFF": return "/retailer";
    default: return "/";
  }
}
