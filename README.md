# PPSSPP Xenon

**PPSSPP Xenon** is an Xbox 360 / Xenon modernization project based on the legacy Xbox 360 port of PPSSPP.

The project goal is to preserve the working Xbox 360 platform implementation while improving PSP compatibility, performance, stability, game-library usability, and game switching specifically for Xenon PowerPC and Xenos hardware.

## Codex / development bootstrap

**Start here:** [`CODEX_START_HERE.md`](CODEX_START_HERE.md)

Then read:

- [`PPSSPP-Xenon-Modernization-Milestone-v1.0.md`](PPSSPP-Xenon-Modernization-Milestone-v1.0.md)
- [`RESEARCH_REFERENCES.md`](RESEARCH_REFERENCES.md)
- [`PPSSPP-Xenon-Test-Matrix.csv`](PPSSPP-Xenon-Test-Matrix.csv)
- [`source-overlay/README.md`](source-overlay/README.md)
- [`REUPLOAD_VERIFICATION_2026-09-03.md`](REUPLOAD_VERIFICATION_2026-09-03.md)

The owner-provided Xbox source overlay is preserved under `source-overlay/` and includes automatic reconstruction/integrity-check scripts.

Windows / PowerShell:

```powershell
& .\source-overlay\reconstruct.ps1
```

Linux / shell:

```bash
bash source-overlay/reconstruct.sh
```

The reconstructed owner source must match SHA-256:

`6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35`

The GitHub repository itself is the authoritative Codex handoff; a separate chat attachment is not required.

## Primary targets

- Xbox 360 Xenon PowerPC optimization
- validation and improvement of the existing MIPS → PPC JIT
- Xenos / XDK Direct3D 9 optimization
- persistent PSP ROM/game library
- ISO, CSO and PSP homebrew/PBP support
- embedded PSP metadata and artwork
- Recent / All Games / Favorites / Folders views
- clean return-to-library and in-process game switching
- per-game compatibility/performance settings
- selective, documented backports from modern PPSSPP
- reproducible Xbox 360 build and hardware test matrix

## Upstream/reference projects

- PPSSPP: https://github.com/hrydgard/ppsspp
- PSP autotests: https://github.com/hrydgard/pspautotests
- Legacy Xbox 360 port: https://github.com/metalex10/PPSSPP-X360

This repository must retain applicable PPSSPP/upstream licensing and attribution when the legacy source tree is imported.

No commercial PSP ROMs, ISOs, CSOs, copyrighted game assets, BIOS files, or keys belong in this repository.
