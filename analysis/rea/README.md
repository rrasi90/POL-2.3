# REA Audit Workspace

This directory is the canonical, version-controlled home for sanitized REA (Reverse Engineer Anything) findings used to analyze authorized application artifacts and compare evidence with POL.

## Operating principle

**A REA task is synchronized only after its reports are validated, committed, pushed, and read back from GitHub.** A successful local command or local-only report is not a synchronized deliverable.

## Layout

```text
analysis/rea/
  README.md
  SYNC_PROTOCOL.md
  AGENT_PROMPT.md
  COMPREHENSIVE_CARTONA_EXTRACTION_PROMPT.md
  CARTONA_DEEP_EXTRACTION_REMEDIATION_PLAN.md
  LATEST.md
  sync-manifest.json
  runs/
    YYYY-MM-DD-<run-id>/
      reports and validated evidence artifacts
      validation.json
      run-log.md
```

Each run uses a new immutable directory. Preserve previous findings; update `LATEST.md` and `sync-manifest.json` to point to the latest run and exact commit.

## Current synchronized audit

The latest committed historical Cartona evidence run is the comprehensive extraction report under. Its original validator reported PASS, but later semantic review found defects; treat it as historical evidence and do not rely on its PASS label until the v3 remediation run verifies the data.

`runs/2026-10-26-cartona-comprehensive-extraction/`

- [Latest run status](LATEST.md)
- [Comprehensive executive summary](runs/2026-10-26-cartona-comprehensive-extraction/executive-summary.md)
- [Comprehensive validation](runs/2026-10-26-cartona-comprehensive-extraction/validation.json)
- [POL capability gap matrix](runs/2026-10-26-cartona-comprehensive-extraction/pol-feature-gap-matrix.csv)
- [Previous Revision 2 import](runs/2026-10-26-cartona-revision-2-import-02/executive-summary.md) — retained as historical evidence.

The reported APK SHA-256 is `e4a0f4d1a3a607ad4e06e73fee70bf296c14205696b1cdc20892b5e893df808c`. Re-hash the original artifact when it is available for a new analysis.

## How to use this workspace

- For routine REA investigation and synchronization, follow [the reusable agent prompt](AGENT_PROMPT.md).
- For the baseline APK/XAPK workflow, use [the comprehensive extraction prompt](COMPREHENSIVE_CARTONA_EXTRACTION_PROMPT.md), but it does not replace the latest execution plan.
- For remediation of the previous run, Agent failure recovery, toolchain decisions and deeper extraction, follow the [hardened Cartona deep-extraction execution plan (v2)](CARTONA_DEEP_EXTRACTION_REMEDIATION_PLAN.md).
- Apply the requirements in [the synchronization protocol](SYNC_PROTOCOL.md).
- Read the current status from [LATEST.md](LATEST.md) and [sync-manifest.json](sync-manifest.json).

## What belongs here

- Sanitized Markdown reports, evidence metadata, CSV inventories and gap matrices.
- Artifact hashes, tool versions, exact coverage, limitations, confidence, test outcomes, stable evidence IDs, and relevant excerpts.
- UI/UX screen catalogs, selected representative evidence images when justified, route/feature maps, and independent product requirements.
- POL-relative file paths and implementation acceptance criteria verified against source.

## What must not be committed

Do not commit:
- Original Cartona APK/XAPK/split packages, extracted DEX files, complete Dart AOT snapshot, `.so` libraries, or other raw executable binaries.
- Bulk proprietary decompilation/recovered source/pseudocode, complete proprietary asset dumps, or full raw strings/snapshot dumps.
- Raw database contents, customer/business records, session tokens, credentials, API secrets, cookies, private keys, `.env` files, MCP config files, or personal data.
- Unredacted logs or evidence payloads containing sensitive information.

Keep full raw extraction artifacts in a local-only directory outside the Git working tree. Track their hashes, paths, parent artifacts, extraction method, and coverage in a private local manifest. Commit curated, proportionate evidence and analysis. Use findings to implement independent POL behavior; do not copy Cartona's proprietary code into POL.

## Audit history and accuracy

- Keep the initial blocked import attempt at `runs/2026-10-26-cartona-revision-2-import-attempt-01/` for audit history.
- Keep the validated Revision 2 import at `runs/2026-10-26-cartona-revision-2-import-02/`.
- A static string does not prove runtime execution. Clearly distinguish verified artifact facts, runtime observations, hypotheses, and unknowns.
- Never claim that all original source code was recovered from a compiled APK.
