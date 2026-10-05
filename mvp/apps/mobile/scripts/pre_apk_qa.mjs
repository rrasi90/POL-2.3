import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRequire } from "node:module";

const appDir = resolve(process.cwd());
const requireFromApp = createRequire(resolve(appDir, "package.json"));

function assert(condition, message) {
  if (!condition) throw new Error("[PRE-APK FAIL] " + message);
  console.log("[PRE-APK PASS]", message);
}

function gitBlobSha(file) {
  const bytes = readFileSync(file);
  const header = Buffer.from("blob " + bytes.length + "\0");
  return createHash("sha1").update(Buffer.concat([header, bytes])).digest("hex");
}

function pngDimensions(file) {
  const bytes = readFileSync(file);
  assert(bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), file + " is a valid PNG");
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20), colorType: bytes[25] };
}

const variant = (process.argv[2] || process.env.POL_APP_VARIANT || "retailer").toLowerCase();
assert(["retailer", "vendor"].includes(variant), "Android variant is retailer or vendor");
const releaseGate = process.env.POL_RELEASE !== "0";
const dataMode = (process.env.EXPO_PUBLIC_DATA_MODE || "live").toLowerCase();
const apiBaseUrl = (process.env.EXPO_PUBLIC_API_BASE_URL || "").trim();

assert(dataMode === "live" || dataMode === "mock", "data mode is constrained to live/mock");
if (releaseGate) {
  assert(dataMode !== "mock", "release build cannot use mock data mode");
  assert(apiBaseUrl.length > 0, "release build requires EXPO_PUBLIC_API_BASE_URL");
  const parsedApi = new URL(apiBaseUrl);
  assert(parsedApi.protocol === "https:", "release build API base URL must use HTTPS");
  assert(!["localhost", "127.0.0.1", "10.0.2.2"].includes(parsedApi.hostname), "release build API base URL cannot target local/emulator hosts");
}

const originalVariant = process.env.POL_APP_VARIANT;
process.env.POL_APP_VARIANT = variant;
const configPath = requireFromApp.resolve("./app.config.js");
delete requireFromApp.cache[configPath];
const config = requireFromApp("./app.config.js");
if (originalVariant === undefined) delete process.env.POL_APP_VARIANT;
else process.env.POL_APP_VARIANT = originalVariant;

const expected = variant === "vendor"
  ? {
      name: "پل بنکدار",
      slug: "pol-vendor",
      packageId: "ir.pol.vendor",
      icon: "./assets/vendor-logo.png",
      source: "src/screens/VendorMobileScreen.tsx",
      loginMessage: "این حساب برای اپلیکیشن بنکدار مجاز نیست.",
    }
  : {
      name: "پل بازار",
      slug: "pol-market",
      packageId: "ir.pol.market",
      icon: "./assets/icon.png",
      source: "src/screens/RetailerMobileScreen.tsx",
      loginMessage: "این حساب برای این اپلیکیشن مجاز نیست.",
    };

assert(config.name === expected.name, variant + " app name is canonical");
assert(config.slug === expected.slug, variant + " Expo slug is canonical");
assert(config.android?.package === expected.packageId, variant + " Android package is canonical");
assert(config.icon === expected.icon, variant + " launcher icon is canonical");

const iconPath = resolve(appDir, expected.icon);
const iconInfo = pngDimensions(iconPath);
assert(iconInfo.width > 0 && iconInfo.height > 0, variant + " launcher icon has readable dimensions");
if (variant === "vendor") {
  assert(gitBlobSha(iconPath) === "d6b0bc5c4ea5aa66e0feb739bfc176589d89a182", "vendor logo is byte-identical to the canonical Vendor brand asset");
  assert(iconInfo.width >= 512 && iconInfo.height >= 512, "vendor logo asset has sufficient raster resolution");
  assert(Math.abs(iconInfo.width - iconInfo.height) <= Math.max(iconInfo.width, iconInfo.height) * 0.05, "vendor logo asset is near-square for launcher/splash use");
  assert(config.android?.adaptiveIcon?.foregroundImage === "./assets/vendor-logo.png", "vendor adaptive foreground uses canonical vendor brand asset");
  assert(config.android?.splash?.image === "./assets/vendor-logo.png", "vendor Android splash uses canonical vendor brand asset");
} else {
  assert(config.android?.package === "ir.pol.market", "retailer package ID is explicit");
}

for (const p of [
  "assets/icon.png",
  "assets/android-icon-foreground.png",
  "assets/android-icon-background.png",
  "assets/android-icon-monochrome.png",
  "assets/favicon.png",
  "assets/fonts/Vazirmatn-Regular.ttf",
  "assets/fonts/Vazirmatn-SemiBold.ttf",
  "assets/fonts/Vazirmatn-Bold.ttf",
]) {
  assert(existsSync(resolve(appDir, p)), p + " exists");
  if (p.endsWith(".png")) pngDimensions(resolve(appDir, p));
}

const apiSource = readFileSync(resolve(appDir, "src/api.ts"), "utf8");
assert(!/sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN .*PRIVATE KEY-----/.test(apiSource), "mobile API source contains no obvious hard-coded secrets");
assert(apiSource.includes("EXPO_PUBLIC_API_BASE_URL"), "API base URL remains environment-configurable");
assert(apiSource.includes("/api/v1/"), "mobile API remains on canonical v1 routes");
if (releaseGate) console.log("[PRE-APK PASS] release build API endpoint is HTTPS and non-local");

const source = readFileSync(resolve(appDir, expected.source), "utf8");
const loginSource = readFileSync(resolve(appDir, "src/screens/LoginScreen.tsx"), "utf8");
assert(loginSource.includes("allowedRoles"), "login enforces an app-level allowed-role boundary");
assert(loginSource.includes(expected.loginMessage) || (variant === "retailer" && loginSource.includes("پل بازار")), variant + " login copy identifies the correct app boundary");

const supportSource = readFileSync(resolve(appDir, "src/screens/SupportMobileScreen.tsx"), "utf8");
assert(source.includes("SupportMobileScreen"), variant + " includes support surface");
assert(supportSource.includes("/api/v1/support/cases") && supportSource.includes("/messages"), "support surface uses canonical case/message routes");

if (variant === "vendor") {
  const app = readFileSync(resolve(appDir, "AppVendor.tsx"), "utf8");
  assert(app.includes('allowedRoles={["VENDOR_OWNER", "VENDOR_STAFF"]}'), "vendor entrypoint is restricted to vendor roles");
  assert(source.includes("/api/v1/orders"), "vendor app uses canonical orders route");
  assert(source.includes("/api/v1/catalog/vendors/products"), "vendor app uses canonical vendor catalog route");
  assert(source.includes("/api/v1/inventory/daily/"), "vendor app uses canonical daily inventory route");
  assert(source.includes("/api/v1/invoices"), "vendor app uses canonical invoice route");
  assert(source.includes("/api/v1/vendors/settlements"), "vendor app uses canonical settlement route");
  assert(source.includes("/api/v1/vendors/customers"), "vendor app uses canonical customer route");
  assert(source.includes("/api/v1/vendors/staff"), "vendor app uses canonical staff route");
  assert(source.includes("/api/v1/storefront/vendors"), "vendor app includes canonical storefront route");
  assert(source.includes("/api/v1/catalog/barcode/lookup"), "vendor app includes canonical barcode lookup route");
  assert(source.includes("/api/v1/vendors/inventory/continuous-scan"), "vendor app includes canonical continuous-scan route");
  assert(source.includes("/api/v1/vendors/inventory/publish"), "vendor app includes canonical inventory publish route");
  assert(source.includes("formatTehranDateTime") && source.includes("todayTehranIso"), "vendor app uses Tehran-localized date/time formatting");
  assert(source.includes("toAsciiDigits"), "vendor app normalizes Persian/Arabic numeric input for API boundaries");
} else {
  const app = readFileSync(resolve(appDir, "AppRetailer.tsx"), "utf8");
  assert(app.includes('allowedRoles={["RETAILER_OWNER", "RETAILER_STAFF"]}'), "retailer entrypoint is restricted to retailer roles");
  assert(source.includes("serverBasketId") && source.includes("allocation") && source.includes("Idempotency-Key"), "retailer checkout preserves basket/allocation/idempotency gates");
  assert(source.includes("/api/v1/catalog/search"), "retailer app uses canonical catalog search route");
  assert(source.includes("/api/v1/baskets"), "retailer app uses canonical basket routes");
  assert(source.includes("/api/v1/orders"), "retailer app uses canonical orders route");
  assert(source.includes("/api/v1/invoices"), "retailer app uses canonical invoice route");
}

const paritySource = readFileSync(resolve(appDir, "src/__tests__/parity.md"), "utf8");
assert(paritySource.includes("CAMERA RUNTIME GAP") && paritySource.includes("match-barcode"), "barcode camera boundary is explicitly tracked in parity");

const buildScript = readFileSync(resolve(appDir, "scripts/build_android_variant.mjs"), "utf8");
assert(buildScript.includes('variant === "vendor" ? "index.vendor.ts"'), "build script selects the dedicated Vendor entrypoint");
assert(buildScript.includes('variant === "vendor" ? "index.vendor.ts" : "index.retailer.ts"'), "build script contains both deterministic entrypoints");
assert(buildScript.includes("assembleRelease"), "build script uses native Gradle release build");
assert(buildScript.includes("finally"), "build script restores the default entrypoint after the build");

const mobilePackage = JSON.parse(readFileSync(resolve(appDir, "package.json"), "utf8"));
const workspaceLock = JSON.parse(readFileSync(resolve(appDir, "..", "..", "package-lock.json"), "utf8"));
const lockedMobile = workspaceLock.packages?.["apps/mobile"]?.dependencies || {};
const lockedSecureStore = workspaceLock.packages?.["node_modules/expo-secure-store"];
assert(mobilePackage.dependencies?.["expo-secure-store"] === "~57.0.4", "expo-secure-store is aligned to Expo SDK 57");
assert(lockedMobile["expo-secure-store"] === "~57.0.4", "package-lock mobile dependency is aligned to Expo SDK 57");
assert(lockedSecureStore?.version === "57.0.4", "package-lock resolves expo-secure-store 57.0.4");

const mockTransport = readFileSync(resolve(appDir, "src/mock/mockTransport.ts"), "utf8");
assert(mockTransport.includes("mockRequest") && mockTransport.includes("resetMockState"), "mock transport is present and resettable");

function runQa(label, args) {
  const result = spawnSync(process.execPath, args, { cwd: appDir, env: process.env, stdio: "inherit" });
  assert(result.status === 0, label + " completed successfully");
}

runQa("mobile regression QA", ["scripts/mobile_regression_qa.mjs"]);
if (variant === "vendor") {
  runQa("Vendor mock transport QA", ["--experimental-strip-types", "scripts/mock_transport_qa.ts"]);
}

console.log("[PRE-APK] " + variant + " app passed source/config, regression, and variant-specific mock gates immediately before native Android build.");
