import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, copyFileSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const variant = (process.argv[2] || "retailer").toLowerCase();
const artifact = (process.argv[3] || "apk").toLowerCase();
if (!["retailer", "vendor"].includes(variant) || !["apk", "aab"].includes(artifact)) {
  throw new Error("Usage: node scripts/build_android_variant.mjs retailer|vendor [apk|aab]");
}

const appDir = resolve(".");
const androidDir = resolve(appDir, "android");
const entryFile = resolve(appDir, "index.ts");
const entrySource = readFileSync(entryFile, "utf8");
const variantEntry = variant === "vendor" ? "index.vendor.ts" : "index.retailer.ts";
const variantSource = readFileSync(resolve(appDir, variantEntry), "utf8");

const env = {
  ...process.env,
  POL_APP_VARIANT: variant,
};

function run(command, args, cwd = appDir) {
  const result = spawnSync(command, args, {
    cwd,
    env,
    stdio: "inherit",
    shell: process.platform === "win32",
  });
  if (result.status !== 0) {
    throw new Error(`Command failed: ${command} ${args.join(" ")}`);
  }
}

try {
  if (variant === "vendor") {
    run("node", ["scripts/pre_apk_qa.mjs"]);
  }

  // Metro sees only the selected entrypoint, so the other product's workspace
  // is not pulled into this production bundle.
  writeFileSync(entryFile, variantSource, "utf8");

  run("npx", ["expo", "prebuild", "--clean", "--platform", "android"]);

  if (!existsSync(resolve(androidDir, "gradlew"))) {
    throw new Error("Expo prebuild did not generate android/gradlew");
  }

  run(
    process.platform === "win32" ? "gradlew.bat" : "./gradlew",
    [artifact === "aab" ? "bundleRelease" : "assembleRelease"],
    androidDir,
  );

  const extension = artifact === "aab" ? "aab" : "apk";
  const source = resolve(
    androidDir,
    "app/build/outputs",
    artifact === "aab" ? "bundle/release/app-release.aab" : "apk/release/app-release.apk",
  );
  if (!existsSync(source)) throw new Error(`Release ${extension.toUpperCase()} was not generated`);

  const output = resolve(appDir, "dist", variant);
  mkdirSync(output, { recursive: true });
  const productName = variant === "retailer" ? "POL-Market" : "POL-Vendor";
  const target = resolve(output, `${productName}.${extension}`);
  copyFileSync(source, target);
  console.log(`${extension.toUpperCase()}:`, target);
} finally {
  writeFileSync(entryFile, entrySource, "utf8");
}
