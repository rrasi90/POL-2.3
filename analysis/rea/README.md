# REA Audit Workspace

This directory is the canonical, version-controlled home for sanitized REA (Reverse Engineer Anything) analysis outputs used to understand authorized app artifacts and compare observed product behavior with POL.

## Operating principle

**No REA task is complete until its useful evidence and deliverables have been synchronized here, validated, committed, pushed, and read back from GitHub.** A local-only report is not a synchronized deliverable.

## Layout

```text
analysis/rea/
  README.md
  SYNC_PROTOCOL.md
  AGENT_PROMPT.md
  LATEST.md
  sync-manifest.json
  runs/
    YYYY-MM-DD-<run-id>/
      executive-summary.md
      apk-identity-and-integrity.json
      audit-evidence.json
      static-analysis-findings.md
      user-journey-inventory.md
      pol-feature-gap-matrix.csv
      implementation-priorities.md
      limitations-and-unknowns.md
      validation.json
      run-log.md
```

Each analysis run gets a new immutable directory. Do not overwrite a previous run's evidence. Update `LATEST.md` and `sync-manifest.json` to point to the latest complete run.

## Initial state

The Cartona APK v8.4.6 Revision 2 audit was reported as generated locally at `C:\\Star\\pol-2.4\\analysis-v2\\` on 2026-10-26. Its eight files have **not yet been imported into this directory**. The initial synchronization task must import and validate those eight files before claiming that Revision 2 is synchronized.

The reported APK SHA-256 is `e4a0f4d1a3a607ad4e06e73fee70bf296c14205696b1cdc20892b5e893df808c`. Always verify it against the original APK when the APK is available; do not treat a report's hash as proof that the current local file is identical.

## What belongs here

- Sanitized Markdown reports, CSV gap matrices, and valid JSON metadata/evidence bundles.
- Artifact identity and hashes, tool versions, coverage, limitations, confidence, test results, and stable references to evidence.
- A clear distinction between verified findings, hypotheses, and unknowns.
- POL-relative file paths and implementation acceptance criteria when supported by source inspection.

## What must not be committed

- The original Cartona APK/XAPK, extracted DEX files, full Dart AOT snapshot, `.so` libraries, reconstructed database files, or bulk proprietary decompilation output.
- Credentials, authorization tokens, API keys, cookies, private customer/business records, live secrets, `.env` files, MCP configuration files, or personal data.
- Unredacted logs or evidence payloads containing sensitive information.

Only inspect authorized artifacts. Use reverse-engineering results to document behavior and write independent POL implementations; do not copy proprietary code into POL. Keep evidence excerpts proportionate to the finding.

## Quick links

- [Sync protocol](SYNC_PROTOCOL.md)
- [Reusable agent prompt](AGENT_PROMPT.md)
- [Latest run status](LATEST.md)
- [Machine-readable sync manifest](sync-manifest.json)
