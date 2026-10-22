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
const taskRowPattern = /^\s*-\s*\[([ xX])\]\s+`TODO-(\d{3})`(?:\s|$)/;
const rowsById = new Map();
for (const line of lines) {
  const match = line.match(taskRowPattern);
  if (!match) continue;
  const id = `TODO-${match[2]}`;
  const number = Number(match[2]);
  if (number > 154) {
    blocked.push(`${id}: task ID exceeds the gate-supported range TODO-154; review/update the gate before APK eligibility`);
  }
  const existing = rowsById.get(id) ?? [];
  existing.push(line);
  rowsById.set(id, existing);
}

for (const [id, rows] of rowsById) {
  if (rows.length !== 1) blocked.push(`${id}: duplicate task row (${rows.length} occurrences)`);
}

for (const number of requiredIds) {
  const id = `TODO-${String(number).padStart(3, "0")}`;
  const rows = rowsById.get(id) ?? [];
  if (rows.length !== 1) {
    blocked.push(`${id}: expected exactly one canonical task row; found ${rows.length}`);
    continue;
  }
  const row = rows[0];
  if (!/^\s*-\s*\[x\]/i.test(row) || !row.includes("DONE_VERIFIED")) {
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
