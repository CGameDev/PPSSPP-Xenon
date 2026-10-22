# Baseline compatibility layer

The archive is the byte-exact original. These patches apply only to fresh build
staging and never alter that archive.

- `launcher-legacy-compat.patch`: legacy atlas-name mappings, state-deletion API
  bridge and truthful failure toast. No new scans, effects or session rewrite.
- `local-build-project.patch`: excludes every Deploy entry and corrects the
  Release_LTCG FFmpeg directory relative to the executable project.
- `warning-fixes.patch`: match existing GPU global alignment in declarations,
  define both image-loader failure returns/cleanup and reject empty icon data.
  Struct layouts, successful pixel conversion and both UI modes stay intact.
- `remaining-warnings.patch`: typed numeric boundaries, post-construction cache
  binding, unused-code/project cleanup and owner-loop extraction; see the M3 review.
- `cclos-launcher-milestone.patch`: original M4 launcher presentation and bounded
  fitting/selection helpers, keeping both views.
- `cclos-ingame-menu.patch`: M5 menu/notification drawing only.
- `cclos-approved-shell.patch`: M6 reviewed navy/teal sidebar, larger grid/compact
  geometry and right-side slot/session pages; input and state handlers preserved.
- `pgf-endian-fix.patch`: M7 isolated PGF packed-bit byte order and 0/32-bit
  boundary correction; no font assets, state layout, settings or UI changes.
- `Xbox/CclosLauncherTheme.h` and `Xbox/CclosShellLayout.h`: presentation constants,
  fitted text/image helpers and bounded grid/list offsets, with no runtime hooks.
- `Xbox/XenonEmulationLoop.h`: original owner loop in a non-inlined SEH helper
  with POD locals. Main keeps its RAII objects; one call per session.
- `Xbox/XenonStateDeleteCompat.h`: deletes only the selected current-title state
  and optional screenshot using core-generated paths. Empty/missing paths and
  partial failures return false. It never scans or deletes folders.

Preparation verifies archive/donor identities, records pristine source hashes,
normalizes patch-target line endings to LF and checks/applies all eight patches.
Owner files always win same-path conflicts before this separate compatibility
step. The licensed font header/helper and guarded provenance string follow.
Fresh replay was compared with the built files. Runtime validation remains open.
