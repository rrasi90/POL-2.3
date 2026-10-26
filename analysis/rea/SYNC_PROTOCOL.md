# REA Evidence Synchronization Protocol

This protocol is mandatory for every REA skill/CLI/MCP investigation performed for POL.

## 1. Pre-flight and branch safety

1. Resolve the actual repository root using `git rev-parse --show-toplevel`; do not assume the shell's current directory is the repository.
2. Record `git status --short`, `git branch --show-current`, `git rev-parse HEAD`, and the configured remotes.
3. Never discard, reset, force-push, or silently overwrite existing user changes. If the working tree contains unrelated changes, leave them untouched and stage only `analysis/rea/`.
4. Fetch the remote and compare the local branch to its upstream. If local and remote histories diverge, inspect the commit graph and reconcile safely. Never use `git push --force` or `git reset --hard` to resolve a sync problem.
5. Confirm which branch is intended for the current work. Do not push to `main` unless the user explicitly requests it or the repository's documented workflow requires it.

## 2. Run identifiers and immutable evidence

1. Use a unique run directory such as `analysis/rea/runs/2026-10-26-cartona-v2/`. For a repeat run on the same day, append a short unique suffix.
2. Never rewrite or delete a previous run's evidence to make the latest result look cleaner. A correction creates a new run or a clearly named revision directory and links back to the original.
3. Every run must include `run-log.md` recording objective, target artifact identity, exact commands/tools invoked, timestamps, exit codes, tool versions, changed files, validations, commit SHA, and sync/read-back result.
4. Record the target artifact's SHA-256, package/version metadata, and source path only as appropriate. Do not upload the original APK or bulky recovered binary artifacts.

## 3. Required report set

For a full APK audit, include these files when applicable:

- `executive-summary.md`
- `apk-identity-and-integrity.json`
- `audit-evidence.json`
- `static-analysis-findings.md`
- `user-journey-inventory.md`
- `pol-feature-gap-matrix.csv`
- `implementation-priorities.md`
- `limitations-and-unknowns.md`
- `validation.json`
- `run-log.md`

For a smaller REA task, include a scoped summary, sanitized evidence bundle, limitations, and run log; mark non-applicable files explicitly instead of inventing them.

## 4. Evidence quality and safety

1. Use actual command output and provider evidence. Do not invent results, evidence IDs, exit codes, files, screenshots, or runtime behavior.
2. Distinguish `VERIFIED`, `HYPOTHESIS`, `UNVERIFIED`, and `UNKNOWN`. Static strings alone do not prove a route is invoked or a feature works at runtime.
3. Preserve the artifact hash, provider/tool version, operation name, sanitized parameters, limitations, and references for each material finding.
4. Sanitize JSON payloads and logs before committing. Remove tokens, cookies, credentials, customer data, personal identifiers, and live secrets.
5. Do not commit the APK/XAPK, extracted DEX, full decompilation, Dart AOT snapshot, native shared libraries, private SQLite/database dumps, or third-party proprietary source. Commit only appropriately scoped findings and evidence excerpts.
6. Do not contact production endpoints or execute an analyzed APK unless a separate task explicitly authorizes a safe runtime-testing plan.

## 5. Importing an existing local report set

For the first sync, inspect `C:\\Star\\pol-2.4\\analysis-v2\\` if it exists. Verify these eight files before import:

1. `executive-summary.md`
2. `apk-identity-and-integrity.json`
3. `audit-evidence.json`
4. `static-analysis-findings.md`
5. `user-journey-inventory.md`
6. `pol-feature-gap-matrix.csv`
7. `implementation-priorities.md`
8. `limitations-and-unknowns.md`

Copy the files into a new run directory under `analysis/rea/runs/`, not to the repository root. Preserve source copies. If one is absent, mark it missing; do not fabricate a replacement and claim it was copied.

## 6. Validate before committing

- Parse every JSON file with a standard JSON parser (for Python, `python -m json.tool <file>`).
- Parse CSV with a real CSV parser; verify the expected column count and consistent rows.
- Check every report's artifact SHA-256 against the other reports.
- Check evidence IDs and claims are consistent across the run files.
- Confirm all referenced paths are either valid repository-relative paths or explicitly labeled as external/local.
- Run `git diff --check` and inspect `git diff --cached --stat` plus the staged diff.
- Ensure the staged changes contain only intended, sanitized report artifacts and index updates.

Write validation outcomes, warnings, missing artifacts, and coverage boundaries in `validation.json` and `run-log.md`.

## 7. Commit, push, and verify remote read-back

1. Stage only the intended `analysis/rea/` files.
2. Create a descriptive commit, for example `docs(rea): sync Cartona audit 2026-10-26-v2`.
3. Push the intended branch to the configured GitHub remote. Do not claim synchronization on a local commit alone.
4. If push is rejected, fetch and investigate divergence. Reconcile without force-pushing or removing other people's commits.
5. After push, read the remote branch and confirm the commit SHA and all expected paths. Prefer `git fetch`, `git ls-tree`, and `git show origin/<branch>:analysis/rea/...` or the equivalent GitHub API read-back.
6. Update `LATEST.md` and `sync-manifest.json` with the new run path, branch, commit SHA, validation status, and remote read-back status. Because these index files themselves need to be synced, commit and push the index update too, then read it back again.
7. If any step is blocked, mark synchronization as `PARTIAL` or `BLOCKED`; never report `SYNCED` until remote read-back succeeds.

## 8. Definition of done

A run is `PASS / SYNCED` only when:
- evidence and deliverables are stored under a new run directory,
- JSON/CSV validation completed,
- limitations and any missing artifacts are recorded,
- the commit was pushed to the intended remote branch,
- the expected files were read back from GitHub,
- and `LATEST.md` plus `sync-manifest.json` point to that exact commit/run.

Local generation success is not GitHub sync success.
