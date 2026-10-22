# Compatibility evidence

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
