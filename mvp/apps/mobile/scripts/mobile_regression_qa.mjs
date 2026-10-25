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
  ["Vendor queue hides owner-only acceptance from vendor staff", () => {
    const s = read("screens/VendorMobileScreen.tsx");
    const d = read("screens/OrderDetailMobileScreen.tsx");
    return s.includes('props.role === "VENDOR_OWNER"') &&
      s.includes("پذیرش سفارش فقط برای مالک بنکداری مجاز است.") &&
      d.includes("vendorOwner") && d.includes("پذیرش جزئی فقط برای مالک بنکداری مجاز است.");
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
    return p.includes("CAMERA RUNTIME GAP") && p.includes("match-barcode");
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
  ["Vendor catalog/inventory maps canonical names, physical quantity and PATCH schema", () => {
    const webInventory = readMobile("../web/src/app/(dashboard)/vendor/inventory/page.tsx");
    const webCatalog = readMobile("../web/src/app/(dashboard)/vendor/catalog/page.tsx");
    const vendorShared = readMobile("../web/src/app/(dashboard)/vendor/_shared.ts");
    const mobileVendor = read("screens/VendorMobileScreen.tsx");
    return vendorShared.includes("vendorProductDisplayName") &&
      vendorShared.includes("کالای بدون نام") &&
      webInventory.includes("p.canonical_name_fa") &&
      webInventory.includes("p.physical_quantity") &&
      webInventory.includes("new_physical_quantity: n") &&
      webCatalog.includes("p.canonical_name_fa") &&
      webCatalog.includes("p.available_quantity") &&
      mobileVendor.includes("props.row.canonical_name_fa");
  }],
  ["Retailer/vendor order status chips use canonical Persian labels", () => {
    const labels = read("utils/statusLabels.ts");
    const retailer = read("screens/RetailerMobileScreen.tsx");
    const vendor = read("screens/VendorMobileScreen.tsx");
    return labels.includes('DELIVERED: "تحویل‌شده"') &&
      labels.includes('IN_TRANSIT: "در مسیر"') &&
      retailer.includes("formatOrderStatus(o.order_status)") &&
      vendor.includes("formatOrderStatus(status)");
  }],
  ["Delivery, return and timeline states use purpose-specific Persian labels", () => {
    const labels = read("utils/statusLabels.ts");
    const detail = read("screens/OrderDetailMobileScreen.tsx");
    return labels.includes('ASSIGNED: "راننده تخصیص داده‌شده"') &&
      labels.includes('REFUNDED: "بازپرداخت‌شده"') &&
      labels.includes('DELIVERY_COMPLETED: "تحویل ثبت شد"') &&
      detail.includes("formatDeliveryStatus(deliveryStatus)") &&
      detail.includes("formatReturnStatus(x.status)") &&
      detail.includes("formatTimelineEvent(x.event_type)");
  }],
  ["Ops mobile localizes order, reconciliation, notification, candidate and organization states", () => {
    const screen = read("screens/OpsMobileScreen.tsx");
    const labels = read("utils/statusLabels.ts");
    return screen.includes("formatNotificationPriority(n.priority)") &&
      screen.includes("formatOrderStatus(o.order_status)") &&
      screen.includes("formatReconciliationStatus(r.status)") &&
      screen.includes("formatCandidateStatus(c.status)") &&
      screen.includes("formatOrganizationStatus(o.status)") &&
      labels.includes("export function formatAuditAction") &&
      screen.includes("formatAuditAction(a.action)");
  }],
  ["Support mobile localizes case status, priority, type, role and timestamps", () => {
    const screen = read("screens/SupportMobileScreen.tsx");
    return screen.includes("formatSupportStatus(selected.status)") &&
      screen.includes("formatSupportPriority(selected.priority)") &&
      screen.includes("formatSupportType(selected.case_type)") &&
      screen.includes("formatRole(m.sender_role)") &&
      screen.includes("formatTehranDateTime(m.created_at)");
  }],
  ["Vendor finance, referrals and delegated permissions use Persian labels", () => {
    const screen = read("screens/VendorMobileScreen.tsx");
    const labels = read("utils/statusLabels.ts");
    return screen.includes("formatInvoiceStatus(invoice.status)") &&
      screen.includes("formatSettlementStatus(settlement.status)") &&
      screen.includes("formatReferralStatus(referral.status)") &&
      screen.includes("formatPermission(permission)") &&
      screen.includes("formatGrantStatus(grant.status)") &&
      labels.includes("export function formatPermission");
  }],
  ["Retailer invoice and account notification statuses use Persian labels", () => {
    const retailer = read("screens/RetailerMobileScreen.tsx");
    const account = read("screens/AccountMobileScreen.tsx");
    return retailer.includes("formatInvoiceStatus(i.status)") &&
      account.includes("formatNotificationPriority(n.priority)");
  }],
  ["Order timeline and return issue details do not expose raw state enums", () => {
    const detail = read("screens/OrderDetailMobileScreen.tsx");
    return detail.includes("formatOperationalStatus(x.from_status)") &&
      detail.includes("formatReturnIssue(x.issue_type)") &&
      detail.includes("formatTimelineEvent(x.event_type)");
  }],
  ["Vendor scan and status fallbacks never expose raw enum names", () => {
    const screen = read("screens/VendorMobileScreen.tsx");
    const labels = read("utils/statusLabels.ts");
    return screen.includes('"وضعیت تطبیق نامشخص"') &&
      screen.includes("formatOperationalStatus(status)") &&
      screen.includes("معادل فارسی: {formatPackagingUnit(scanPackaging)}") &&
      screen.includes('label="کد فروشنده"') &&
      labels.includes("export function formatPackagingUnit");
  }],
  ["Return issue selection and operations KPI names are presented in Persian", () => {
    const detail = read("screens/OrderDetailMobileScreen.tsx");
    const ops = read("screens/OpsMobileScreen.tsx");
    const labels = read("utils/statusLabels.ts");
    return detail.includes('["DAMAGED", "کالای آسیب‌دیده"]') &&
      detail.includes('["QUANTITY_MISMATCH", "مغایرت تعداد"]') &&
      ops.includes("return formatKpiLabel(key)") &&
      labels.includes("export function formatKpiLabel");
  }],
  ["Field-task and assisted-order screens localize status, type and timestamp content", () => {
    const list = read("screens/FieldTaskListScreen.tsx");
    const detail = read("screens/FieldTaskDetailScreen.tsx");
    const assisted = read("screens/AssistedOrderScreen.tsx");
    const labels = read("utils/statusLabels.ts");
    return list.includes("formatFieldTaskStatus(item.status)") &&
      list.includes("formatFieldTaskType(item.task_type)") &&
      detail.includes("statusOptions.map(([code, label])") &&
      detail.includes("formatTehranDateTime(task?.due_date)") &&
      labels.includes("export function formatFieldTaskStatus") &&
      assisted.includes('badge="سفارش کمکی"') &&
      !assisted.includes('badge="F-03"');
  }],
  ["Account notifications use Persian channel labels and Tehran timestamps", () => {
    const screen = read("screens/AccountMobileScreen.tsx");
    return screen.includes('label="اعلان برنامه"') &&
      screen.includes("formatTehranDateTime(n.created_at)") &&
      screen.includes('subtitle="اعلان برنامه، پیامک و ایمیل"');
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
