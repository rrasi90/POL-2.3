import { appendFileSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

// QA APKs are prohibited by TODO_LIST.md until the canonical pre-build
// qualification tasks and aggregate TODO-084 gate are DONE_VERIFIED.
// Missing/malformed task rows fail closed; this job reports a blocked gate
// without failing the non-build CI checks.
const requiredIds = [
  ...Array.from({ length: 23 }, (_, index) => 61 + index),
  ...Array.from({ length: 46 }, (_, index) => 85 + index),
  131, 132, 133, 134, 135, 136, 138, 139, 144, 145, 147, 149, 84,
];

const todoPath = resolve(process.cwd(), "../../../TODO_LIST.md");
let lines;
try {
  lines = readFileSync(todoPath, "utf8").split(/\r?\n/);
} catch (error) {
  console.error(`PREBUILD_QA_APK_GATE=BLOCKED — could not read ${todoPath}: ${error instanceof Error ? error.message : String(error)}`);
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, "allow_qa_apk=false\n");
  process.exit(0);
}

const blocked = [];
for (const number of requiredIds) {
  const id = `TODO-${String(number).padStart(3, "0")}`;
  const escaped = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const rowPattern = new RegExp(`^\\s*-\\s*\\[([ xX])\\]\\s+` + "`" + escaped + "`" + `(?:\\s|$)`);
  const row = lines.find((line) => rowPattern.test(line));
  if (!row) {
    blocked.push(`${id}: task row missing or format changed`);
  } else if (!/^\s*-\s*\[x\]/i.test(row) || !row.includes("DONE_VERIFIED")) {
    blocked.push(`${id}: not DONE_VERIFIED (checked checkbox and explicit status are both required)`);
  }
}

const allowed = blocked.length === 0;
const output = allowed ? "true" : "false";
if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, `allow_qa_apk=${output}\n`);

if (allowed) {
  console.log(`PREBUILD_QA_APK_GATE=PASS — ${requiredIds.length} required TODO rows are checked.`);
} else {
  console.log(`PREBUILD_QA_APK_GATE=BLOCKED — ${blocked.length} of ${requiredIds.length} required TODO rows are not verified.`);
  for (const item of blocked) console.log(`BLOCKED | ${item}`);
  console.log("QA APK jobs will be skipped. Internal source, typecheck, API/E2E, static and independent verification jobs remain enabled.");
}
