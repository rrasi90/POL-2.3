import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PREFIXES = [
  "/",
  "/auth",
  "/retailers",
  "/vendors",
  "/how",
  "/pilot",
  "/about",
  "/contact",
  "/legal",
  "/dev",
  "/api/v1",
  "/_next",
];

const ROLE_PREFIX: Array<{ prefix: string; roles: string[] }> = [
  { prefix: "/retailer", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { prefix: "/vendor", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { prefix: "/ops", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { prefix: "/admin", roles: ["ADMIN_SUPER"] },
  { prefix: "/field", roles: ["FIELD_ACTIVATOR", "OPS_AGENT"] },
  { prefix: "/profile", roles: ["*"] },
  { prefix: "/notifications", roles: ["*"] },
];

function isPublic(path: string): boolean {
  if (path === "/") return true;
  return PUBLIC_PREFIXES.some((p) => p !== "/" && (path === p || path.startsWith(`${p}/`)));
}

/**
 * QA branch: /api/v1 is intentionally public because the Vercel mock server
 * is the test data source. This does not model backend authorization.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (isPublic(pathname)) return NextResponse.next();

  const session = request.cookies.get("pol.session")?.value;
  const role = request.cookies.get("pol.role")?.value ?? null;

  const rule = ROLE_PREFIX.find(
    (r) => pathname === r.prefix || pathname.startsWith(`${r.prefix}/`),
  );

  if (!rule) {
    if (!session) {
      const url = request.nextUrl.clone();
      url.pathname = "/auth/login";
      url.searchParams.set("next", pathname);
      return NextResponse.redirect(url);
    }
    return NextResponse.next();
  }

  if (!session) {
    const url = request.nextUrl.clone();
    url.pathname = "/auth/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  if (rule.roles[0] !== "*" && role && !rule.roles.includes(role)) {
    const home =
      role === "RETAILER_OWNER" || role === "RETAILER_STAFF"
        ? "/retailer"
        : role === "VENDOR_OWNER" || role === "VENDOR_STAFF"
          ? "/vendor"
          : role === "OPS_AGENT" || role === "ADMIN_SUPER"
            ? "/ops"
            : role === "FIELD_ACTIVATOR"
              ? "/field"
              : "/";
    const url = request.nextUrl.clone();
    url.pathname = home;
    url.search = "";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
