# HAD-CV M0 — recovery gate and reviewable UI concepts

HAD-CV is applied as bounded autonomous development with continuous verification:
freeze input identities, inspect a discrepancy, implement the smallest independent
change, verify it, retain PASS/FAIL/BLOCKED/NOT RUN evidence and preserve rollback.
The owner controls design acceptance and release. Routine host development does
not need repeated permission.

## Authorized M0 delivered scope

- Read-only Python source-overlay gate with strict Base64 decoding, immutable
  expected SHA-256, complete ZIP CRC diagnostics, required-member checks and
  bounded diagnostic sizes. It never extracts, imports, repairs or writes source.
- Host tests for trusted fixture success, hash/CRC failure independence, malformed
  archive/Base64, missing source/parts, size limit and preservation of existing
  extracted files. Synthetic fixtures cannot certify the real damaged archive.
- CI runs host tests separately from real owner-source integrity. The latter
  remains red while corruption exists; the expected hash is not weakened.
- Frozen baseline, real legacy donor build failure, feasibility, next gates and
  CCLOS-style review concepts. No emulator implementation or tuning changed.

## State

| Item | State |
| --- | --- |
| Source authenticity gate implementation | PASS, host verification |
| Owner source authenticity | FAIL, retained evidence |
| Working emulator baseline | BLOCKED |
| Tile + compact views | Owner selected **both as switchable views**, 2026-10-21 |
| Detailed visual design | Provisional / review pending |
| Production CCLOS renderer | Not implemented; source/build baseline gate applies |
| Physical Xbox validation | NOT RUN; no console connection/deployment attempted |
| Release/merge | Not accepted; review through draft PR |

## Next bounded milestone

Recover the authentic owner archive and Xbox FFmpeg dependency provenance. Import
the complete source with attribution, overlay last, then establish a linkable
unchanged baseline. Do not create `xenon-baseline-legacy` until its building
requirements are met. Group physical validation into one baseline checkpoint:
ISO/CSO/homebrew boot, audio/input, savedata, reset, state save/load, failed-launch
recovery and at least twenty return/relaunch/switch transitions. Record actual
backend, memory after cache stabilization, file handles and frame-time evidence.

UI implementation follows that checkpoint and the design review. Keep both view
types; do not treat that selection as acceptance of exact typography, spacing,
artwork, navigation or runtime behavior shown in the concepts.

## Rollback

M0 is additive host tooling/documentation/design content, plus an entry-point
warning. Reverting the M0 commit restores the original handoff. Original archive
parts and their expected hash are unchanged. No SDK binaries, media, ROMs,
commercial artwork, console credentials, XEX or generated libraries are published.
