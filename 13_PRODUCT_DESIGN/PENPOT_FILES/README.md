# POL Penpot Design Files Archive

## Overview

This directory (`13_PRODUCT_DESIGN/PENPOT_FILES/`) serves as the **canonical GitHub archive** for all POL Penpot design source and export artifacts.

- **Canonical Repository**: `rrasi90/POL-2.3`
- **Target Branch**: `research-hardening-2026-09-14`
- **Synchronization Date**: `2026-09-16`
- **Active Penpot Project**: `New File 1` (`d8ac01df-6646-81d2-8008-a4f2f52bf86c`)

---

## Directory Architecture

```text
13_PRODUCT_DESIGN/PENPOT_FILES/
├── SOURCE/
│   └── New File 1.penpot.zip      # Canonical Penpot source archive
├── EXPORTS/                        # Exported assets, SVG/PDF slices, or page bundles
├── ARCHIVE/                        # Historical milestone versions and deprecations
├── MANIFEST/
│   ├── PENPOT_FILE_MANIFEST.json  # Machine-readable artifact metadata schema
│   ├── PENPOT_FILE_MANIFEST.md    # Human-readable inventory and audit log
│   └── SHA256SUMS.txt             # Cryptographic checksums for integrity verification
└── README.md                       # Operational rules and governance documentation
```

---

## Operational Rules & Governance

1. **Canonical Archive**: This directory is the sole versioned repository archive for raw Penpot source/export artifacts.
2. **Preserve Filenames**: Original source filenames and extensions (`.penpot`, `.penpot.zip`) must be preserved as emitted by Penpot. Do not artificially rename or flatten archive structures.
3. **Manifest Synchronization**: Never manually add, replace, or remove an artifact without recomputing SHA-256 checksums and updating `PENPOT_FILE_MANIFEST.json`, `PENPOT_FILE_MANIFEST.md`, and `SHA256SUMS.txt`.
4. **Integrity Verification**: Every committed binary artifact is strictly verified against its recorded SHA-256 hash before and after git operations.
5. **Separation of Authority**:
   - **Visual Execution Layer**: Penpot is the design execution and prototyping tool.
   - **Business Rules Authority**: Product and business specifications remain strictly governed by POL canonical documents (`DECISION_REGISTER.md`, `13_PRODUCT_DESIGN/*.md`, and functional specifications). Penpot visual files do not supersede canonical written specifications.
6. **No Credentials/Secrets**: Penpot access URLs containing user tokens, session cookies, or environment variables must never be committed.

---

## Restoring or Importing into Penpot

To import this project into any Penpot workspace:
1. Download `13_PRODUCT_DESIGN/PENPOT_FILES/SOURCE/New File 1.penpot.zip`.
2. Open your Penpot dashboard (or self-hosted Penpot instance).
3. Click **Import file** and select `New File 1.penpot.zip`.
4. All 11 pages, components, variants, and design tokens will be restored natively.
