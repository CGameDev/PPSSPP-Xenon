# Performance evidence

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
