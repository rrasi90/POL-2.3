import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRequire } from "node:module";

const appDir = resolve(process.cwd());
const requireFromApp = createRequire(resolve(appDir, "package.json"));

function assert(condition, message) {
  if (!condition) throw new Error("[PRE-APK FAIL] " + message);
  console.log("[PRE-APK PASS]", message);
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
assert(config.splash?.image === "./assets/vendor-logo.png", "vendor splash uses canonical vendor brand asset");
assert(config.android?.adaptiveIcon?.foregroundImage === "./assets/vendor-logo.png", "vendor adaptive foreground uses canonical vendor brand asset");

const vendorLogo = resolve(appDir, "assets/vendor-logo.png");
const logoInfo = pngDimensions(vendorLogo);
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

const apiSource = readFileSync(resolve(appDir, "src/api.ts"), "utf8");
assert(!/sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN .*PRIVATE KEY-----/.test(apiSource), "mobile API source contains no obvious hard-coded secrets");
assert(apiSource.includes("EXPO_PUBLIC_API_BASE_URL"), "API base URL remains environment-configurable");
assert(apiSource.includes("/api/v1/"), "mobile API remains on canonical v1 routes");

const vendorSource = readFileSync(resolve(appDir, "src/screens/VendorMobileScreen.tsx"), "utf8");
assert(vendorSource.includes("SupportMobileScreen"), "vendor app includes support surface");
assert(vendorSource.includes("/api/v1/orders"), "vendor app uses canonical orders route");
assert(vendorSource.includes("/api/v1/catalog/vendors/products"), "vendor app uses canonical vendor catalog route");
assert(vendorSource.includes("/api/v1/inventory/daily/"), "vendor app uses canonical daily inventory route");
assert(vendorSource.includes("/api/v1/invoices"), "vendor app uses canonical invoice route");
assert(vendorSource.includes("/api/v1/vendors/settlements"), "vendor app uses canonical settlement route");
assert(vendorSource.includes("/api/v1/vendors/customers"), "vendor app uses canonical customer route");
assert(vendorSource.includes("/api/v1/vendors/staff"), "vendor app uses canonical staff route");

const buildScript = readFileSync(resolve(appDir, "scripts/build_android_variant.mjs"), "utf8");
assert(buildScript.includes('variant === "vendor" ? "index.vendor.ts"'), "APK build script selects dedicated vendor entrypoint");
assert(buildScript.includes("assembleRelease"), "APK build script uses release Gradle assemble");
assert(buildScript.includes("finally"), "APK build script restores the default entrypoint");

const regression = readFileSync(resolve(appDir, "scripts/mobile_regression_qa.mjs"), "utf8");
assert(regression.includes('tab === "support"'), "regression QA covers vendor support tab");
assert(regression.includes("new_physical_quantity"), "regression QA covers inventory mutation field");

console.log("[PRE-APK] Vendor app is at the final source/config gate immediately before APK build.");
