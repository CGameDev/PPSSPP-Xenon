# Reproduce the recovered Xbox 360 build

Read [BASELINE.md](BASELINE.md) for identities, limitations and retained warnings. This procedure builds local files. The original XDK project automatically deploys after image generation unless its Deploy metadata is excluded.

## Verify and stage

Use Python 3 and Git. The legacy checkout must be at `metalex10/PPSSPP-X360@540db97d96136b2139e5f12dd3c0bb18f2e1cd1f`. Committed objects are imported, never its working-tree changes. A fresh destination is required.

```powershell
python tools/verify_source_overlay.py
python -m unittest discover -s tests -v
python tools/prepare_baseline.py --legacy <legacy-checkout> `
  --destination artifacts/baseline-m1 --with-build-compatibility
```

Compatibility mode stages beneath this project. It records the pristine source manifest, applies the two tracked patches, copies the licensed font header/helper and writes combined provenance. The original archival overlay remains unchanged.

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
  --source artifacts/baseline-m1/ffmpeg --build artifacts/ffmpeg-debug `
  --make <make-source>/WinRel/gnumake.exe --c99 <c99-tools-directory> `
  --xdk 'C:/Program Files (x86)/Microsoft Xbox 360 SDK' `
  --bash 'C:/Program Files/Git/bin/bash.exe' --configuration Debug

python tools/build_xbox_ffmpeg.py `
  --source artifacts/baseline-m1/ffmpeg --build artifacts/ffmpeg-release `
  --make <make-source>/WinRel/gnumake.exe --c99 <c99-tools-directory> `
  --xdk 'C:/Program Files (x86)/Microsoft Xbox 360 SDK' `
  --bash 'C:/Program Files/Git/bin/bash.exe' --configuration Release
```

The driver verifies pinned FFmpeg source hashes, derives arguments from existing Xbox recipes, places XDK compiler/linker ahead of Unix tools, validates PPC/32-bit/big-endian configuration and checks every archive object. Logs and BUILD_RECEIPT.json stay in each build directory. All six `.lib` files go to ffmpeg/Xbox/ppcD/lib or ffmpeg/Xbox/ppc/lib. It does not run old install/clean scripts.

Native Makefiles use Windows source paths. The old MSVC dependency scanner is bypassed because of its native Make/modern Git Bash quoting incompatibility. **Header changes require fresh FFmpeg build directories.** `--resume` is allowed only when existing configuration arguments match the recipe exactly; it does not replace clean builds after header changes. Both profiles were exercised with this driver against completed M1 builds.

## Build local XEX files

```powershell
./tools/build_baseline.ps1 -SourceRoot artifacts/baseline-m1 -Configuration Debug
./tools/build_baseline.ps1 -SourceRoot artifacts/baseline-m1 -Configuration Release_LTCG
```

The driver checks every project deployment exclusion and all six library architectures before MSBuild with normal project references. It requests Build only. Do not invoke Deploy or launch an XEX as part of this procedure.

Outputs: Xbox/xx/Debug/xx.xex and Xbox/xx/Release_LTCG/xx.xex. They require matching application assets and runtime verification before use. Record hashes after every rebuild; timestamps and embedded paths may differ.

Compile tests/state_delete_compat.cpp with VS2010 or a C++98-capable host compiler and run it in a fresh disposable folder. Never run its fixed fixture filenames in an owner savedata directory. CI uses artifacts/state-delete-test.
