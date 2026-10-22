# Reproduce the recovered Xbox 360 build

Current checkpoint: **M6 approved shell**. Use `artifacts/baseline-m6` for all
current examples below. Preparation now applies seven patches and copies four
helpers. The current launcher/menu runners reverse only the M6 patch to recover
M5 for differential checks. Older M4/M5 sections below explain those historical
milestones; current acceptance commands are in [TESTING.md](TESTING.md).

```powershell
python tools/prepare_baseline.py --legacy <legacy-checkout> --destination artifacts/baseline-m6 --with-build-compatibility
# Restore the verified FFmpeg profiles using the procedure below, or reuse all
# twelve previously verified libraries only after byte/architecture checks.
./tools/build_baseline.ps1 -SourceRoot artifacts/baseline-m6 -Configuration Debug -Rebuild
./tools/build_baseline.ps1 -SourceRoot artifacts/baseline-m6 -Configuration Release_LTCG -Rebuild
python tests/run_cclos_shell.py --source-root artifacts/baseline-m6 --build-root artifacts/cclos-shell-tests
```

Both builds request no deployment/launch target; all four Deploy entries must
remain explicitly excluded. The M6 local evidence is under `docs/evidence/m6/`.

Read [BASELINE.md](BASELINE.md) for identities, limitations and retained warnings. This procedure builds local files. The original XDK project automatically deploys after image generation unless its Deploy metadata is excluded.

## Verify and stage

Use Python 3 and Git. The legacy checkout must be at `metalex10/PPSSPP-X360@540db97d96136b2139e5f12dd3c0bb18f2e1cd1f`. Committed objects are imported, never its working-tree changes. A fresh destination is required.

```powershell
python tools/verify_source_overlay.py
python -m unittest discover -s tests -v
python tools/prepare_baseline.py --legacy <legacy-checkout> `
  --destination artifacts/baseline-m5 --with-build-compatibility
```

Compatibility mode stages beneath this project. It records the pristine source manifest, applies the seven tracked patches, copies the licensed font header and four launcher/session helpers and writes combined provenance. The original archival overlay remains unchanged.

## Local host tools

Use the installed licensed VS2010/XDK. No SDK content is downloaded or redistributed. Exact host-tool hashes are in `evidence/m1/host-tool-provenance.json`.

- GNU Make source: https://ftp.gnu.org/gnu/make/make-3.82.tar.gz
- C99 wrapper/converter: https://github.com/libav/c99-to-c89/releases/tag/release-1.0.2
- Existing Git for Windows Bash.

Extract tools into task-owned staging. For GNU Make, copy config.h.W32 to config.h, enable HAVE_CYGWIN_SHELL there, enter the VS2010 x86 tools environment, add the Make source root to INCLUDE, and run build_w32.bat. The extra include directory fixes its historical subproc config.h search. M1 used WinRel/gnumake.exe. This is a host tool, not an emulator dependency. GNU Make 4.4.1 failed with the old compiler and is not used.

## Build Xbox FFmpeg

Use source/build staging paths without spaces; SDK/Bash installation paths may contain spaces. Supply verified tool locations. Run Debug and Release in separate fresh directories:

```powershell
python tools/build_xbox_ffmpeg.py `
  --source artifacts/baseline-m5/ffmpeg --build artifacts/ffmpeg-debug `
  --make <make-source>/WinRel/gnumake.exe --c99 <c99-tools-directory> `
  --xdk 'C:/Program Files (x86)/Microsoft Xbox 360 SDK' `
  --bash 'C:/Program Files/Git/bin/bash.exe' --configuration Debug

python tools/build_xbox_ffmpeg.py `
  --source artifacts/baseline-m5/ffmpeg --build artifacts/ffmpeg-release `
  --make <make-source>/WinRel/gnumake.exe --c99 <c99-tools-directory> `
  --xdk 'C:/Program Files (x86)/Microsoft Xbox 360 SDK' `
  --bash 'C:/Program Files/Git/bin/bash.exe' --configuration Release
```

The driver verifies pinned FFmpeg source hashes, derives arguments from existing Xbox recipes, places XDK compiler/linker ahead of Unix tools, validates PPC/32-bit/big-endian configuration and checks every archive object. Logs and BUILD_RECEIPT.json stay in each build directory. All six `.lib` files go to ffmpeg/Xbox/ppcD/lib or ffmpeg/Xbox/ppc/lib. It does not run old install/clean scripts.

Native Makefiles use Windows source paths. The old MSVC dependency scanner is bypassed because of its native Make/modern Git Bash quoting incompatibility. **Header changes require fresh FFmpeg build directories.** `--resume` is allowed only when existing configuration arguments match the recipe exactly; it does not replace clean builds after header changes. Both profiles were exercised with this driver against completed M1 builds.

## Build local XEX files

```powershell
./tools/build_baseline.ps1 -SourceRoot artifacts/baseline-m5 -Configuration Debug -Rebuild
./tools/build_baseline.ps1 -SourceRoot artifacts/baseline-m5 -Configuration Release_LTCG -Rebuild
```

The driver checks every project deployment exclusion and all six library architectures before MSBuild with normal project references. It requests Build or, with -Rebuild, a full Rebuild. Do not invoke Deploy or launch an XEX as part of this procedure.

Outputs: Xbox/xx/Debug/xx.xex and Xbox/xx/Release_LTCG/xx.xex. They require matching application assets and runtime verification before use. Record hashes after every rebuild; timestamps and embedded paths may differ.

Compile tests/state_delete_compat.cpp with VS2010 or a C++98-capable host compiler and run it in a fresh disposable folder. Never run its fixed fixture filenames in an owner savedata directory. CI uses artifacts/state-delete-test.

## M3 warning validation

M3 reuses the twelve previously built FFmpeg libraries byte-for-byte after architecture/hash
checks; no FFmpeg header/source changed. The examples above can instead rebuild
FFmpeg from its pinned source when reproducing from an empty environment.

Run `python -m unittest discover -s tests -v` in a VS2010 host developer environment
(or with g++ on Linux). The actual owner loader functions are reconstructed,
patched, extracted and compiled under C++98 with warnings as errors, then exercised
with host texture/decoder stubs. This never launches an Xbox executable. Confirm
that no test is skipped in the acceptance environment.

For compile-only ABI checks, set INCLUDE to the licensed XDK include/xbox and
include/xbox/sys directories, then invoke its bin/win32/cl.exe with /c /W3 /WX,
/D_XBOX /DPPC /DBIG_ENDIAN /DEXPECT_ALIGNED_GLOBALS, /I<staging>,
/I<staging>/Common and /I<staging>/native on tests/gpu_layout_probe.cpp. Use
/D_DEBUG /MTd for Debug or /DNDEBUG /MT for Release_LTCG, and put /Fo output under
ignored artifacts. M1 comparison omits EXPECT_ALIGNED_GLOBALS and uses M1 source.
These are compile-only assertions, with no link or console execution.

Audit each final log with `python tools/audit_build_warnings.py <log>`.
Every final audit must have total=0 and agree with MSBuild 0 Warning(s).
Read WARNING_REVIEW_M3.md and preserve any failed logs.

Run the added source-derived regressions after preparation:

```powershell
python tests/run_m3_regressions.py --source-root artifacts/baseline-m5 `
  --reference-root <pinned-legacy-checkout> --build-root artifacts/m3-host-regressions
```

Use the VS2010 x86 host tools environment locally; CI uses g++ with the pinned
public legacy checkout. Reference inputs use unchanged donor emitter/morph/hash
code. The script executes host fixtures and emitter word generators, never Xbox
machine code. Native Windows SEH is tested with host RaiseException; GCC's stub
case checks control flow and does not claim native SEH. Current fixtures treat
warnings as errors; old negative/differential controls retain expected warnings.
Emitter fixtures use the real /W3 setting; other new MSVC fixtures use /W4.

Keep enough free local storage for full compiler/link intermediates. After a
space failure, preserve sources/evidence and only remove verified task-generated
intermediates in obsolete staging roots; never delete owner source or SDK files.
Repeat both full rebuilds before recording accepted hashes.

## M4 launcher validation and previews

After staging, run the actual launcher methods with host drawing/input/cache stubs:

```powershell
python tests/run_cclos_launcher.py --source-root artifacts/baseline-m5 `
  --build-root artifacts/cclos-launcher-tests --preview-data design/cclos-launcher-frames.js
```

This recovers the preceding launcher by reversing only the M4 patch in a disposable
reference folder. An explicit `--reference-root` can instead select a retained M3
stage. Both use the same donor font packed at 20 px / 2x oversampling. Assertions
cover packed glyph bounds, fitting, both view layouts and input contracts; real
Xbox machine code, storage or input devices are never executed. Source-derived
M3 regressions above also run against the M4 stage.

Open design/cclos-preview.html for the trace-driven provisional review. With
Playwright installed, `node tests/cclos_preview_smoke.cjs` checks 56 scene/view/
viewport combinations and writes screenshots under ignored artifacts. Set
PREVIEW_BROWSER_CHANNEL=msedge and NODE_PATH to an existing Playwright package
when using installed Edge on Windows. The older concept study and its smoke
check remain at design/cclos-concept-m0.html / tests/preview_smoke.cjs.

The MSVC host tracer uses the desktop CRT's standard non-deprecation macro for
existing bounded sprintf usage. Only the unchanged owner's animated-background
method has a desktop-only C4244 diagnostic bracket while compiling the fixture;
this adds no production warning suppression or project warning-policy change.
New presentation methods remain under /W3 /WX (GCC -Wall -Wextra
-Werror). This host compatibility handling does not alter the rendered source.
The historical comparison source retains its diagnostics without warnings as
errors: GCC reports three unused variables in those old presentation methods.
The initial CI reference-compile failure is preserved in M4 evidence; current
launcher code compiled cleanly in that run and keeps its strict warning policy.

## M5 in-game menu validation

```powershell
python tests/run_cclos_ingame.py --source-root artifacts/baseline-m5 `
  --build-root artifacts/cclos-ingame-tests --preview-data design/cclos-ingame-frames.js
```

The host runner copies only required comparison files, reverses the M5 patch
there to recover M4, and compiles actual drawing/action methods. Save/load/delete
services are string/counter stubs; no real state or console is touched. All 137
action snapshots must equal M4 and explicit expected requests. It checks 42
presentation frames, five existing presence queries, inactive early returns,
packed glyph bounds and notification timing/fading. Existing launcher and M3
regressions also run against M5. Native code is unchanged outside two drawing
functions. The M3 launcher comparison reverses M5 before M4 to retain its exact
historical reference.

Open design/cclos-ingame-preview.html for review. With the same optional browser
setup, `node tests/cclos_ingame_preview_smoke.cjs` checks 136 combinations. The
launcher preview's 56 checks still pass. These SVG previews approximate font
rasterization and simulate states; they never execute real save/reset actions.
Read CONSOLE_TEST_READINESS.md before any future hardware checkpoint. Local
build ZIPs contain XEX/evidence, not runtime assets, flash0, ROMs or user data.
