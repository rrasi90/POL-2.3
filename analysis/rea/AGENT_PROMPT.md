# Reusable Agent Prompt — Run REA and Sync Everything to GitHub

Copy the prompt below into ZCode/OpenCode or another agent that has the REA skill installed.

---

## Prompt

You are working in the POL repository. Your goal is to perform the requested REA investigation and make every useful, sanitized deliverable directly reviewable from GitHub.

### Mandatory reading

Before using REA, read:

- `analysis/rea/README.md`
- `analysis/rea/SYNC_PROTOCOL.md`
- the locally installed `reverse-engineer-anything` skill instructions and any relevant bundled Android-analysis references.

Use the actual tool names, schemas, and limits exposed by the installed REA version. Do not invent commands or assume a CLI result proves the MCP server is available.

### First-run bootstrap

If `analysis/rea/LATEST.md` says the initial import is pending, locate the existing report set at `C:\\Star\\pol-2.4\\analysis-v2\\` (or identify the equivalent location if the project has moved). Import the eight Revision 2 deliverables listed in the sync protocol into a new immutable directory under `analysis/rea/runs/`. Validate them and record any missing item. Do not modify the original v1 reports.

### For every new REA task

1. Establish repository root, branch, current commit, remote, and working-tree status. Preserve unrelated local edits.
2. Run the requested analysis using REA CLI/MCP and any genuinely necessary supporting tools.
3. Save the useful results as sanitized, inspectable reports and structured evidence under a new directory named `analysis/rea/runs/YYYY-MM-DD-<task-id>/`.
4. Preserve real operation names, inputs, artifact hashes, provider versions, evidence IDs, limitations, exit codes, and coverage boundaries. Clearly separate verified facts from hypotheses and unknowns.
5. For APK work, inspect the Flutter/native/framework architecture before treating a decompiled launcher stub as the product's main logic. Search relevant DEX classes, manifest entries, resources, assets, Dart/JavaScript bundles, API clues, and data models as applicable. Do not assume that string mining alone proves runtime behavior.
6. Compare each product finding against the actual current POL source, navigation, API contracts, data models, and tests. Every gap row must contain evidence and exact POL file paths. Use `UNVERIFIED` when evidence is insufficient.
7. Do not change POL application code unless the user separately requests implementation. A research task must not silently become a code-change task.
8. Validate JSON and CSV with real parsers; verify artifact hashes and evidence IDs; run `git diff --check`; inspect staged changes.
9. Update `analysis/rea/LATEST.md` and `analysis/rea/sync-manifest.json` to point to this run and its validation state.
10. Stage only the intended `analysis/rea/` files, commit using a descriptive message, and push to the intended branch. Never force-push, reset away user changes, or commit APKs, complete proprietary decompilation, secrets, credentials, or real customer data.
11. Verify the new commit and expected files by reading them back from the remote GitHub branch. Update the run log with the remote-read-back result. Sync that index update too and verify it again.

### Mandatory final response

Report:
- exact repository, branch, local HEAD and remote HEAD,
- run directory and files created,
- APK/artifact SHA-256 when applicable,
- commands/tools actually executed and exit/status,
- JSON/CSV validation results,
- test and analysis coverage plus limitations,
- commit SHA and GitHub links,
- remote read-back evidence,
- remaining gaps or blockers.

Use exactly one of these final synchronization statuses:

- `PASS / SYNCED` — all deliverables are committed, pushed and confirmed by remote read-back.
- `PARTIAL` — useful results exist but some deliverables, validation, push or read-back remain incomplete.
- `BLOCKED` — no reliable synchronization was completed.

Never claim a task is done just because REA commands exited zero. Never claim all code was recovered from an APK. Never invent evidence, test results, commits, or GitHub links.
