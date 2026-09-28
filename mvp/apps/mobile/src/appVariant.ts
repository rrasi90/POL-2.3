export type AppVariant = "retailer" | "vendor";

const raw = (process.env.EXPO_PUBLIC_APP_VARIANT ?? "retailer").toLowerCase();

export const APP_VARIANT: AppVariant = raw === "vendor" ? "vendor" : "retailer";
export const APP_NAME = APP_VARIANT === "vendor" ? "پل بنکدار" : "پل بازار";
export const ALLOWED_ROLES =
  APP_VARIANT === "vendor"
    ? (["VENDOR_OWNER", "VENDOR_STAFF"] as const)
    : (["RETAILER_OWNER", "RETAILER_STAFF"] as const);

export function isAllowedRole(role: string): boolean {
  return (ALLOWED_ROLES as readonly string[]).includes(role);
}
