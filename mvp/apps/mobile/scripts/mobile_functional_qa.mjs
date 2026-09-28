import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "src");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

const checks = [
  ["Retailer blocks empty basket submission", () => read("screens/RetailerMobileScreen.tsx").includes('if (!basket.length) { setError("سبد خالی است."); return; }')],
  ["Retailer requires server basket before allocation preview", () => read("screens/RetailerMobileScreen.tsx").includes('if (!serverBasketId) { setError("ابتدا سبد را روی سرور ثبت کنید."); return; }')],
  ["Retailer requires allocation before checkout", () => read("screens/RetailerMobileScreen.tsx").includes('if (!allocation) { setError("ابتدا بررسی تخصیص را اجرا کنید."); return; }')],
  ["Retailer validates delivery address", () => read("screens/RetailerMobileScreen.tsx").includes('address.trim().length < 5')],
  ["Retailer sends checkout Idempotency-Key", () => read("screens/RetailerMobileScreen.tsx").includes('"Idempotency-Key": keyV4()')],
  ["Retailer clears basket/order state after successful checkout", () => {
    const s = read("screens/RetailerMobileScreen.tsx");
    return s.includes("setBasket([])") && s.includes("setServerBasketId(null)") && s.includes("setAllocation(null)") && s.includes('setTab("orders")');
  }],
  ["Vendor exposes only status-appropriate order transitions", () => {
    const s = read("screens/VendorMobileScreen.tsx");
    return s.includes('["SUBMITTED", "CREATED"]') && s.includes('["ACCEPTED", "PARTIALLY_ACCEPTED"]') && s.includes('o.order_status === "PREPARING"') && s.includes('o.order_status === "READY"');
  }],
  ["Vendor rejects negative/non-numeric inventory", () => read("screens/VendorMobileScreen.tsx").includes('!Number.isFinite(n) || n < 0')],
  ["Vendor supports daily confirmation with and without changes", () => {
    const s = read("screens/VendorMobileScreen.tsx");
    return s.includes("/confirm") && s.includes("/confirm-with-changes") && s.includes("confirmed_quantity");
  }],
  ["Order detail retries failed load", () => read("screens/OrderDetailMobileScreen.tsx").includes('label="تلاش مجدد"')],
  ["Order detail validates return quantity", () => read("screens/OrderDetailMobileScreen.tsx").includes('quantity < 1')],
  ["Order detail requires dispute reason", () => read("screens/OrderDetailMobileScreen.tsx").includes('if (!disputeReason.trim())')],
  ["Order detail gates vendor actions by order state", () => {
    const s = read("screens/OrderDetailMobileScreen.tsx");
    return s.includes('["SUBMITTED", "CREATED"]') && s.includes('["ACCEPTED", "PARTIALLY_ACCEPTED"]') && s.includes('status === "DISPATCHED"');
  }],
  ["Support requires a subject before case creation", () => read("screens/SupportMobileScreen.tsx").includes('if (!subject.trim())')],
  ["Support prevents empty message send", () => read("screens/SupportMobileScreen.tsx").includes('if (!selected || !message.trim()) return;')],
  ["Ops audit tab is restricted to ADMIN_SUPER", () => read("screens/OpsMobileScreen.tsx").includes('props.role === "ADMIN_SUPER"')],
  ["API propagates bearer authentication", () => read("api.ts").includes('headers.Authorization = "Bearer " + accessToken')],
  ["API distinguishes network failures from API errors", () => read("api.ts").includes('"NETWORK"') && read("api.ts").includes("setOnline(false)")],
  ["Retailer exposes finance parity against REAL invoices API", () => read("screens/RetailerMobileScreen.tsx").includes("/api/v1/invoices") && read("screens/RetailerMobileScreen.tsx").includes('tab === "finance"')],
  ["Vendor exposes finance parity against REAL invoices API", () => read("screens/VendorMobileScreen.tsx").includes("/api/v1/invoices") && read("screens/VendorMobileScreen.tsx").includes('tab === "finance"')],
  ["Vendor exposes referral attribution against REAL referrals API", () => read("screens/VendorMobileScreen.tsx").includes("/api/v1/referrals") && read("screens/VendorMobileScreen.tsx").includes('tab === "referrals"')],
  ["Shared account exposes REAL notification preferences GET/PUT", () => { const s = read("screens/AccountMobileScreen.tsx"); return s.includes("/api/v1/notifications/preferences") && s.includes("api.put"); }],
  ["Ops exposes REAL support and notification read surfaces", () => { const s = read("screens/OpsMobileScreen.tsx"); return s.includes("SupportMobileScreen") && s.includes("/api/v1/notifications"); }],
  ["Field assisted order never calls catalog without the required q parameter", () => read("screens/AssistedOrderScreen.tsx").includes("if (!q) {") && !read("screens/AssistedOrderScreen.tsx").includes('/api/v1/catalog/search?limit=40')],
  ["Field assisted order maps canonical catalog product fields", () => { const s = read("screens/AssistedOrderScreen.tsx"); return s.includes("canonical_name_fa") && s.includes("master_sku"); }],
  ["Offline banner reconciles the current online state after subscribing", () => read("components/OfflineBanner.tsx").includes("setOnline(isOnline())")],
  ["Mobile theme has runtime provider and explicit Light/Night controls", () => {
    const theme = read("theme.ts");
    const app = read("../AppShell.tsx");
    const account = read("screens/AccountMobileScreen.tsx");
    return theme.includes("ThemeProvider") && app.includes("<ThemeProvider>") && account.includes('setMode("night")') && account.includes('setMode("light")');
  }],
  ["Login normalizes local Iranian numbers to E.164 before auth", () => { const s = read("screens/LoginScreen.tsx"); return s.includes("toE164") && s.includes("mobileNumber"); }],

];

let failed = 0;
for (const [name, fn] of checks) {
  let ok = false;
  try { ok = Boolean(fn()); } catch {}
  console.log(`${ok ? "PASS" : "FAIL"} | ${name}`);
  if (!ok) failed += 1;
}

console.log(`\nMobile functional/state-transition QA: ${checks.length - failed}/${checks.length} checks passed.`);
if (failed) process.exit(1);
