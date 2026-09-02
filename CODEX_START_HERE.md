# PPSSPP-Xenon — CODEX START HERE

Repository: https://github.com/CGameDev/PPSSPP-Xenon.git

Project name: **PPSSPP Xenon**

Mission: turn the legacy Xbox 360 PPSSPP port into a stable, library-driven, modernized PSP emulator specifically optimized for Xbox 360 Xenon/Xenos hardware, while preserving the working Xbox-specific platform layer and existing game-launcher behavior.

## Non-negotiable rules

1. **Do not wholesale merge current upstream PPSSPP into the Xbox 360 tree.**
   - The Xbox 360 port depends on PowerPC, big-endian behavior, XDK Direct3D 9, XAudio/XInput, legacy compiler compatibility, and an existing PPC JIT.
   - Current PPSSPP is a reference/backport source, not a drop-in replacement.

2. **The `source-overlay/Xbox/` folder in this package is authoritative for Xbox-specific code.**
   - It contains newer launcher, ROM-library, in-game-menu, save-state UI, artwork, and game-switching work than the old public fork.
   - Preserve these features unless a change is required to fix a verified bug or architectural issue.

3. **Use the legacy full Xbox 360 port only to reconstruct the missing complete source tree.**
   - Reference: https://github.com/metalex10/PPSSPP-X360
   - Preserve original licensing and attribution.
   - Do not overwrite newer files from `source-overlay/Xbox/`.

4. **Use official PPSSPP v1.20.4 as the fixed modern reference baseline for the first modernization cycle.**
   - Reference: https://github.com/hrydgard/ppsspp
   - Tag: `v1.20.4`
   - Do not chase moving `master` during this milestone.

5. **Use official PSP autotests for CPU/HLE correctness work.**
   - Reference: https://github.com/hrydgard/pspautotests

6. **No ROMs, ISOs, CSOs, commercial game data, BIOS files, keys, or copyrighted game assets are to be committed to this repository.**
   - Testing uses homebrew/tests plus user-owned dumps supplied outside Git.

7. **Do not remove a working compatibility path just to make code cleaner.**
   - Correctness and Xbox 360 stability outrank architectural elegance.

8. **Every upstream backport must be traceable.**
   - Record source repository, source tag/commit when known, files/subsystem affected, reason, Xbox adaptations, and test result in `docs/BACKPORT_LEDGER.md`.

9. **Do not assume a JIT must be created from scratch.**
   - The legacy full source already contains:
     - `Common/ppcEmitter.cpp`
     - `Core/MIPS/PPC/PpcJit.*`
     - PPC register cache
     - PPC ALU/load-store/branch/FPU/VFPU compilation paths
   - First recover, validate, measure, and improve that JIT.

10. **The ROM library is a first-class product feature.**
    - Users must be able to browse local storage, maintain a persistent PSP game library, launch a title, return to the library, and switch to another title without restarting the Xbox application.

## Bootstrap order

Because `CGameDev/PPSSPP-Xenon` was empty when this milestone was prepared:

1. Clone `CGameDev/PPSSPP-Xenon`.
2. Add the legacy Xbox port as a temporary/reference remote:
   - `legacy-x360 = https://github.com/metalex10/PPSSPP-X360.git`
3. Import the complete legacy source tree into the new repository.
4. Preserve the original PPSSPP license and copyright notices.
5. Overlay every file from this package's `source-overlay/Xbox/` onto the imported `Xbox/` tree.
6. Do not merge `.git` metadata from the legacy repository.
7. Add official PPSSPP as a reference remote:
   - `ppsspp-upstream = https://github.com/hrydgard/ppsspp.git`
8. Fetch/tag `v1.20.4` for source comparison only.
9. Create:
   - `docs/BASELINE.md`
   - `docs/BACKPORT_LEDGER.md`
   - `docs/COMPATIBILITY.md`
   - `docs/PERFORMANCE.md`
10. Build an unchanged baseline before modernization.
11. Tag the imported, building baseline:
   - `xenon-baseline-legacy`

## Codex execution policy

Proceed through the milestone in dependency order. Do not stop merely because one phase is large. Keep changes in focused commits and checkpoint after major subsystems. If the Xbox 360 SDK/XDK or physical-console access is unavailable in the current environment, complete all source-level work that can be validated statically, document the exact hardware test required, and continue with independent work rather than guessing test results.

Start with `PPSSPP-Xenon-Modernization-Milestone-v1.0.md`.
