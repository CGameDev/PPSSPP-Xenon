# First CCLOS-style launcher checkpoint — M4

The native launcher now uses the requested dark navy/teal presentation with
**both switchable Games grid and compact views**. Both full local XDK Rebuilds
finish with **0 warnings and 0 errors**. No Xbox connection, deployment or launch
was performed. Styling remains provisional for owner review; hardware behavior
and performance remain **NOT RUN**.

## Implemented scope

`baseline-overlay/cclos-launcher-milestone.patch` changes only XboxLauncher.cpp
and its header over M3. The new CclosLauncherTheme.h supplies colors, geometry,
bounded text/image fitting and conversion between grid-row/list-item scroll
offsets. Three nonvirtual methods are added; class state and layout are unchanged.

- Static navy panels, teal selection borders, safe 1280×720 insets, header/tabs,
  selected-game details and the existing controller hints.
- Four columns × three visible grid rows or eight compact rows. Titles and
  paths fit their pixel width with ellipses; non-ASCII bytes use the existing
  atlas's question-mark glyph. Existing ASCII-only font coverage is not expanded.
- Aspect-preserving artwork from the existing poster/icon cache; folder,
  missing-art, empty and loading presentations. No new shader, texture asset,
  animation, network, decoder or cache policy is introduced.
- RT switches Games views while preserving the selected game and converting
  offset units so it stays visible. Existing A file/folder requests, B exit,
  LB/RB tabs, debounce and repeat logic remain. Recent retains its existing
  grid-only policy. The already inactive Settings action is labelled unavailable.

All 3,878 source/project/font/image files in the manifest were compared with M3:
only XboxLauncher.cpp/.h differ. The additional generated git-version.cpp moves
from m3 to m4. Core, GPU, Common, FFmpeg sources, XboxMain and the session helper
are unchanged. Thirty-three other launcher methods, including artwork loaders,
resource creation, drawing primitives, animated background and in-game menu/toast
paths, match M3 exactly. Only the launcher's call to its animated background is
replaced; in-game behavior is preserved in source. Fresh preparation reproduces
the exact built launcher/helper/project bytes.

## Review previews

Open [the implementation preview](../design/cclos-preview.html). It visualizes
draw commands from the actual native methods with host device/cache stubs,
including both views and empty/missing-art/long-title/folder/Recent/loading
scenarios. Artwork is fictional; browser text rasterization is approximate.
These are **host previews, not Xbox screenshots**. The earlier broader concept
study remains [separate](../design/cclos-concept-m0.html). Both view types were
approved; detailed spacing, typography and TV readability are still open.

## Validation

| Check | Result |
| --- | --- |
| Owner archive authority and every ZIP member CRC | PASS; original SHA-256 unchanged |
| Twelve FFmpeg libraries / 436 PPCBE objects | PASS; byte-identical to M3 |
| Full Debug Rebuild | PASS; 0 warnings / 0 errors |
| Full Release_LTCG Rebuild | PASS; 0 warnings / 0 errors |
| Existing host unit tests | 20 PASS; no local skips |
| Existing state-deletion fixture | PASS |
| Source-derived M3 regressions against M4 | PASS; numeric, native host SEH, owner lifecycle, emitter/cache/hash and negative controls |
| Actual launcher method traces | PASS; both views and all listed fixture states |
| Packed font quad bounds and bounded text/image fitting | PASS; existing donor font/packing settings |
| RT toggle debounce/selection visibility and existing input requests | PASS with host stubs |
| Inactive Render/Update and view switch side effects | PASS; no work while inactive, no scan/write/resource calls from switching |
| Fresh source replay / class state / unaffected methods | PASS |
| Browser scene/view/viewport combinations | 56 PASS; no page errors or external requests |
| Xbox boot, runtime, rendering/input/audio, states/switching, memory or performance | NOT RUN |

The fixed 14-title fixture gives this bounded drawing comparison:

| View | M3 → M4 draw calls | Triangles | Artwork lookups |
| --- | --- | --- | --- |
| Grid | 153 → 80 | 740 → 636 | 15 → 13 |
| Compact | 157 → 64 | 632 → 562 | 11 → 9 |

Counts include the entire launcher frame with the same cache fixtures; the new
geometry shows fewer items at once. Old nine-slice shadows count as one batched
draw each. M4 removes the launcher's 100 moving symbol draws/trigonometry. Grid
artwork now queries up to 13 texture descriptors for aspect fitting (M3 grid: 0);
compact queries 9 versus 10. Those metadata reads reuse cached textures. No
frame-time or CPU/GPU speedup is inferred from these host counts. The normal
emulation loop receives no new per-frame calls; inactive launcher methods return
before resource or drawing work. Actual Xbox performance equivalence still needs
measurement at a separately authorized checkpoint.

## Evidence and limits

[M4 evidence](evidence/m4/) contains full redacted build logs, zero-warning
audits, XEX/source identities, preservation and deployment metadata, host outputs,
trace comparison and browser checks. [Build instructions](BUILD_XBOX360.md)
reproduce the fresh stage, local builds and host checks. XEX files are kept local
and not committed; timestamps/paths mean deterministic binary identity is not
claimed. No SDK or private CCLOS assets are published.

All four Deploy entries remain explicitly excluded. The build driver still
refuses missing/enabled exclusions and verifies library architecture first.
Historical M1's failed SDK auto-copy attempt remains recorded; M4 makes no console
actions. The owner explicitly requested this provisional launcher milestone
while deferring hardware tests; earlier hardware-first ordering is historical.

Keep PR #2 draft. No deployment, launch, baseline tag, merge or release is part
of this checkpoint. The previous [M3 report](BASELINE_M3.md) and its evidence are
historical at `6f65400eacc6200fa198351bd324a368ed5ad6df`. M0–M2 reports and failures
remain. To roll back the UI, revert the M4 checkpoint commit (or omit only its
last patch/helper and restore the m3 identity); the authentic archive, dependency
recovery and warning fixes remain independent.
