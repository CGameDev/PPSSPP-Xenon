# Baseline compatibility layer

The archive is the byte-exact original. These patches apply only to fresh build
staging and never alter that archive.

- `launcher-legacy-compat.patch`: legacy atlas-name mappings, state-deletion API
  bridge and truthful failure toast. No new scans, effects or session rewrite.
- `local-build-project.patch`: excludes every Deploy entry and corrects the
  Release_LTCG FFmpeg directory relative to the executable project.
- `Xbox/XenonStateDeleteCompat.h`: deletes only the selected current-title state
  and optional screenshot using core-generated paths. Empty/missing paths and
  partial failures return false. It never scans or deletes folders.

Preparation verifies archive/donor identities, records pristine source hashes,
normalizes patch-target line endings to LF and checks/applies both patches.
Owner files always win same-path conflicts before this separate compatibility
step. The licensed font header/helper and guarded provenance string follow.
Fresh replay was compared with the built files. Runtime validation remains open.
