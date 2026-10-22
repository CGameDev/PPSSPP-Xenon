# Performance evidence

M1 builds exist, but Xbox performance remains NOT RUN. Dependency restoration and
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
