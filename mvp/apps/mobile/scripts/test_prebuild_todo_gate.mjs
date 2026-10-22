import assert from "node:assert/strict";
import {
  existsSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const gateScript = resolve(here, "check_prebuild_todo_gate.mjs");

// Keep this mirror explicit: changes to the gate's required list must also
// update these fixtures so the negative/positive behavior remains reviewable.
const requiredIds = [
  ...Array.from({ length: 6 }, (_, index) => 12 + index),
  ...Array.from({ length: 23 }, (_, index) => 61 + index),
  ...Array.from({ length: 46 }, (_, index) => 85 + index),
  131, 132, 133, 134, 135, 136, 138, 139, 144, 145, 147, 149, 84,
];

const doneRows = () =>
  requiredIds.map((number) =>
    `- [x] \`TODO-${String(number).padStart(3, "0")}\` DONE_VERIFIED — fixture row`,
  );

function evaluate(rows) {
  const root = mkdtempSync(join(tmpdir(), "pol-todo-084-gate-"));
  const cwd = join(root, "mvp", "apps", "mobile");
  const outputPath = join(root, "github-output.txt");
  mkdirSync(cwd, { recursive: true });
  writeFileSync(join(root, "TODO_LIST.md"), rows.join("\n") + "\n", "utf8");

  try {
    const result = spawnSync(process.execPath, [gateScript], {
      cwd,
      encoding: "utf8",
      env: { ...process.env, GITHUB_OUTPUT: outputPath },
      timeout: 10_000,
    });
    assert.ifError(result.error);
    assert.equal(result.status, 0, result.stderr || result.stdout);
    const output = existsSync(outputPath)
      ? readFileSync(outputPath, "utf8")
      : "";
    return { stdout: result.stdout ?? "", output };
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

const valid = evaluate(doneRows());
assert.match(valid.output, /^allow_qa_apk=true\n$/m);
assert.match(valid.stdout, /PREBUILD_QA_APK_GATE=PASS/);
console.log("PASS: all required tasks DONE_VERIFIED => allow_qa_apk=true");

const openTask = doneRows().map((row) =>
  row.startsWith("- [x] `TODO-084`")
    ? row.replace("- [x]", "- [ ]").replace("DONE_VERIFIED", "OPEN")
    : row,
);
const blockedOpen = evaluate(openTask);
assert.match(blockedOpen.output, /^allow_qa_apk=false\n$/m);
assert.match(blockedOpen.stdout, /TODO-084: not DONE_VERIFIED/);
console.log("PASS: unchecked required task => allow_qa_apk=false");

const missingTask = doneRows().filter((row) => !row.startsWith("- [x] `TODO-061`"));
const blockedMissing = evaluate(missingTask);
assert.match(blockedMissing.output, /^allow_qa_apk=false\n$/m);
assert.match(blockedMissing.stdout, /TODO-061: expected exactly one canonical task row; found 0/);
console.log("PASS: missing required task => allow_qa_apk=false");

const duplicateTask = [...doneRows(), "- [x] `TODO-061` DONE_VERIFIED — duplicate fixture row"];
const blockedDuplicate = evaluate(duplicateTask);
assert.match(blockedDuplicate.output, /^allow_qa_apk=false\n$/m);
assert.match(blockedDuplicate.stdout, /TODO-061: duplicate task row \(2 occurrences\)/);
console.log("PASS: duplicate task ID => allow_qa_apk=false");

const unknownTask = [...doneRows(), "- [x] `TODO-155` DONE_VERIFIED — unsupported future task"];
const blockedUnknown = evaluate(unknownTask);
assert.match(blockedUnknown.output, /^allow_qa_apk=false\n$/m);
assert.match(blockedUnknown.stdout, /TODO-155: task ID exceeds the gate-supported range TODO-154/);
console.log("PASS: unknown future task ID => allow_qa_apk=false");

const malformedTask = doneRows().map((row) =>
  row.startsWith("- [x] `TODO-061`")
    ? "- [x] TODO-061 DONE_VERIFIED — malformed fixture row"
    : row,
);
const blockedMalformed = evaluate(malformedTask);
assert.match(blockedMalformed.output, /^allow_qa_apk=false\n$/m);
assert.match(blockedMalformed.stdout, /TODO-061: expected exactly one canonical task row; found 0/);
console.log("PASS: malformed required task row => allow_qa_apk=false");

console.log("All TODO-084 gate fixture tests passed (6/6).");
