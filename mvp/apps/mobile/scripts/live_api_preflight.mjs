const baseUrl = (process.env.EXPO_PUBLIC_API_BASE_URL || "").trim().replace(/\/+$/, "");
const timeoutMs = Number(process.env.POL_LIVE_QA_TIMEOUT_MS || "10000");

function fail(message) {
  console.error("[LIVE-QA FAIL]", message);
  process.exitCode = 1;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
  console.log("[LIVE-QA PASS]", message);
}

async function probe(path) {
  const url = baseUrl + path;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { method: "GET", signal: controller.signal });
    const body = await res.text();
    if (!res.ok) throw new Error(`${path} returned HTTP ${res.status}: ${body.slice(0, 240)}`);
    console.log("[LIVE-QA PASS]", path, "HTTP", res.status);
    return body;
  } finally {
    clearTimeout(timer);
  }
}

try {
  assert(baseUrl.length > 0, "EXPO_PUBLIC_API_BASE_URL is set");
  const parsed = new URL(baseUrl);
  assert(parsed.protocol === "http:" || parsed.protocol === "https:", "API base URL uses HTTP(S)");
  assert(!["localhost", "127.0.0.1", "10.0.2.2"].includes(parsed.hostname), "API base URL is not a loopback/emulator default");

  await probe("/healthz");
  await probe("/readyz");
  await probe("/api/v1/categories");

  if (new URL(baseUrl).protocol !== "https:") {
    console.warn("[LIVE-QA WARN] endpoint is HTTP; this is acceptable only for non-production staging verification.");
  }
  console.log("[LIVE-QA] Public API preflight completed.");
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}
