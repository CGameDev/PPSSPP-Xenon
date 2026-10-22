# CCLOS-style launcher design review

Open [cclos-preview.html](cclos-preview.html) in a browser. It has four local scenes:
tile library, compact library, in-game menu and empty library. No service, emulator,
filesystem mutation or network dependency is involved. The preview action buttons
only update their explanatory status. Navigation tabs show proposed states and do
not filter a real library. Mouse/keyboard use is a browser preview, not Xbox input
testing. Both grid and compact views were selected by the owner in this chat on
2026-10-21; keep them switchable. Other design details remain provisional.

## Visual direction and provenance

The requested dark navy/teal CCLOS_NAND aesthetic and the locally inspected owner
Home reference inform the canvas, restrained panel borders, bright focus and
header/footer hierarchy. This is an original PPSSPP adaptation, not a pixel-exact
CCLOS copy or a claim that this whole emulator design is approved. No CCLOS_NAND
code, screenshot, wallpaper, logo or private asset is published here.

All names and artwork in this preview are fictional fixtures. Simple geometric
art is authored in CSS. ISO/CSO/PBP badges illustrate proposed metadata fields;
they do not certify launch support. There are no FPS counters, fake compatibility
scores or invented runtime measurements. No generated AI bitmap is required.

Provisional palette: canvas `#07131f`, secondary navy `#101e30`, panels `#102c3c`,
focus teal `#5ce6d0`, primary text `#eaf6fa`, secondary text `#aec7d3`.
System Segoe UI/Arial fonts are referenced, not redistributed. Any eventual XDK
font assets need their own format, license and renderer qualification.

## Review and acceptance before implementation

- Retain shared navigation/selection between both library views.
- Confirm focus treatment, game-detail density, artwork ratio and menu order.
- Establish native 1280×720 geometry, overscan-safe insets and legible TV text;
  small fixture labels in the browser are not locked Xbox font metrics.
- Exercise missing/corrupt artwork, removed USB root, empty/loading/error states,
  long titles/paths and save/load/reset/return confirmations.
- Preserve existing behavior and test measured performance on the actual renderer.

Browser checks cover four scenes at 1280, 1920, 736 and 360 px, scene changes,
selection updates, mock actions, navigation and absence of external requests.
They are functional/layout smoke checks, not accessibility certification or TV
readability acceptance. Native captures and owner design review are still needed.

To repeat the optional browser smoke check in an environment with Playwright
1.62.1 and its browser available, run `node tests/preview_smoke.cjs`. On this
Windows host it used the installed Edge channel with
`PREVIEW_BROWSER_CHANNEL=msedge`; set `NODE_PATH` to an existing package location
if needed. It writes only preview screenshots and a JSON report to
`artifacts/preview/`, or the output directory supplied as its first argument.
This optional check is separate from the dependency-free Python CI gate.
