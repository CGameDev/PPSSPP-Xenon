# HAD-CV M6 checkpoint

Authorization: implement the reviewed navy/teal shell on the same PR; keep both
launcher views and a side-panel in-game menu, preserve save/load/reset/performance,
rebuild both configurations, and perform no Xbox deployment or launch.

Frozen parent: b82bad8848956e55d04933bfb04e9019f9b6ecb0 (M5).
Separate replayable patch: eight presentation bodies plus explicit geometry and
view-offset substitutions; one pure geometry helper. Save-state/session handlers,
header/state, toast lifecycle and all emulation code stay unchanged.

The approved visual direction uses three-by-two grid and six compact rows,
existing fitted embedded art, static shading, and one right-side page at a time.
Original Left/Right switches slot and session pages; default Slot 1 is unchanged.
An opaque pause background avoids introducing an untested framebuffer snapshot
path. The concept's game-details/settings pages remain future work.

Verification: archive/CRC and dependency gates; 20 tests; existing actual-source
regressions; 137 identical action snapshots with explicit expectations; 14 launcher
and 42 menu frames; exact source-boundary check; geometry/input boundary tests;
192 browser scenarios; exact fresh replay across 3,876 files; both full XDK
Rebuilds with zero warnings/errors and all Deploy entries explicitly excluded.
Host drawing/cache costs fall for normal views; small empty/folder glyph exceptions
are bounded and disclosed. Initial host budget failure is retained with its fix.

No console connection/deployment/launch, no actual runtime/performance claim.
Keep PR #2 draft. The existing hardware smoke-test gates remain outstanding.
