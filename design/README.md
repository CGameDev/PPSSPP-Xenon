# CCLOS-style launcher review

M5 adds [the in-game menu preview](cclos-ingame-preview.html), drawn from 42
actual method trace frames with simulated states. Review slot/session focus,
empty/saved slots, two-second notifications and their final half-second fade.
All bindings/order stay: A saves on slots and confirms session actions, X loads,
Y deletes an existing state, B continues. Settings remains unimplemented and is
labelled unavailable. No preview can execute those operations. Its browser check
covers 136 combinations; both original launcher views and their 56 checks remain.
Exact styling and TV readability stay provisional. The native menu/notifications
use the same M4 palette, helpers and font with no new artwork/resource dependency.

Open [cclos-preview.html](cclos-preview.html) for the M4 implementation preview:
grid/compact Games views plus empty, missing-art, long-title/path, folder, Recent
and loading scenarios. These render draw commands from actual staged launcher
methods, captured with host device/cache/input stubs. Geometry/colors/fitted text
match that trace; SVG artwork is fictional and browser font rasterization is
approximate. This is not an Xbox capture, runtime result or final design approval.

Both switchable views were selected by the owner. Games uses RT to switch them,
retaining the selected game. Recent keeps the owner's existing grid policy.
The implemented controls stay A Select / B Exit / LB/RB Tabs / RT Grid/List.
Settings was already inactive and is labelled unavailable; no future feature or
file-format support is implied. Preview controls only select fixtures; no emulator,
console, service or storage action is attached.

The original [M0 concept study](cclos-concept-m0.html) remains for historical
comparison, including future navigation/menu proposals. Its optional smoke check
is tests/preview_smoke.cjs; those broader proposals are not all implemented in M4.

The requested CCLOS_NAND dark navy/teal direction informs this original PPSSPP
adaptation. Canvas #07131f, panels #101e30 / #102c3c, focus #5ce6d0, text #eaf6fa /
#aec7d3. No private CCLOS code, logo, screenshot, wallpaper or asset is published.
Names and geometric artwork are fictional. Browser fonts use system Arial; the
native renderer keeps its existing donor Roboto-Condensed.ttf and stb packing.
No new production asset dependency or generated AI bitmap is introduced.

Review remains open for exact typography, density, focus and TV legibility.
Host tests validate packed glyph quad bounds within 64/36 safe insets, long text,
image aspect ratios, inactive/input paths and bounded draw/cache work. Browser
checks cover 56 combinations across 1280/1920/736/360 px without overflow, page
errors or external requests. Neither certifies TV readability, accessibility or
Xbox frame times; hardware is deliberately deferred.

Regenerate the trace with tests/run_cclos_launcher.py after fresh preparation
(see docs/BUILD_XBOX360.md). Run `node tests/cclos_preview_smoke.cjs` with an
existing Playwright/browser installation for screenshots and browser checks.
Outputs default to ignored artifacts/cclos-preview/. Use the msedge channel and
an existing NODE_PATH on the recorded Windows host. No browser package is vendored.
