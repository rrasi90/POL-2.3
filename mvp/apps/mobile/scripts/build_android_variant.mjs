import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, copyFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

const variant = (process.argv[2] || "retailer").toLowerCase();
if (!["retailer", "vendor"].includes(variant)) {
  throw new Error("Usage: node scripts/build_android_variant.mjs retailer|vendor");
}

const appDir = resolve(".");
const androidDir = resolve(appDir, "android");
const env = {
  ...process.env,
  POL_APP_VARIANT: variant,
  EXPO_PUBLIC_APP_VARIANT: variant,
};

function run(command, args, cwd = appDir) {
  const result = spawnSync(command, args, { cwd, env, stdio: "inherit", shell: process.platform === "win32" });
  if (result.status !== 0) process.exit(result.status ?? 1);
}

run("npx", ["expo", "prebuild", "--clean", "--platform", "android"]);

if (!existsSync(resolve(androidDir, "gradlew"))) {
  throw new Error("Expo prebuild did not generate android/gradlew");
}

run(process.platform === "win32" ? "gradlew.bat" : "./gradlew", ["assembleRelease"], androidDir);

const apk = resolve(androidDir, "app/build/outputs/apk/release/app-release.apk");
if (!existsSync(apk)) throw new Error("Release APK was not generated");

const output = resolve(appDir, "dist", variant);
mkdirSync(output, { recursive: true });
const target = resolve(output, variant === "retailer" ? "POL-Market.apk" : "POL-Vendor.apk");
copyFileSync(apk, target);
console.log("APK:", target);
