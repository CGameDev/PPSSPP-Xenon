# Source and build baseline — M0, 2026-10-21

This is a **recovery checkpoint**, not a known-good emulator baseline or release.
No Xbox 360 runtime test was performed. The tag `xenon-baseline-legacy` has not
been created because the required complete, owner-overlay build does not exist.

## Frozen identities

| Input | Exact identity | Disposition |
| --- | --- | --- |
| Destination main | `a616aa62bbef6102a68a49ed0532dbccb1ea6764` | Clean clone; handoff plus four Base64 parts, no complete emulator tree |
| Legacy donor | `metalex10/PPSSPP-X360@540db97d96136b2139e5f12dd3c0bb18f2e1cd1f` | Separate reference checkout; unchanged source build attempted |
| Modern comparison | `hrydgard/ppsspp`, tag `v1.20.4` | Annotated tag object `3a31057b7e44270b4d5cef8c31b6559d51802a3b`, peeled commit `fa50bb1976065c4f8b1b47af227d367fe9771555`; verified via GitHub; no code imported |
| Owner archive expected | `6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35` | Original documented authority; retained unchanged |
| Owner archive actual | `755ae766ecceb5c3469f765e46de1470fdddbc978ec3c260076f9c2097c907d2` | **FAIL**: 56,233 decoded bytes, 30 ZIP entries; bad CRC in `Xbox/XboxMain.cpp` |

The original PowerShell reconstruction script rejected the archive. An independent
Python decode and CRC check confirmed the failure. The new read-only preflight
records each part's size/hash and checks every ZIP member. ZIP inspection is
diagnostic only: no damaged source was extracted, imported, repaired or compiled.
Git history shows each of the four parts was introduced once, with no earlier
complete, corrected version available in this repository's history.

## Actual build evidence

The PC has Visual Studio 2010 and the Xbox 360 SDK. Observed compiler versions:
XDK `cl.exe` file version `16.00.11886.00`; host VC compiler
`16.00.40219.01` (SP1). These are compiler identities, not a claim that every
installed SDK component shares a particular release version.

The separate legacy checkout was built with .NET Framework 4 MSBuild:

```powershell
$env:XEDK = 'C:\Program Files (x86)\Microsoft Xbox 360 SDK'
& 'C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe' `
  Xbox/PPSSPP.sln /t:Build /p:Configuration=Debug '/p:Platform=Xbox 360' `
  /p:DeployOnBuild=false /p:BuildProjectReferences=false /m:1 /nologo `
  '/flp:logfile=../legacy-debug-build.log;verbosity=minimal' /verbosity:minimal
```

Exit code **1**. `CommonXbox.lib`, `CoreXbox.lib`, `GPUXbox.lib`,
`libkirkXbox.lib` and `zlibXbox.lib` were emitted. PPC emitter/JIT sources compiled.
The front-end link failed with **LNK1181: cannot open input file `avcodec.lib`**.
Both `ffmpeg/Xbox/ppcD/lib/avcodec.lib` and `ffmpeg/Xbox/ppc/lib/avcodec.lib`
are absent. Other missing link dependencies may surface after this first failure.
The legacy version-generation script also reported Git unavailable and generated
an `unknown` version string. The checkout was shallow; the full source commit is
recorded independently above. No source edits were made to achieve these results.

This invocation disables recursive project-reference builds; the solution still
built its listed library projects. It is diagnostic evidence, not a qualified
dependency-ordered clean build. After dependency recovery, use the normal
project-reference behavior and re-establish Debug and Release_LTCG from a clean,
verified full tree. Do not accept the partial libraries as a baseline XEX.

| Gate | Result |
| --- | --- |
| Handoff source identity | PASS |
| Owner archive authenticity / member CRC | FAIL |
| Complete legacy+owner source import | BLOCKED by archive integrity |
| Legacy donor Debug solution build | FAIL at front-end link; partial libraries emitted |
| Owner-overlay Debug / Release_LTCG build | BLOCKED / NOT RUN |
| ISO/CSO/PBP boot, sound, input, savedata, game switching | NOT RUN |
| FPS/VPS, memory, texture lifetime, frame pacing | NOT RUN |
| Baseline XEX size/hash | Unavailable; no XEX produced |

See [M0 evidence](evidence/m0/) and [feasibility](FEASIBILITY.md).

## Recovery condition

Recover the owner's original `Xbox.zip` from a trusted original source. Its bytes
must match the documented expected SHA-256 and pass every member CRC before use.
If the original is lost, a different owner-supplied archive requires an explicit
new provenance/authority record; changing the expected hash to bless these damaged
bytes is not a recovery. Preserve the current parts and failure evidence.
