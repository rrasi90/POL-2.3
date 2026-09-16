# POL Penpot Revision 69 Sync Report

Date: 2026-09-16
Branch: `research-hardening-2026-09-14`
Project: `New File 1`
Penpot File ID: `d8ac01df-6646-81d2-8008-a4f2f52bf86c`

## New externally downloaded snapshot

The user supplied a fresh Penpot export downloaded directly from Penpot:

- Filename: `New File 1.penpot_2.zip`
- Size: `6,040,863` bytes
- SHA-256: `ba7e9b53c71d156b73b49f44e86a918052a14120aa78a9a6c626f398b5cb787f`
- Penpot revision (`revn`): `69`
- Modified at: `2026-09-16T08:52:00.095061Z`
- Penpot format version: `67`
- Penpot generator: `penpot/2.18.0-RC5`
- ZIP entries: `2,046`

## Existing GitHub snapshot

The currently archived GitHub file remains:

- Path: `13_PRODUCT_DESIGN/PENPOT_FILES/SOURCE/New File 1.penpot.zip`
- Size: `5,810,558` bytes
- SHA-256 recorded in the repository manifest: `b27dab72381f4e4551b684090f8caff3198f6b113a460c61a484d68e3d7ecbda`
- Git blob SHA: `751677d321bd096a2ec5a0479c2aed72613cdcc5`
- Recorded modified time: `2026-09-16T07:28:10.579843Z`

## Conclusion

The two archives are NOT byte-identical, but they belong to the same Penpot project because the internal Penpot File ID is identical.

The user-supplied archive is a newer snapshot (`revn=69`) than the currently archived GitHub snapshot. Therefore the GitHub archive is stale relative to the supplied download.

## Important limitation

The GitHub connector available in this session can create/update UTF-8 text files, but cannot upload a local multi-megabyte binary file from the working container as a repository blob. Therefore this report records the verified newer snapshot, but the binary `New File 1.penpot.zip` in `SOURCE/` has NOT been replaced by revision 69 in this commit.

Do not mark the GitHub binary as revision 69 until the actual binary archive has been uploaded and its SHA-256 has been re-verified.

## Required next binary sync

Upload the supplied revision-69 archive as a new historical snapshot or replace the current source only after preserving the old snapshot. Recommended archive path:

`13_PRODUCT_DESIGN/PENPOT_FILES/ARCHIVE/New File 1__rev69__2026-09-16.penpot.zip`

Then update the manifest and `SHA256SUMS.txt` with the verified SHA-256 above.
