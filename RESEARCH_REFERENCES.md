# PPSSPP Xenon — Research and Reference Ledger

These sources were selected because they are primary/official sources or directly relevant working Xbox 360 code.

## 1. Destination repository

- CGameDev/PPSSPP-Xenon
- https://github.com/CGameDev/PPSSPP-Xenon

At milestone preparation time the repository was empty.

## 2. Legacy Xbox 360 PPSSPP source

- metalex10/PPSSPP-X360
- https://github.com/metalex10/PPSSPP-X360

Why it matters:
- complete Xbox 360-era PPSSPP tree
- Visual Studio/Xbox 360 projects
- DirectX/XDK code
- PowerPC/big-endian support
- native PPC JIT backend
- PPC emitter
- historical Xbox build logs

Important paths:
- `Common/ppcEmitter.cpp`
- `Core/MIPS/PPC/`
- `Core/CoreXbox.vcxproj`
- `Xbox/PPSSPP.sln`

The source-overlay in this package takes precedence for files under `Xbox/`.

## 3. Official modern PPSSPP

- hrydgard/ppsspp
- https://github.com/hrydgard/ppsspp
- fixed reference tag for milestone v1.0: `v1.20.4`

Why it matters:
- current PSP emulation correctness
- current HLE fixes
- modern MIPS/JIT architecture
- current game browser
- current GameInfoCache
- current game lifecycle/shutdown behavior
- modern ISO/CSO/CHD behavior

Useful paths/concepts:
- `UI/GameBrowser.cpp`
- `UI/GameBrowser.h`
- `UI/GameInfoCache.cpp`
- `UI/GameInfoCache.h`
- `UI/MainScreen.cpp`
- `UI/EmuScreen.cpp`
- `Core/System.cpp`
- `Core/MIPS/`
- `GPU/Common/`

Important rule:
Do not merge this repository wholesale into the Xbox tree. Use it to identify and backport narrowly scoped fixes.

## 4. Official PSP autotests

- hrydgard/pspautotests
- https://github.com/hrydgard/pspautotests

Why it matters:
- PSP behavioral tests used by emulator development
- CPU/FPU/VFPU/HLE correctness work
- safer validation than relying only on commercial games

## 5. PPSSPP game-loading/library documentation

Official PPSSPP documentation:
- https://www.ppsspp.org/docs/getting-started/how-to-get-games/

Relevant behavior:
- game browser navigates local files/folders
- PSP game images are user-provided
- ISO is a standard game-image path
- library behavior should be local-first and not depend on a ROM download service

## 6. Modern CHD support

Current PPSSPP history documents full CHD support in modern versions.

For PPSSPP Xenon this is a useful future reference, but CHD must not be forced into the first Xbox milestone if dependencies or decompression cost are unsuitable for the XDK/Xenon environment.

## Source trust policy

Preferred:
1. official PPSSPP repository
2. official PSP autotests
3. known working Xbox 360 PPSSPP source
4. Xbox SDK/XDK documentation available in the developer's licensed environment

Do not copy random emulator patches solely because a fork claims higher FPS.

Any third-party patch must:
- have inspectable source
- have a compatible license
- solve a demonstrated issue
- be measured on Xbox 360
- be reversible
- be documented in `BACKPORT_LEDGER.md`
