import path from "node:path";
import { defineConfig, devices } from "@playwright/test";

const REPO_ROOT = path.resolve(__dirname, "../../..");
const WEB_PORT = Number(process.env.POL_E2E_WEB_PORT ?? 3000);
const API_PORT = Number(process.env.POL_E2E_API_PORT ?? 8001);
const API_URL = `http://127.0.0.1:${API_PORT}`;

export default defineConfig({
  testDir: "./tests",
  outputDir: "./test-results",
  timeout: 90_000,
  expect: { timeout: 15_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 3 : 4,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "playwright-report" }],
    ["json", { outputFile: "test-results/results.json" }],
  ],
  use: {
    baseURL: `http://127.0.0.1:${WEB_PORT}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    locale: "fa-IR",
    timezoneId: "Asia/Tehran",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `python "${path.join(REPO_ROOT, "scripts", "e2e_serve.py")}"`,
      cwd: REPO_ROOT,
      url: `${API_URL}/healthz`,
      reuseExistingServer: !process.env.CI,
      timeout: 240_000,
      stdout: "pipe",
      stderr: "pipe",
      env: { POL_E2E_API_PORT: String(API_PORT) },
    },
    {
      command: "npm run dev",
      cwd: __dirname,
      url: `http://127.0.0.1:${WEB_PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 240_000,
      stdout: "pipe",
      stderr: "pipe",
      env: {
        NEXT_PUBLIC_API_BASE_URL: API_URL,
        PORT: String(WEB_PORT),
      },
    },
  ],
});
