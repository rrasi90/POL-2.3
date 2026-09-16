# POL Penpot Working Artifact

Source file: `New File 1.penpot.zip`
Original SHA-256: `b27dab72381f4e4551b684090f8caff3198f6b113a460c61a484d68e3d7ecbda`

This directory stores the uploaded Penpot export as versioned Base64 chunks because the repository connector cannot upload a multi-megabyte binary artifact directly.

## Rebuild

Run:

```bash
python scripts/rebuild_penpot_zip.py
```

The script reconstructs `New File 1.penpot.zip` from `parts/` and verifies the SHA-256 checksum.

## Working rule

Edits to the Penpot export should be made from the reconstructed archive, validated locally, then the archive should be re-chunked so this folder remains the versioned source artifact.
