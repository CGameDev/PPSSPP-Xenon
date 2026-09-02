# PPSSPP-Xenon — CODEX START HERE

Repository: https://github.com/CGameDev/PPSSPP-Xenon.git

Project name: **PPSSPP Xenon**

Mission: turn the legacy Xbox 360 PPSSPP port into a stable, library-driven, modernized PSP emulator specifically optimized for Xbox 360 Xenon/Xenos hardware, while preserving the working Xbox-specific platform layer and existing game-launcher behavior.

## Read these first

Before making source changes, read completely:

1. `PPSSPP-Xenon-Modernization-Milestone-v1.0.md`
2. `RESEARCH_REFERENCES.md`
3. `PPSSPP-Xenon-Test-Matrix.csv`
4. `source-overlay/README.md`

These documents are authoritative for the initial modernization cycle.

## Non-negotiable rules

1. **Do not wholesale merge current upstream PPSSPP into the Xbox 360 tree.**
   - The Xbox 360 port depends on PowerPC, big-endian behavior, XDK Direct3D 9, XAudio/XInput, legacy compiler compatibility, and an existing PPC JIT.
   - Current PPSSPP is a reference/backport source, not a drop-in replacement.

2. **The user-provided Xbox source overlay in `source-overlay/` is authoritative for same-path Xbox-specific code.**
   - The original uploaded `Xbox.zip` is preserved as four ordered Base64 chunks because the repository-seeding connector could only write text files.
   - Follow `source-overlay/README.md` to reconstruct the ZIP, verify its SHA-256, and extract its `Xbox/` tree.
   - The extracted tree contains newer launcher, ROM-library, in-game-menu, save-state UI, artwork, and game-switching work than the old public fork.
   - Preserve these features unless a change is required to fix a verified bug or architectural issue.

3. **Use the legacy full Xbox 360 port to reconstruct the missing complete source tree.**
   - Reference: https://github.com/metalex10/PPSSPP-X360
   - Preserve original licensing and attribution.
   - Do not overwrite newer same-path Xbox files supplied by the owner overlay.

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

9. **Do not create a Xenon JIT from scratch.**
   - The legacy full source already contains:
     - `Common/ppcEmitter.cpp`
     - `Core/MIPS/PPC/PpcJit.*`
     - PPC register cache
     - PPC ALU/load-store/branch/FPU/VFPU compilation paths
   - First recover, validate, measure, and improve that JIT.

10. **The ROM library is a first-class product feature.**
    - Users must be able to browse local storage, maintain a persistent PSP game library, launch a title, return to the library, and switch to another title without restarting the Xbox application.

## Bootstrap order

1. Clone `CGameDev/PPSSPP-Xenon` and work in this repository permanently.
2. Read all four authoritative project documents listed above.
3. Add the legacy Xbox port as a temporary/reference remote or clone it separately:
   - `legacy-x360 = https://github.com/metalex10/PPSSPP-X360.git`
4. Import the complete legacy source tree into this repository so the missing `Common/`, `Core/`, `GPU/`, `native/`, PPC JIT, Xbox project dependencies, and other required source are present.
5. Preserve the original PPSSPP license and copyright notices.
6. Follow `source-overlay/README.md` exactly:
   - concatenate the four `.b64` chunks in numeric order
   - decode `Xbox-original-upload.zip`
   - verify SHA-256 `6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35`
   - extract it
   - overlay its extracted `Xbox/` tree onto the imported legacy `Xbox/` tree
7. Do not merge `.git` metadata from the legacy repository.
8. Add official PPSSPP as a reference remote:
   - `ppsspp-upstream = https://github.com/hrydgard/ppsspp.git`
9. Fetch/tag `v1.20.4` for source comparison only.
10. Create and maintain:
    - `docs/BASELINE.md`
    - `docs/BACKPORT_LEDGER.md`
    - `docs/COMPATIBILITY.md`
    - `docs/PERFORMANCE.md`
    - plus all other documentation required by the milestone
11. Establish and document an unchanged/near-unchanged legacy + owner-overlay baseline before major modernization.
12. Once the baseline is valid enough to proceed, tag it `xenon-baseline-legacy`.
13. Continue through `PPSSPP-Xenon-Modernization-Milestone-v1.0.md` in dependency order.

## Codex execution policy

Proceed through the milestone in dependency order. Do not stop merely because one phase is large. Keep changes in focused commits and checkpoint after major subsystems.

Do not repeatedly interrupt development for tiny hardware tests. Complete related source-level work first. When real Xbox 360/XDK validation is genuinely required, clearly tell the project owner what build/XEX to run, what game/test to use, what behavior to observe, and what logs/results are needed.

If the Xbox 360 SDK/XDK or physical-console access is unavailable in the current environment, complete all source-level/static work that can safely be done, document the exact hardware validation still required, and continue with independent work rather than guessing test results.

Do not claim hardware validation passed unless it was actually performed.

## First action

Start by reconstructing the complete baseline source and owner-provided Xbox overlay exactly as described above. Then inspect the resulting source tree and begin the modernization milestone.
