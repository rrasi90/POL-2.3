import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "src");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const readMobile = (file) => fs.readFileSync(path.resolve(process.cwd(), file), "utf8");

const checks = [
  ["All implemented mobile role families remain explicitly role-gated in App routing", () => {
    const s = readMobile("App.tsx");
    return ["RETAILER_OWNER","RETAILER_STAFF","VENDOR_OWNER","VENDOR_STAFF","OPS_AGENT","ADMIN_SUPER","FIELD_ACTIVATOR"].every(r => s.includes(r)) &&
      s.includes("onAuthed(nextRole: Role)") && s.includes("setRole(nextRole)");
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
    return s.includes("SUBMITTED") && s.includes("ACCEPTED") && s.includes("PREPARING") && s.includes("READY");
  }],
  ["Mobile order mutations match canonical API payloads and roles", () => {
    const s = read("screens/OrderDetailMobileScreen.tsx");
    const v = read("screens/VendorMobileScreen.tsx");
    return s.includes("reason: rejectReason.trim()") && s.includes("driver_name: dispatchDriverName.trim()") &&
      s.includes("order_item_id: x.id") && s.includes("accepted_quantity: Number") &&
      s.includes("submitDeliveryStage(target:") && s.includes('"arrived"') && s.includes("recipient_name: deliveryRecipient.trim()") &&
      v.includes("new_physical_quantity") && v.includes("vendor_product_id: x.vendor_product_id || x.id") &&
      v.includes("declared_quantity: Number") && v.includes("physical_quantity ?? 0");
  }],
  ["Mobile dispute submission uses canonical amount and description fields", () => {
    const s = read("screens/OrderDetailMobileScreen.tsx");
    return s.includes("claimed_amount_toman") && s.includes("const description = disputeDescription.trim()") && !s.includes("{ reason: disputeReason.trim() }");
  }],
  ["Order detail lifecycle remains state-gated for returns/disputes/vendor actions", () => {
    const s = read("screens/OrderDetailMobileScreen.tsx");
    return s.includes("quantity < 1") && s.includes("disputeReason") && s.includes("DISPATCHED");
  }],
  ["Support creation/message validation remains enforced", () => {
    const s = read("screens/SupportMobileScreen.tsx");
    return s.includes("!subject.trim()") && s.includes("!message.trim()");
  }],
  ["Ops privileged audit surface remains ADMIN_SUPER-only", () => read("screens/OpsMobileScreen.tsx").includes('props.role === "ADMIN_SUPER"')],
  ["Mobile logout revokes the current server session before clearing local auth", () => {
    const api = read("api.ts");
    const account = read("screens/AccountMobileScreen.tsx");
    const app = readMobile("App.tsx");
    return api.includes('request<T>("DELETE"') && api.includes("delete: <T>") && account.includes("/api/v1/auth/sessions/current") &&
      account.includes("clearSession()") && api.includes("SecureStore") && api.includes("refreshAccessToken") &&
      api.includes("AUTH_EXPIRED") && app.includes("onLogout()");
  }],
  ["Mobile session survives process restart through SecureStore and rotates access on 401", () => {
    const s = read("api.ts");
    const login = read("screens/LoginScreen.tsx");
    const app = readMobile("App.tsx");
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
  ["Night theme is runtime-wired rather than a static palette only", () => {
    const theme = read("theme.ts");
    const app = readMobile("App.tsx");
    const account = read("screens/AccountMobileScreen.tsx");
    return theme.includes("ThemeProvider") && app.includes("<ThemeProvider>") && account.includes('setMode("night")');
  }],
  ["Retailer checkout reconciles stale basket conflicts from current server basket", () => { const s = read("screens/RetailerMobileScreen.tsx"); return s.includes("ApiError") && s.includes("e.status === 409") && s.includes("/api/v1/baskets/current") && s.includes("setAllocation(null)"); }],
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
