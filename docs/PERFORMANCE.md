# Performance evidence

M6 implements the approved shell with static rectangles and cached fitted artwork.
Against M5, normal grid/compact calls fall 80→62 / 64→56; triangles 636→584 /
562→554; artwork lookups 13→7 / 9→7. Save-slot/session menu calls fall 47→30 /
47→25, triangles 518→480 / 518→462. No launcher fixture increases draw/cache/
descriptor counts. Empty-folder captions add at most 24 triangles and compact
folder captions six; these glyph-only exceptions are tested. Notifications and
inactive guards remain exact. No emulator/session/resource-policy code changes.
There is no blur, framebuffer capture, animation or new texture. The side-panel
backdrop is deliberately opaque/static. All counts are host evidence; Xbox frame
times and performance equivalence remain NOT RUN. See evidence/m6 and BASELINE.md.

M5 changes only the menu and toast drawing bodies. Normal menu host draw calls fall 127→47 (with active notification 129→49); triangles 778→518. With no atlas, the old menu drew 26 calls versus 47 now, while triangles still fall 576→518. Visible notifications keep two draws and normal 28 triangles; a deliberately long fixture uses 130 versus 128 triangles because fitted ellipsis can add a glyph. Five existing save-presence queries remain; no new artwork/scan/decode/resource policy. Inactive paths do no work. Core/session code and both launcher traces exactly match M4. These are bounded host counts, not Xbox frame-time measurements.

M4 replaces the launcher-only animated shell with static panels and limits visible cards/rows. Same 14-title fixture: host draw calls grid 153→80, compact 157→64; triangles 740→636 / 632→562; artwork lookups 15→13 / 11→9. These count actual method traces with stubbed drawing/cache; they are not frame times or GPU measurements. Existing in-game/IGM code is unchanged. No new resources, cache policy, persistence, shader or emulation tuning is introduced. See evidence/m4/launcher-receipt.json. Xbox performance remains NOT RUN.

M3 fully rebuilds both configurations warning-clean and preserves GPU/cache layouts, but Xbox performance remains NOT RUN. Dependency restoration and
the recorded launcher/build adapters do not change CPU clock/worker/JIT/GPU/audio
tuning. Do not infer performance equivalence from build success. The following
M0 measurement plan remains the acceptance basis.

No Xbox performance measurements exist for M0. No improvement, 60 FPS, active JIT,
memory stability or regression-free runtime claim is made. No production emulator
source, worker count, PSP clock, JIT, audio or GPU path changes are included.

After the trusted baseline builds, record the exact XEX/source/resources, output
mode, title/test identity and scene, CPU backend, emulated FPS/VPS, median/p95/max
frame interval, audio underruns, process/texture/cache high-water marks and switch
latency. Use identical settings and scenes across baseline/candidate. Record at
least twenty session transitions plus cache-stabilized memory observations.
Retain outliers and failing evidence. Browser mockup rendering is host-only and
cannot substitute for these measurements.

UI integration must bound artwork residency, release textures deterministically,
reuse the existing session model and avoid scan/decode/network work on the render
or controller path. Measure the added UI cost before selecting any optimization.
