import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { basename, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const variant = (process.argv[2] || "").toLowerCase();
const profile = (process.argv[3] || "").toLowerCase();
if (!["retailer", "vendor"].includes(variant) || !["arm64", "x86_64"].includes(profile)) {
  throw new Error("Usage: node scripts/write_qa_artifact_manifest.mjs retailer|vendor arm64|x86_64");
}

const product = variant === "retailer" ? "POL-Market" : "POL-Vendor";
const expectedPackageId = variant === "retailer" ? "ir.pol.market" : "ir.pol.vendor";
const artifactName = profile === "arm64" ? `${product}.apk` : `${product}-qa-x86_64.apk`;
const artifactPath = resolve("dist", variant, artifactName);
if (!existsSync(artifactPath)) throw new Error(`QA APK missing: ${artifactPath}`);

function run(command, args) {
  const result = spawnSync(command, args, { encoding: "utf8", maxBuffer: 16 * 1024 * 1024 });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed (exit ${result.status}): ${result.stderr || result.stdout}`);
  }
  return result.stdout || "";
}

const sdkRoot = process.env.ANDROID_SDK_ROOT || process.env.ANDROID_HOME;
if (!sdkRoot) throw new Error("ANDROID_SDK_ROOT/ANDROID_HOME is required to verify APK metadata");
const buildToolsRoot = resolve(sdkRoot, "build-tools");
if (!existsSync(buildToolsRoot)) throw new Error(`Android build-tools directory missing: ${buildToolsRoot}`);
const versions = readdirSync(buildToolsRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
const tool = (name) => {
  for (const version of versions) {
    const candidate = resolve(buildToolsRoot, version, process.platform === "win32" ? `${name}.exe` : name);
    if (existsSync(candidate)) return candidate;
  }
  throw new Error(`Android build tool not found: ${name}`);
};
const aapt = tool("aapt");
const apksigner = tool("apksigner");

const badging = run(aapt, ["dump", "badging", artifactPath]);
const packageMatch = badging.match(/^package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'/m);
if (!packageMatch) throw new Error("aapt dump badging did not return package/version metadata");
const [, actualPackageId, versionCode, versionName] = packageMatch;
if (actualPackageId !== expectedPackageId) {
  throw new Error(`Package ID mismatch: expected ${expectedPackageId}, got ${actualPackageId}`);
}

const signatureOutput = run(apksigner, ["verify", "--verbose", artifactPath]);
if (!/Verified using v[123] scheme/i.test(signatureOutput)) {
  throw new Error("apksigner did not report a verified APK signing scheme");
}

const entries = run("unzip", ["-Z1", artifactPath]).split(/\r?\n/);
const nativeAbis = [...new Set(entries
  .map((entry) => entry.match(/^lib\/([^/]+)\/.*\.so$/)?.[1])
  .filter(Boolean))].sort();
const requiredAbi = profile === "arm64" ? "arm64-v8a" : "x86_64";
if (!nativeAbis.includes(requiredAbi)) {
  throw new Error(`APK does not contain required native ABI ${requiredAbi}; found: ${nativeAbis.join(", ") || "none"}`);
}

const bytes = readFileSync(artifactPath);
const sha256 = createHash("sha256").update(bytes).digest("hex");
const manifest = {
  artifactName,
  variant,
  profile,
  expectedPackageId,
  actualPackageId,
  versionCode,
  versionName,
  sizeBytes: bytes.length,
  sha256,
  nativeAbis,
  signatureVerified: true,
  signatureVerificationTool: basename(apksigner),
  sourceSha: process.env.GITHUB_SHA || "UNKNOWN",
  workflowRunId: process.env.GITHUB_RUN_ID || "UNKNOWN",
  workflowRunAttempt: process.env.GITHUB_RUN_ATTEMPT || "UNKNOWN",
  createdAt: new Date().toISOString(),
};
writeFileSync(`${artifactPath}.sha256`, `${sha256}  ${basename(artifactPath)}\n`, "utf8");
writeFileSync(`${artifactPath}.manifest.json`, JSON.stringify(manifest, null, 2) + "\n", "utf8");
console.log(JSON.stringify(manifest, null, 2));
