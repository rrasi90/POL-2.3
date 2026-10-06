// QA-only build: canonical retailer variant + x86_64 ABI for emulator runtime QA.
// Mirrors build_android_variant.mjs but overrides reactNativeArchitectures and
// writes a QA-suffixed artifact. NOT a release candidate.
import { spawnSync } from "node:child_process";
import { readFileSync, writeFileSync, copyFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const appDir = process.cwd();
const variant = process.argv[2] || "retailer";
const variantEntry = variant === "vendor" ? "index.vendor.ts" : "index.retailer.ts";
const entryFile = resolve(appDir, "index.ts");
const entrySource = readFileSync(entryFile, "utf8");
const variantSource = readFileSync(resolve(appDir, variantEntry), "utf8");

function run(cmd, args, cwd = appDir) {
  const result = spawnSync(cmd, args, { cwd, env: process.env, stdio: "inherit", shell: process.platform === "win32" });
  if (result.status !== 0) throw new Error(`Command failed: ${cmd} ${args.join(" ")}`);
}

try {
  writeFileSync(entryFile, variantSource, "utf8");
  run("npx", ["expo", "prebuild", "--clean", "--platform", "android"]);
  const androidDir = resolve(appDir, "android");
  run(process.platform === "win32" ? "gradlew.bat" : "./gradlew",
    ["assembleRelease", "-PreactNativeArchitectures=arm64-v8a,x86_64"], androidDir);
  const source = resolve(androidDir, "app/build/outputs/apk/release/app-release.apk");
  if (!existsSync(source)) throw new Error("QA APK was not generated");
  const output = resolve(appDir, "dist", variant);
  mkdirSync(output, { recursive: true });
  const name = variant === "retailer" ? "POL-Market-qa-x86_64.apk" : "POL-Vendor-qa-x86_64.apk";
  copyFileSync(source, resolve(output, name));
  console.log("QA APK:", resolve(output, name));
} finally {
  writeFileSync(entryFile, entrySource, "utf8");
}
