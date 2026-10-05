import { spawnSync } from "node:child_process";

const command = process.platform === "win32" ? "npx.cmd" : "npx";
const result = spawnSync(command, ["expo", "export", "--platform", "android"], {
  stdio: "inherit",
  env: { ...process.env, EXPO_ATLAS: "true" },
});
if (result.status !== 0) throw new Error("Expo Atlas bundle export failed");
