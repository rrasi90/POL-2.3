import { createHash } from "node:crypto";
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
  assert(bytes.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10])), file + " is a valid PNG");
  return {
    width: bytes.readUInt32BE(16),
    height: bytes.readUInt32BE(20),
    colorType: bytes[25],
  };
}

const originalVariant = process.env.POL_APP_VARIANT;
const releaseGate = process.env.POL_RELEASE === "1";
const dataMode = (process.env.EXPO_PUBLIC_DATA_MODE || "live").toLowerCase();
const apiBaseUrl = (process.env.EXPO_PUBLIC_API_BASE_URL || "").trim();
if (releaseGate) {
  assert(dataMode !== "mock", "release build cannot use mock data mode");
}
if (releaseGate) {
  assert(apiBaseUrl.length > 0, "release build requires EXPO_PUBLIC_API_BASE_URL; emulator fallback is not allowed");
  const parsedApi = new URL(apiBaseUrl);
  assert(parsedApi.protocol === "https:", "release build API base URL must use HTTPS");
  assert(!["localhost", "127.0.0.1", "10.0.2.2"].includes(parsedApi.hostname), "release build API base URL cannot target local/emulator hosts");
}
process.env.POL_APP_VARIANT = "vendor";
const configPath = requireFromApp.resolve("./app.config.js");
delete requireFromApp.cache[configPath];
const config = requireFromApp("./app.config.js");
if (originalVariant === undefined) delete process.env.POL_APP_VARIANT;
else process.env.POL_APP_VARIANT = originalVariant;

assert(config.name === "پل بنکدار", "vendor app name is canonical");
assert(config.slug === "pol-vendor", "vendor Expo slug is canonical");
assert(config.android?.package === "ir.pol.vendor", "vendor Android package is canonical");
assert(config.icon === "./assets/vendor-logo.png", "vendor launcher icon uses canonical vendor brand asset");
assert(config.android?.adaptiveIcon?.foregroundImage === "./assets/vendor-logo.png", "vendor adaptive foreground uses canonical vendor brand asset");
assert(config.android?.splash?.image === "./assets/vendor-logo.png", "vendor Android splash uses canonical vendor brand asset");

const vendorLogo = resolve(appDir, "assets/vendor-logo.png");
const logoInfo = pngDimensions(vendorLogo);
assert(gitBlobSha(vendorLogo) === "d6b0bc5c4ea5aa66e0feb739bfc176589d89a182", "vendor logo is byte-identical to the canonical Vendor brand asset");
assert(logoInfo.width >= 512 && logoInfo.height >= 512, "vendor logo asset has sufficient raster resolution");
assert(Math.abs(logoInfo.width - logoInfo.height) <= Math.max(logoInfo.width, logoInfo.height) * 0.05, "vendor logo asset is near-square for launcher/splash use");

for (const p of [
  "assets/icon.png",
  "assets/android-icon-foreground.png",
  "assets/android-icon-background.png",
  "assets/android-icon-monochrome.png",
  "assets/favicon.png",
]) {
  const absolute = resolve(appDir, p);
  assert(existsSync(absolute), p + " exists");
  const info = pngDimensions(absolute);
  assert(info.width > 0 && info.height > 0, p + " has readable PNG dimensions");
}

for (const p of [
  "assets/fonts/Vazirmatn-Regular.ttf",
  "assets/fonts/Vazirmatn-SemiBold.ttf",
  "assets/fonts/Vazirmatn-Bold.ttf",
]) {
  assert(existsSync(resolve(appDir, p)), p + " exists");
}

const apiSource = readFileSync(resolve(appDir, "src/api.ts"), "utf8");
assert(!/sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN .*PRIVATE KEY-----/.test(apiSource), "mobile API source contains no obvious hard-coded secrets");
assert(apiSource.includes("EXPO_PUBLIC_API_BASE_URL"), "API base URL remains environment-configurable");
if (releaseGate) console.log("[PRE-APK PASS] release build API endpoint is HTTPS and non-local");
assert(apiSource.includes("/api/v1/"), "mobile API remains on canonical v1 routes");

const vendorSource = readFileSync(resolve(appDir, "src/screens/VendorMobileScreen.tsx"), "utf8");
const supportSource = readFileSync(resolve(appDir, "src/screens/SupportMobileScreen.tsx"), "utf8");
assert(vendorSource.includes("SupportMobileScreen") && vendorSource.includes("role={props.role}"), "vendor app includes support surface");
assert(supportSource.includes("/api/v1/support/cases") && supportSource.includes("/messages"), "support surface uses canonical case/message routes");
assert(vendorSource.includes("/api/v1/orders"), "vendor app uses canonical orders route");
assert(vendorSource.includes("/api/v1/catalog/vendors/products"), "vendor app uses canonical vendor catalog route");
assert(vendorSource.includes("/api/v1/inventory/daily/"), "vendor app uses canonical daily inventory route");
assert(vendorSource.includes("/api/v1/invoices"), "vendor app uses canonical invoice route");
assert(vendorSource.includes("/api/v1/vendors/settlements"), "vendor app uses canonical settlement route");
assert(vendorSource.includes("/api/v1/vendors/customers"), "vendor app uses canonical customer route");
assert(vendorSource.includes("/api/v1/vendors/staff"), "vendor app uses canonical staff route");
assert(vendorSource.includes("/api/v1/storefront/vendors"), "vendor app includes canonical storefront route");
assert(vendorSource.includes("/api/v1/catalog/barcode/lookup"), "vendor app includes canonical barcode lookup route");
assert(vendorSource.includes("/api/v1/products/match-barcode"), "vendor app includes canonical barcode match route");
assert(vendorSource.includes("/api/v1/vendors/inventory/continuous-scan"), "vendor app includes canonical continuous-scan route");
assert(vendorSource.includes("/api/v1/vendors/inventory/publish"), "vendor app includes canonical inventory publish route");
assert(vendorSource.includes("formatTehranDateTime") && vendorSource.includes("todayTehranIso"), "vendor app uses Tehran-localized date/time formatting");
assert(vendorSource.includes("toAsciiDigits"), "vendor app normalizes Persian/Arabic numeric input for API boundaries");

const buildScript = readFileSync(resolve(appDir, "scripts/build_android_variant.mjs"), "utf8");
assert(buildScript.includes('variant === "vendor" ? "index.vendor.ts"'), "APK build script selects dedicated vendor entrypoint");
assert(buildScript.includes("assembleRelease"), "APK build script uses release Gradle assemble");
assert(buildScript.includes("finally"), "APK build script restores the default entrypoint");

const mockTransport = readFileSync(resolve(appDir, "src/mock/mockTransport.ts"), "utf8");
const mockQa = readFileSync(resolve(appDir, "scripts/mock_transport_qa.ts"), "utf8");
assert(mockTransport.includes("mockRequest") && mockTransport.includes("resetMockState"), "mock transport is present and resettable");
assert(mockQa.includes("Vendor Staff cannot accept orders") && mockQa.includes("Vendor Staff cannot manage prices"), "mock QA covers Vendor Staff RBAC");
assert(dataMode === "live" || dataMode === "mock", "data mode is constrained to live/mock");

const regression = readFileSync(resolve(appDir, "scripts/mobile_regression_qa.mjs"), "utf8");
assert(regression.includes('tab === "support"'), "regression QA covers vendor support tab");
assert(regression.includes("new_physical_quantity"), "regression QA covers inventory mutation field");

console.log("[PRE-APK] Vendor app is at the final source/config gate immediately before APK build.");
