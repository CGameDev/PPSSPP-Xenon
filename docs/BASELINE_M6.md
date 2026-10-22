# Approved CCLOS shell implementation — M6

The reviewed navy/teal direction is implemented on PR #2: sidebar navigation,
larger three-by-two game cards, a six-row compact view with shared selection,
selected-game artwork, and a right-side in-game panel. Both full local XDK
Rebuilds pass with **0 warnings / 0 errors**. No console was contacted, deployed
to or launched. Xbox runtime and frame-time performance remain **NOT RUN**.

## Native scope

`baseline-overlay/cclos-approved-shell.patch` follows the six earlier patches.
It changes eight presentation methods and explicit layout constants/offset-helper
selection in XboxLauncher.cpp. `CclosShellLayout.h` supplies three-column/two-row
and six-row-list geometry with bounded selection offsets. The older theme helper
stays byte-identical, allowing independent reconstruction of the previous shell.

All other launcher source matches M5 after those explicit geometry substitutions.
UpdateInGameMenu, ShowToast, RenderToast, font/image fitting, class state/header,
XboxMain, session helper, Core, GPU, Common and FFmpeg remain unchanged. Among
3,876 source/project/font/image/helper/identity files compared with M5, differences
are limited to launcher.cpp, the new geometry header and generated m6 identity.
Fresh source preparation reproduces all 3,876 compared files exactly.

The same RT binding switches Games grid/compact while retaining selection and
visibility. Recent retains its existing grid-only policy. Folder entry, A launch,
LB/RB tabs, B exit and existing right-panel actions remain. This milestone does
not implement the concept's proposed game-details page or additional settings.

## Side-panel behavior and visual limits

The right panel presents the currently focused save-slot or session page.
Existing Left/Right switches pages; Up/Down selects a row. Opening still selects
Slot 1. A saves, X loads, Y deletes, and B continues. Session actions retain their
original indices and reset/exit flags. Settings is labelled unavailable and keeps
its legacy close-menu behavior. No serialization/reset/exit handler is rewritten.

Static navy/teal shading approximates the reviewed layered panels using existing
rectangles and cached artwork. Embedded PIC1/ICON0 images are fitted without
stretching. The side menu uses an **opaque static paused backdrop**, rather than
the concept's illustrated game scene. Retaining gameplay would require a
separately validated snapshot path instead of relying on swap-chain contents.
No live blur, framebuffer capture, new shader/texture, animation, decoder, thread,
filesystem query or cache policy is introduced. Five existing slot-presence
queries remain per visible menu frame. Normal notifications remain unchanged.

## Verification

| Check | Result |
| --- | --- |
| Owner archive hash / all 30 CRCs | PASS, unchanged authority |
| Twelve FFmpeg libraries / 436 PPCBE objects | PASS, byte-identical to M5 |
| Full Debug Rebuild | PASS, 0 warnings / 0 errors |
| Full Release_LTCG Rebuild | PASS, 0 warnings / 0 errors |
| Existing tests | 20 PASS, no skips in local VS2010 environment |
| Numeric/session/emitter/cache/hash regressions | PASS, including native Windows host SEH |
| Save/load/delete/session snapshots vs M5 | 137 identical, plus explicit action expectations |
| Exact source boundary / unchanged state handlers | PASS |
| Launcher frames / bounded costs | 14 PASS against reconstructed M5 |
| New grid/list navigation and offset boundaries | PASS, including partial rows and count limits |
| In-game frames / toast timing and inactive guards | 42 PASS |
| Browser scenarios | 56 launcher + 136 menu PASS, no errors/overflow/external requests |
| Fresh source replay / project Deploy exclusions | PASS, all four Deploy entries excluded |
| Xbox boot, real state round trips, reset, switching, frame times | NOT RUN |

Host checks compile extracted native methods with device/input/state stubs. They
do not execute PPC machine code, real saves or Xbox APIs. Current methods compile
with warnings treated as errors; the historical reference policy stays visible.
Previews use actual drawing traces with fictional artwork and approximate browser
text rasterization. See [launcher](../design/cclos-preview.html),
[side menu](../design/cclos-ingame-preview.html) and [evidence](evidence/m6/).

## Drawing cost versus M5

| Normal fixture | M5 → M6 draws | M5 → M6 triangles |
| --- | --- | --- |
| Grid library | 80 → 62 | 636 → 584 |
| Compact library | 64 → 56 | 562 → 554 |
| Save-slot menu | 47 → 30 | 518 → 480 |
| Session menu | 47 → 25 | 518 → 462 |
| Menu with notification | 49 → 32 | 546 → 508 |
| Gameplay notification | 2 → 2 | 28 → 28 |

Artwork lookups fall 13→7 in grid and 9→7 in compact. Draw/cache/descriptor counts
do not increase in any of the 14 launcher fixtures. Different fitted captions add
18/24 triangles for empty grid/list and six for compact folder; these explicit
glyph-only bounds are tested. Long notifications remain 130 triangles, unchanged
from M5. These are host work counts, **not Xbox performance measurements**.

The first host attempt caught redundant compact labels exceeding the older M3
triangle budget. Those labels were removed; final checks compare the immediately
preceding M5 shell. The initial failure log is retained. An exact-source checker
also identified six inserted blank-line separators; its documented, narrow
normalization accounts for them without relaxing executable-code comparison.
Both production builds succeeded on their first attempts.

## Readiness and rollback

Software remains at the first controlled console smoke-test gate. Exact TV
appearance, controller transitions, real save/load/reset, repeated switching,
memory stability and measured performance still require separately authorized
hardware testing. Read [CONSOLE_TEST_READINESS.md](CONSOLE_TEST_READINESS.md).
Keep PR #2 draft. No merge, release, tag or console action is part of M6.

The local M6 ZIP contains two XEX candidates plus identities, not a complete
runtime install. No binaries, SDK content or game data are committed. Reverting
the M6 implementation commit restores M5 while preserving source recovery,
dependencies and warning fixes. Previous evidence is retained in
[BASELINE_M5.md](BASELINE_M5.md) and `evidence/m1` through `evidence/m5`.
