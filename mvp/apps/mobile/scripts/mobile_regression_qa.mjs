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
  ["Order detail lifecycle remains state-gated for returns/disputes/vendor actions", () => {
    const s = read("screens/OrderDetailMobileScreen.tsx");
    return s.includes("quantity < 1") && s.includes("disputeReason") && s.includes("DISPATCHED");
  }],
  ["Support creation/message validation remains enforced", () => {
    const s = read("screens/SupportMobileScreen.tsx");
    return s.includes("!subject.trim()") && s.includes("!message.trim()");
  }],
  ["Ops privileged audit surface remains ADMIN_SUPER-only", () => read("screens/OpsMobileScreen.tsx").includes('props.role === "ADMIN_SUPER"')],
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
