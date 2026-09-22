import type { Role } from "@pol/types";

/** Role → default home path (route map + matrix). Server remains authoritative. */
export const roleHome: Record<Role, string> = {
  ADMIN_SUPER: "/admin",
  OPS_AGENT: "/ops",
  FIELD_ACTIVATOR: "/field",
  VENDOR_OWNER: "/vendor",
  VENDOR_STAFF: "/vendor",
  RETAILER_OWNER: "/retailer",
  RETAILER_STAFF: "/retailer",
};

export type RouteAccess = "public" | "auth" | Role[];

/** Route prefix → allowed (UX gate only). */
export const routeAccess: Record<string, RouteAccess> = {
  "/auth": "public",
  "/": "public",
  "/retailers": "public",
  "/vendors": "public",
  "/how": "public",
  "/pilot": "public",
  "/about": "public",
  "/contact": "public",
  "/legal": "public",
  "/dev": "public",
  "/retailer": ["RETAILER_OWNER", "RETAILER_STAFF"],
  "/vendor": ["VENDOR_OWNER", "VENDOR_STAFF"],
  "/ops": ["OPS_AGENT", "ADMIN_SUPER"],
  "/admin": ["ADMIN_SUPER"],
  "/field": ["FIELD_ACTIVATOR", "OPS_AGENT"],
  "/profile": "auth",
  "/notifications": "auth",
};

export function pathAllowed(path: string, role: Role | null): boolean {
  const hit = Object.entries(routeAccess)
    .sort(([a], [b]) => b.length - a.length)
    .find(([prefix]) =>
      prefix === "/" ? path === "/" : path === prefix || path.startsWith(`${prefix}/`),
    );
  if (!hit) return false;
  const access = hit[1];
  if (access === "public") return true;
  if (access === "auth") return role !== null;
  if (!role) return false;
  return access.includes(role);
}
