# Compatibility evidence

M5 retains exact input/action/session code and compares 137 host action snapshots with M4, plus explicit request expectations. SaveState services are stubs: actual serialization, recovery and Xbox resets are NOT RUN. Both launcher traces stay identical and both full local builds are warning-clean. See CONSOLE_TEST_READINESS.md.

M4 host traces exercise both launcher views and existing input requests with stubs. Core/session/IGM paths stay unchanged from M3. Both full local builds remain warning-clean. All Xbox compatibility rows still remain NOT RUN; no console actions were taken.

M1 recovers the owner source and builds Debug/Release_LTCG. No Xbox runtime result
exists; every hardware row in the test matrix remains NOT RUN. Host file-helper
tests and library object/header checks do not certify JIT/codec behavior, loading,
audio/input, savedata, states or game switching. M3 resolves the remaining diagnostics and both builds are warning-clean. Host
normal-math/session checks and target layouts do not establish Xbox behavior. The M0 record below is historical; its archive blocker is now resolved.

M0 has no verified Xbox runtime compatibility results. All hardware rows in
`PPSSPP-Xenon-Test-Matrix.csv` remain NOT RUN. The damaged owner source prevents
reconstruction of its claimed launcher/session behavior. A compiled legacy Core
library does not establish CPU/JIT correctness or successful game loading.

Use official PSP autotests/homebrew and locally supplied owner dumps outside Git.
Record exact test revision, CPU interpreter/JIT mode, settings, content identity,
expected/actual result and console logs per case. Verify ISO, CSO and supported
PBP loading through the actual core before advertising support in the launcher.
Do not label ZIP/RAR or unimplemented CHD paths directly playable. Validate savedata,
states, reset, failed-launch recovery and game switching before any release.
