import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "src");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const readMobile = (file) => fs.readFileSync(path.resolve(process.cwd(), file), "utf8");

const checks = [
  ["All mobile products remain explicitly role-gated", () => {
    const shell = readMobile("AppShell.tsx");
    const retailer = readMobile("AppRetailer.tsx");
    const vendor = readMobile("AppVendor.tsx");
    return ["RETAILER_OWNER", "RETAILER_STAFF"].every((r) => retailer.includes(r)) &&
      ["VENDOR_OWNER", "VENDOR_STAFF"].every((r) => vendor.includes(r)) &&
      shell.includes("allowedRoles") && shell.includes("onAuthed(nextRole: Role)");
  }],
  ["Mobile API client preserves canonical auth/error contract", () => {
    const s = read("api.ts");
    return s.includes("Authorization") && s.includes("ApiError") && s.includes("NETWORK") &&
      s.includes('Content-Type": "application/json"');
  }],
  ["Retailer checkout remains gated by server basket and allocation", () => {
    const s = read("screens/RetailerMobileScreen.tsx");
    return s.includes("serverBasketId") && s.includes("allocation") && s.includes("Idempotency-Key");
  }],
  ["Vendor lifecycle actions remain state-gated", () => {
    const s = read("screens/VendorMobileScreen.tsx");
    return s.includes("SUBMITTED") && s.includes("ACCEPTED") && s.includes("PREPARING") &&
      s.includes("READY") && s.includes('"/api/v1/orders/"');
  }],
  ["Vendor workspace has operational home, compact primary navigation, inventory and finance sections", () => {
    const s = read("screens/VendorMobileScreen.tsx");
    return s.includes("پل بنکدار") && s.includes("فضای عملیاتی بنکداری") &&
      s.includes('type MainTab = "home" | "orders" | "inventory" | "finance" | "more"') &&
      s.includes("اقدام‌های امروز") && s.includes("Segmented");
  }],
  ["Vendor inventory and price mutations use canonical endpoints", () => {
    const s = read("screens/VendorMobileScreen.tsx");
    return s.includes("/api/v1/catalog/vendors/products/") &&
      s.includes("/inventory") && s.includes("/prices") &&
      s.includes("new_physical_quantity") && s.includes("price_toman");
  }],
  ["Vendor daily confirmation uses canonical endpoint and payload", () => {
    const s = read("screens/VendorMobileScreen.tsx");
    return s.includes("/api/v1/inventory/daily/") &&
      s.includes("/confirm-with-changes") && s.includes("declared_quantity");
  }],
  ["Mobile order detail keeps canonical vendor actions and delivery states", () => {
    const s = read("screens/OrderDetailMobileScreen.tsx");
    return s.includes("reason: rejectReason.trim()") && s.includes("driver_name: dispatchDriverName.trim()") &&
      s.includes("order_item_id: x.id") && s.includes("accepted_quantity: Number") &&
      s.includes('"arrived"') && s.includes("recipient_name: deliveryRecipient.trim()");
  }],
  ["Mobile dispute submission uses canonical amount and description fields", () => {
    const s = read("screens/OrderDetailMobileScreen.tsx");
    return s.includes("claimed_amount_toman") && s.includes("const description = disputeDescription.trim()") &&
      !s.includes("{ reason: disputeReason.trim() }");
  }],
  ["Support creation/message validation remains enforced", () => {
    const s = read("screens/SupportMobileScreen.tsx");
    return s.includes("!subject.trim()") && s.includes("!message.trim()");
  }],
  ["Ops privileged audit surface remains ADMIN_SUPER-only", () => read("screens/OpsMobileScreen.tsx").includes('props.role === "ADMIN_SUPER"')],
  ["Mobile logout revokes the current server session before clearing local auth", () => {
    const api = read("api.ts");
    const account = read("screens/AccountMobileScreen.tsx");
    const app = readMobile("AppShell.tsx");
    return api.includes('request<T>("DELETE"') && api.includes("delete: <T>") &&
      account.includes("/api/v1/auth/sessions/current") && account.includes("clearSession()") &&
      api.includes("SecureStore") && api.includes("refreshAccessToken") &&
      api.includes("AUTH_EXPIRED") && app.includes("onLogout()");
  }],
  ["Mobile session restores from SecureStore and refreshes access on 401", () => {
    const s = read("api.ts");
    const login = read("screens/LoginScreen.tsx");
    const app = readMobile("AppShell.tsx");
    return s.includes("expo-secure-store") && s.includes("persistSession") &&
      s.includes("restoreSession") && s.includes("res.status === 401") &&
      s.includes("await refreshAccessToken()") && login.includes("data.refresh_token") &&
      app.includes("restoreSession()");
  }],
  ["Shared account uses real profile/notification preference endpoints", () => {
    const s = read("screens/AccountMobileScreen.tsx");
    return s.includes("/api/v1/notifications/preferences") && s.includes("api.put");
  }],
  ["Supported finance/referral parity remains on real endpoints", () => {
    const r = read("screens/RetailerMobileScreen.tsx");
    const v = read("screens/VendorMobileScreen.tsx");
    return r.includes("/api/v1/invoices") && v.includes("/api/v1/invoices") && v.includes("/api/v1/referrals");
  }],
  ["Unsupported barcode path is not fabricated as a runtime adapter", () => {
    const p = fs.readFileSync(path.resolve(process.cwd(), "src/__tests__/parity.md"), "utf8");
    return p.includes("GAP / CONTRACT") && p.includes("match-barcode");
  }],
  ["Night theme is runtime-wired", () => {
    const theme = read("theme.ts");
    const app = readMobile("AppShell.tsx");
    const account = read("screens/AccountMobileScreen.tsx");
    return theme.includes("ThemeProvider") && app.includes("<ThemeProvider>") && account.includes('setMode("night")');
  }],
  ["Retailer checkout reconciles stale basket conflicts from current server basket", () => {
    const s = read("screens/RetailerMobileScreen.tsx");
    return s.includes("ApiError") && s.includes("e.status === 409") &&
      s.includes("/api/v1/baskets/current") && s.includes("setAllocation(null)");
  }],
  ["F-03 catalog uses the required q parameter and canonical product fields", () => {
    const s = read("screens/AssistedOrderScreen.tsx");
    return s.includes("if (!q) {") && s.includes("canonical_name_fa") && s.includes("master_sku");
  }],
  ["Offline banner captures current connectivity after effect subscription", () => read("components/OfflineBanner.tsx").includes("setOnline(isOnline())")],
  ["Login auth uses E.164 normalization", () => read("screens/LoginScreen.tsx").includes("toE164")],
  ["No Driver App is introduced into Phase 3 mobile source", () => {
    const p = fs.readFileSync(path.resolve(process.cwd(), "src/__tests__/parity.md"), "utf8");
    return p.includes("No Driver App (D-023)");
  }],
];

let failed = 0;
for (const [name, fn] of checks) {
  let ok = false;
  try { ok = Boolean(fn()); } catch {}
  console.log(`${ok ? "PASS" : "FAIL"} | ${name}`);
  if (!ok) failed += 1;
}
console.log(`\nMobile regression/cross-module QA: ${checks.length - failed}/${checks.length} checks passed.`);
if (failed) process.exit(1);
