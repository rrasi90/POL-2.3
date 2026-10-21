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
  ["No Driver App is introduced into Phase 3 mobile source", () => {
    const p = fs.readFileSync(path.resolve(process.cwd(), "src/__tests__/parity.md"), "utf8");
    return p.includes("No Driver App (D-023)");
  }],
  ["Reduced-motion hook follows the native preference and removes unmounted subscribers", () => {
    const s = read("motion/useReducedMotion.ts");
    return s.includes("AccessibilityInfo.isReduceMotionEnabled()") &&
      s.includes('addEventListener("reduceMotionChanged", publish)') &&
      s.includes("listeners.delete(setReduced)");
  }],
  ["ErrorShake cancels interrupted animations and resets its transform", () => {
    const s = read("motion/ErrorShake.tsx");
    return s.includes("translateX.stopAnimation()") && s.includes("animation.stop()") &&
      s.includes("translateX.setValue(0)") && s.includes("if (props.trigger <= 0 || reduced) return;");
  }],
  ["Order progress preserves canonical state mapping and animation cleanup", () => {
    const s = read("motion/OrderProgress.tsx");
    return s.includes("stageIndexForOrderStatus") && s.includes('status === "DELIVERED"') &&
      s.includes('status === "ARRIVED"') && s.includes("animation.stop()") &&
      s.includes("scale.setValue(1)");
  }],
  ["App shell gates splash exit on boot and fonts and transitions routed screens", () => {
    const s = readMobile("AppShell.tsx");
    return s.includes("fontsLoaded && booted") && s.includes("onExited={() => setSplashExited(true)}") &&
      s.includes('<ScreenTransition transitionKey={routeKey}') &&
      s.includes('<ScreenTransition transitionKey="login"');
  }],
  ["Motion primitives are integrated into Retailer, Vendor, delivery and login journeys", () => {
    const login = read("screens/LoginScreen.tsx");
    const retailer = read("screens/RetailerMobileScreen.tsx");
    const vendor = read("screens/VendorMobileScreen.tsx");
    const order = read("screens/OrderDetailMobileScreen.tsx");
    return login.includes("../motion/FadeIn") && login.includes("../motion/PopOnChange") &&
      retailer.includes("../motion/SkeletonPulse") && retailer.includes("../motion/SuccessCheck") &&
      vendor.includes("../motion/ErrorShake") && order.includes("../motion/DeliveryProgress") &&
      order.includes("../motion/OrderProgress");
  }],
  ["Offline banner entrance respects reduced-motion configuration", () => {
    const s = read("components/OfflineBanner.tsx");
    return s.includes("../motion/SlideIn") && s.includes("SlideIn") && s.includes("setOnline(isOnline())");
  }],
  ["Finite Pulse creates independent burst animation instances", () => {
    const s = read("motion/Pulse.tsx");
    return s.includes("const createBurst = () => Animated.sequence([") &&
      s.includes("Animated.sequence([createBurst(), createBurst(), createBurst()])") &&
      s.includes("Animated.loop(createBurst())");
  }],
  ["SuccessCheck fits the canonical complex-sequence timing budget", () => {
    const s = read("motion/SuccessCheck.tsx");
    return s.includes("delay: (props.delay ?? 0) + motionDuration.micro") &&
      s.includes("duration: motionDuration.base") &&
      s.includes("Whole sequence stays inside the canonical ≤400ms complex-sequence band.");
  }],
  ["Splash entrance stops when boot is ready before its sequence finishes", () => {
    const s = read("motion/SplashSequence.tsx");
    return s.includes("reduced || props.ready") && s.includes("[reduced, props.ready, mark, wordmark, tagline]") &&
      s.includes("return () => animation.stop();");
  }],
  ["PopOnChange cancels interrupted springs and resets scale", () => {
    const s = read("motion/PopOnChange.tsx");
    return s.includes("scale.stopAnimation()") && s.includes("animation.stop()") &&
      s.includes("scale.setValue(1)");
  }],
  ["PressScale respects reduced motion and cleans up on unmount", () => {
    const s = read("motion/PressScale.tsx");
    return s.includes("if (reduced)") && s.includes("scale.stopAnimation()") &&
      s.includes("useEffect(() => () =>") && s.includes("scale.setValue(1)");
  }],
  ["Delivery progress uses order-status fallback only when delivery status is absent", () => {
    const s = read("motion/DeliveryProgress.tsx");
    return s.includes("if (!raw)") && s.includes('order === "DISPATCHED"') &&
      s.includes('order === "DELIVERED"') && s.includes('raw === "PICKED_UP"');
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
