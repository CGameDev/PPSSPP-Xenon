# PPSSPP Xenon Modernization Milestone v1.0

**Target repository:** `CGameDev/PPSSPP-Xenon`  
**Target platform:** Xbox 360 / Xenon PowerPC / Xenos GPU  
**Legacy base:** PPSSPP Xbox 360 port derived from the 0.9.x era  
**Modern reference:** Official PPSSPP `v1.20.4`  
**Primary objective:** significantly improve compatibility, performance, stability, and usability without breaking the Xbox 360-specific platform layer.

---

# 0. Project outcome

PPSSPP Xenon must behave like a real console emulator rather than a single-ROM launcher.

The expected user flow is:

```text
Start PPSSPP Xenon
        ↓
Persistent PSP Library
        ↓
Select Game
        ↓
Launch PSP Session
        ↓
Play
        ↓
Open In-Game Menu
        ↓
Return to Library
        ↓
Select Different Game
        ↓
Clean PSP Shutdown
        ↓
Clean PSP Init(new game)
        ↓
Play
```

The Xbox application, D3D device, launcher, and high-level shell should remain resident while PSP emulation sessions are safely created and destroyed.

---

# 1. Current Xbox overlay — preserve and improve

The supplied Xbox source already implements substantial emulator-shell functionality.

## Existing functionality discovered

`XboxLauncher.cpp` already contains:

- device and directory navigation
- ISO/CSO title reading through PSP `PARAM.SFO`
- ISO artwork extraction
- `ICON0.PNG`
- `PIC1.PNG`
- grid/list rendering
- Recent Games
- persisted `recent.txt`
- storage enumeration for `hdd1:` and `usb0:` through `usb9:`
- game-selection flow
- in-game menu
- save-state slots
- reset-game request
- exit-to-library request
- exit-to-Xbox request
- toast notifications

`XboxMain.cpp` already contains a persistent launcher/emulator loop capable of:

- launching a selected game
- returning to the launcher
- shutting down the current PSP instance
- starting another PSP game without restarting the entire Xbox application
- resetting the current game

This architecture is valuable and MUST NOT be replaced with a one-ROM-at-boot design.

---

# 2. Known issues in the supplied launcher that must be addressed

## 2.1 Search directories are persisted but not actually used as a library

The launcher has `searchDirs_`, `SaveSearchDirs()`, `LoadSearchDirs()`, and `BrowseDirectories()`, but saved roots are not used to build an aggregated persistent game library.

### Required fix

Create a proper library scanner that:

- accepts multiple user-selected roots
- recursively scans those roots
- merges results into one library
- deduplicates by canonical path
- persists scan metadata
- updates only changed files/folders when possible
- never performs a slow full-device scan every boot

Suggested design:

```text
Configured Library Roots
   ├─ Hdd1:\PSP\
   ├─ Usb0:\PSP\
   └─ Usb1:\Games\PSP\
             ↓
       Background/Incremental Scan
             ↓
         Library Index
             ↓
     Game Browser / Recent / Favorites
```

Do not scan every directory on every mounted device unless the user explicitly requests it.

## 2.2 `BrowseDirectories()` is placeholder behavior

The current implementation effectively adds the first discovered subdirectory rather than providing a real selectable folder workflow.

Replace it with a controller-driven folder picker using the existing launcher visual language.

Required controls:

- D-pad / left stick: navigate
- A: enter/select
- B: go back
- X: choose current directory as a library root
- Y: remove selected library root where appropriate

## 2.3 Game-file classification is inaccurate

The current launcher treats:

- `.iso`
- `.cso`
- `.zip`
- `.rar`

as equivalent game files.

Correct this.

### Mandatory playable formats

- `.iso`
- `.cso`
- `EBOOT.PBP` / supported PSP homebrew PBP path

### Archive/import formats

ZIP must not be presented as directly playable unless the core genuinely supports that exact path. If install/import functionality is retained, label it separately.

RAR must not be advertised as directly playable without a verified decoder/import path.

### Optional later format

Current PPSSPP supports CHD. CHD is desirable for PPSSPP Xenon but is **not required for the first stable library implementation**. Only add it after its required loader/decompression dependencies are proven to compile and perform acceptably with the Xbox 360/XDK toolchain.

## 2.4 CSO artwork path must be fixed

The supplied launcher reads game titles through the emulator's block-device/ISO filesystem abstraction, which can handle compressed images, but its custom artwork helper explicitly refuses `CISO`.

Refactor metadata/artwork extraction to use one shared PSP image abstraction wherever practical.

Target:

```text
ISO / CSO / future CHD
       ↓
 PSP Block Device
       ↓
 ISO FileSystem
       ↓
 PSP_GAME/
   ├─ PARAM.SFO
   ├─ ICON0.PNG
   └─ PIC1.PNG
```

Do not maintain two competing parsing implementations unless unavoidable.

## 2.5 Potential D3D texture-cache leak

The current `ScanDirs()` clears `iconCache_` without first releasing cached `IDirect3DTexture9*` objects.

Audit all launcher texture caches:

- `iconCache_`
- `posterCache_`
- unknown/fallback art
- atlas resources
- game-switch resources

Every COM-owned texture must have deterministic ownership and `Release()` behavior.

Add debug counters for:

- cached icons
- cached posters
- estimated texture bytes
- created textures
- released textures

A library rescan must not leak GPU memory.

## 2.6 In-game Settings is currently TODO

Implement the Settings entry or explicitly disable it until implemented. Never leave a menu item that silently closes the menu.

---

# 3. Milestone A — Baseline recovery and reproducible build

## Goal

Establish a known-good full source tree before modernizing.

## Tasks

- reconstruct complete source from the legacy Xbox 360 fork
- overlay the supplied `Xbox/` source
- build the existing solution using the intended Xbox 360 XDK / Visual Studio 2010-era toolchain
- prefer `Release_LTCG|Xbox 360` for performance validation after Debug/Profile validation
- document compiler, XDK version, configuration, and required external assets
- capture a baseline XEX size
- capture a baseline memory-use snapshot
- confirm ISO boot
- confirm CSO boot
- confirm sound
- confirm controller
- confirm save data
- confirm return-to-library
- confirm selecting a second game

## Required checkpoint

Do not begin large core backports until an unchanged/near-unchanged baseline has been demonstrated to build or every blocking build problem is precisely documented.

---

# 4. Milestone B — Instrumentation before optimization

## Goal

Never optimize blind.

Add a developer performance overlay or log mode that can report:

- active CPU core: PPC JIT vs interpreter
- emulated FPS
- VPS/emulation speed where available
- frame time
- JIT block count
- JIT code-cache usage
- generic/interpreter fallback count
- audio underruns
- worker-queue depth
- ISO/CSO read throughput
- texture uploads per frame
- approximate texture-cache usage
- game-switch count
- process memory snapshot
- current PSP clock setting
- rendering resolution

Logging must be optional and disabled by default in release builds.

The supplied Xbox startup currently uses `printfEmuLog = true` and shows FPS. Make developer diagnostics configurable rather than permanently enabled.

---

# 5. Milestone C — Validate and improve the existing Xenon PPC JIT

## Critical discovery

The complete legacy port already contains a native PSP MIPS → PowerPC JIT.

Important files include:

```text
Common/ppcEmitter.cpp
Common/ppcEmitter.h

Core/MIPS/PPC/PpcJit.cpp
Core/MIPS/PPC/PpcJit.h
Core/MIPS/PPC/PpcAsm.cpp
Core/MIPS/PPC/PpcRegCache.cpp
Core/MIPS/PPC/PpcRegCacheVPU.cpp
Core/MIPS/PPC/PpcCompAlu.cpp
Core/MIPS/PPC/PpcCompLoadStore.cpp
Core/MIPS/PPC/PpcCompBranch.cpp
Core/MIPS/PPC/PpcCompFpu.cpp
Core/MIPS/PPC/PpcCompVFPU.cpp
```

The PPC emitter already contains Xbox-appropriate instruction/data cache synchronization logic using PowerPC cache instructions. Preserve and validate this implementation.

## Tasks

### C1. Prove which CPU core is actually executing

The supplied Xbox front-end requests `CPU_JIT`.

The legacy tree also contains `NO_JIT` definitions in some Xbox project configurations while the Core project has PPC support.

Trace all relevant preprocessor paths and prove:

- whether `CPU_JIT` creates the PPC JIT
- which project defines `NO_JIT`
- whether that macro affects Core JIT compilation or only a front-end/library
- whether any configuration silently falls back to interpreter

Show the active backend in the developer overlay.

### C2. Correctness first

Before optimizing:

- compare PPC JIT behavior with interpreter behavior
- use `hrydgard/pspautotests`
- identify invalid/disabled PPC operations
- identify `Comp_Generic()` fallbacks
- verify delay-slot behavior
- verify sign/zero extension
- verify unaligned loads/stores
- verify FPU rounding/NaN behavior where feasible
- verify VFPU operations
- verify exceptions and branch behavior
- verify self-modifying/code invalidation paths

### C3. JIT coverage telemetry

Count:

- native compiled MIPS ops
- generic fallback ops
- interpreted ops
- block invalidations
- code-cache clears

Generate per-game summary logs.

### C4. Optimize high-frequency fallbacks

Only after correctness is established, implement/repair native PPC compilation for hot operations that still fall back.

Priority:

1. integer ALU
2. branches
3. loads/stores
4. FPU
5. VFPU
6. syscall/HLE transition overhead
7. block linking
8. register-cache spills/reloads

### C5. Modern PPSSPP lessons

Use current PPSSPP v1.20.4 JIT/common/IR logic as a correctness and optimization reference, but adapt concepts to the existing PPC backend. Do not attempt to compile current x86/ARM/RISC-V emitters on Xbox.

---

# 6. Milestone D — Remove unsafe global performance hacks

The current Xbox configuration contains aggressive global settings such as:

```text
iLockedCPUSpeed = 111
iNumWorkerThreads = 5
separate CPU thread = true
separate I/O thread = true
2x PSP output resolution
vertex cache = false
anisotropy = 8
```

These must become measured settings, not unquestioned constants.

## PSP CPU clock

Do not globally force 111 MHz.

Default should use normal PSP timing / PPSSPP default behavior unless testing proves another value is required for a specific title.

Expose per-game override:

- Auto/default
- 111
- 222
- 266
- 300
- 333

Do not mislabel CPU-clock underclocking as a universal performance enhancement.

## Worker threads

The Xbox 360 has multiple hardware threads but blindly using five PPSSPP workers may compete with:

- emulation CPU
- graphics submission
- audio
- I/O

Benchmark worker counts and thread affinity where the XDK safely permits it.

Candidate profiles:

```text
Conservative
CPU/JIT priority + 2 workers

Balanced
CPU/JIT priority + 3 workers

Aggressive
CPU/JIT priority + 4 workers
```

Choose based on measurements, not hardware-thread count alone.

---

# 7. Milestone E — ROM Library 2.0

This is a required milestone.

## UX goal

On startup, PPSSPP Xenon opens to a normal emulator library.

Tabs/views:

```text
RECENT | ALL GAMES | FAVORITES | FOLDERS
```

Optional later:

```text
HOMEBREW
```

## Game card data

Each game should support:

- title
- file name
- canonical path
- DISC_ID when available
- ICON0.PNG
- PIC1.PNG background/detail art
- file size
- format: ISO / CSO / PBP / CHD if later supported
- last played
- play count
- favorite flag
- compatibility/per-game-profile indicator

Do not require external metadata servers.

Prefer data embedded in the user's game image.

## Library index

Create a persistent local index, for example:

```text
game:\cache\library.dat
```

or another clearly documented application-owned location.

The index should include:

- schema version
- configured roots
- path
- size
- modified timestamp where available
- DISC_ID
- title
- art-cache key
- last played
- play count
- favorite
- last scan status

Use a compact binary or simple robust format suitable for the XDK. Do not add a heavy database dependency merely for this feature.

## Scan behavior

First scan:

1. enumerate configured roots
2. find supported PSP content
3. parse lightweight metadata
4. populate library immediately
5. load/decode artwork lazily
6. save index

Later boots:

1. load cached index quickly
2. validate roots
3. rescan only as needed
4. remove missing files gracefully

## Artwork caching

The Xbox 360 has limited RAM.

Requirements:

- lazy loading
- LRU or bounded texture cache
- release textures when evicted
- do not decode hundreds of covers at startup
- cache small thumbnails where worthwhile
- use fallback art when metadata is unavailable
- no game should fail to launch merely because artwork failed

## Controller behavior

- A: launch
- B: back
- LB/RB: switch tabs
- RT: grid/list where currently supported
- X: favorite/unfavorite when appropriate
- Y: details/options
- Start: settings/library options

Preserve the existing in-game menu chord unless a later UI decision deliberately changes it.

## Search/filter

At minimum:

- alphabetical sort
- recently played
- favorites
- file format
- storage device/folder

If text search is added, make controller-only use practical.

---

# 8. Milestone F — Safe game switching / Session Manager

The existing shutdown/re-init loop is the correct starting point.

Formalize it into a clearly owned lifecycle.

Suggested abstraction:

```text
Xbox Shell
  ├─ Launcher
  ├─ D3D/XAudio/XInput platform services
  └─ PSP Session Manager
       ├─ StartGame(path)
       ├─ StopGame()
       ├─ ResetGame()
       └─ SwitchGame(path)
```

## SwitchGame sequence

The exact internal order must follow what the PPSSPP core requires, but the outcome must guarantee:

1. stop emulation loop
2. finish/flush save operations
3. stop game-specific audio work
4. close game filesystem/block device
5. tear down game-specific GPU objects/caches
6. tear down JIT blocks/code cache
7. call the appropriate PSP shutdown path
8. preserve shell-owned Xbox D3D/UI resources where safe
9. reset game-specific global state
10. initialize the new PSP session
11. on failure, return safely to the library with an error message

Never leave the user at a black screen after a failed second-game launch.

## Return to Library

In-game menu must contain:

```text
Continue Game
Settings
Reset Game
Return to Library
Exit to Xbox
```

Save-state UI may remain alongside these entries.

## Soak test

Test at least 20 consecutive game-session transitions in one PPSSPP Xenon process.

Examples:

```text
A → Library → B → Library → A
A → Reset → A
A → Library → invalid/missing game → Library
ISO → CSO → PBP → ISO
```

Track memory before and after each transition.

---

# 9. Milestone G — Per-game settings

Add a game-specific profile keyed by DISC_ID, with path fallback for homebrew.

Potential settings:

## CPU

- PPC JIT / interpreter fallback
- PSP CPU clock
- fast memory if safe
- worker profile

## Graphics

- 1x PSP (480x272)
- 2x PSP (960x544)
- optional additional tested modes
- frameskip
- auto frameskip
- texture filtering
- anisotropy
- hardware transform
- vertex cache
- framebuffer/rendering compatibility toggles

## Audio

- enable/disable
- latency/buffering mode if exposed safely

Do not force one aggressive configuration on every game.

Provide:

```text
Use Global Settings
Save Settings for This Game
Reset Game Settings
```

---

# 10. Milestone H — GPU/Xenos optimization

Keep the Xbox 360 XDK Direct3D 9 backend.

Do not attempt to replace it with Vulkan, D3D11, OpenGL, or a desktop graphics layer.

## Performance work

Profile and improve:

- redundant D3D state changes
- texture binds
- vertex/pixel shader switches
- render-target changes
- dynamic vertex/index uploads
- texture invalidation
- framebuffer transitions
- CPU/GPU synchronization
- draw-call setup overhead
- temporary allocation churn

Implement state caching where safe:

```text
Requested PSP GE state
        ↓
Xbox GPU state cache
        ↓
Changed?
  ├─ No → draw
  └─ Yes → issue minimum D3D change → draw
```

## Modern PPSSPP backports

Prefer backend-independent GE correctness fixes from current PPSSPP where they can be adapted cleanly.

Do not transplant modern backend code whose assumptions depend on Vulkan/D3D11/modern shader languages.

---

# 11. Milestone I — Big-endian/Xenon memory optimization

Xbox 360 Xenon is big-endian. This is not a normal current PPSSPP target.

Audit:

- PSP memory accessors
- block-device reads
- texture upload conversion
- vertex decoding
- PARAM.SFO parsing
- framebuffer conversion
- save-state serialization
- JIT loads/stores

Goals:

- centralize endian conversion
- avoid repeated swaps of the same data
- use proven PPC/XDK intrinsics/instructions where beneficial
- preserve exact PSP behavior

Correctness tests are mandatory after any endian optimization.

---

# 12. Milestone J — I/O and compressed-image performance

Profile ISO and CSO separately.

Implement where beneficial:

- read-ahead
- block cache
- sequential-read optimization
- bounded asynchronous I/O
- decompression buffer reuse
- fewer small allocations
- background metadata reads only when emulator load allows

Do not allow library scanning or artwork extraction to compete aggressively with active gameplay.

## CHD

Official PPSSPP supports CHD in current versions.

For Xbox 360:

1. research exact dependencies
2. test XDK/compiler compatibility
3. measure CPU cost vs CSO
4. measure memory usage
5. add only if stable

CHD is an enhancement, not a blocker for v1.0 of PPSSPP Xenon.

---

# 13. Milestone K — Audio and media stability

Preserve the Xbox-specific XAudio work in the supplied overlay unless a measured problem requires changes.

Measure:

- underruns
- buffer depth
- desync
- game-switch audio cleanup
- video playback synchronization

Backport current PPSSPP HLE/media fixes selectively.

FFmpeg/media upgrades are high risk on the old XDK compiler. Do not replace the full media stack just to match upstream version numbers.

Prioritize game correctness over library freshness.

---

# 14. Milestone L — Selective compatibility modernization from PPSSPP v1.20.4

Current PPSSPP is many years newer than the Xbox base, but the port cannot safely absorb a decade of changes as a single merge.

Create `docs/BACKPORT_LEDGER.md`.

For each candidate backport record:

```text
Subsystem:
Upstream source:
Upstream tag/commit:
Reason:
Xbox files touched:
Compiler adaptations:
Endian considerations:
JIT considerations:
Regression tests:
Result:
```

## Backport order

Recommended order:

1. CPU/MIPS correctness fixes relevant to observed failures
2. VFPU correctness
3. scheduler/timing fixes
4. HLE kernel/module fixes
5. ISO/filesystem fixes
6. backend-independent GE fixes
7. audio/HLE fixes
8. PSMF/media fixes
9. save-data fixes
10. optional quality-of-life features

Do not target "same version number as PC PPSSPP."

Target:

> modern compatibility behavior where practical on Xbox 360 while retaining a stable Xenon-specific architecture.

---

# 15. Milestone M — Crash recovery and diagnostics

The current Xbox loop has crash-continuation behavior.

Improve diagnostics so a failed title creates a useful report without crashing the shell.

Record:

- game path
- DISC_ID
- exception code
- active CPU backend
- rendering mode
- PSP clock
- JIT cache usage
- last HLE module where known
- last meaningful log lines
- free/used memory estimate

After a recoverable emulation crash:

```text
Game stopped unexpectedly.

[Return to Library]
[View Error Code]
```

Do not automatically relaunch the same crashing game forever.

---

# 16. Milestone N — Compatibility database

Create a local compatibility file maintained by testing.

Suggested states:

```text
Perfect
Playable
In-Game
Boots
Broken
Unknown
```

Track per title:

- DISC_ID
- title
- tested build
- result
- FPS/speed observation
- audio
- graphics issues
- required per-game settings
- notes

The emulator itself may optionally display the status, but the source repository must at least maintain `docs/COMPATIBILITY.md` or a machine-readable equivalent.

---

# 17. Testing strategy

Use four layers.

## Layer 1 — build/static validation

- all Xbox projects
- Debug where needed
- Release
- Release_LTCG
- no newly introduced desktop-only dependencies

## Layer 2 — official PSP tests

Reference:

`https://github.com/hrydgard/pspautotests`

Prioritize tests relevant to:

- CPU
- VFPU
- FPU
- memory
- kernel/HLE
- file I/O
- timing

## Layer 3 — legal homebrew/demo smoke tests

Maintain a small redistributable test set only where licensing clearly permits it.

## Layer 4 — user-owned commercial dumps

Maintain a test matrix but never commit game data.

Suggested stress titles/categories:

- God of War titles — CPU/GPU/VFPU stress
- GTA titles — streaming/I/O stress
- Metal Gear Solid: Peace Walker — broad compatibility
- Gran Turismo — GPU/CPU stress
- Tekken 6 — graphics/timing
- Kingdom Hearts Birth by Sleep — compatibility/timing
- Monster Hunter — long-session stability
- Resistance: Retribution — graphics/media
- Final Fantasy titles — HLE/media/save behavior

No game is to receive a hack merely to improve one title if it breaks PSP-correct behavior elsewhere unless the change is implemented as a documented per-game compatibility rule.

---

# 18. Performance test protocol

For each selected test title capture:

```text
Build:
Game:
DISC_ID:
Format:
Storage:
CPU Backend:
PSP Clock:
Resolution:
Frameskip:
Worker Profile:

Average FPS:
Average Emulation Speed:
Worst observed frame-time spike:
Audio underruns:
JIT generic fallbacks:
JIT cache clears:
Texture-cache high-water mark:
Approx. memory use:
Notes:
```

Repeat measurements from the same gameplay area where possible.

Compare against `xenon-baseline-legacy`.

---

# 19. Game-library acceptance criteria

The library milestone is complete when:

- multiple library roots can be added and removed
- HDD and USB roots can coexist
- ISO and CSO titles appear correctly
- PBP/homebrew is handled correctly where supported
- game title comes from PSP metadata when available
- CSO metadata does not lose artwork merely because it is compressed
- missing/corrupt art never prevents a game launch
- cached library loads without a full rescan
- Recent works
- Favorites works
- grid/list works
- returning from gameplay returns to the library
- selecting another game starts it without restarting the Xbox application
- repeated rescans do not leak D3D textures
- removed games disappear cleanly
- invalid files show a useful failure rather than freezing the UI

---

# 20. Game-switch acceptance criteria

Complete when:

- current game can return to library
- same game can be relaunched
- different game can be launched
- failed launch returns to library
- audio does not continue from previous game
- controller input does not leak from menu into newly launched game
- old ISO/CSO file handles are closed
- game-specific textures/framebuffers are released
- JIT state is reset
- save data survives switching
- at least 20 transitions complete without a crash
- no continuous unexplained memory growth is observed after caches stabilize

---

# 21. Release target

Initial modernization release:

**PPSSPP Xenon v0.1.0-alpha**

This release should prioritize:

1. reproducible Xbox 360 build
2. working PPC JIT validation
3. stable ROM library
4. reliable return-to-library/game switching
5. removal of dangerous hardcoded global tuning
6. diagnostics/per-game configuration foundation
7. first set of high-value compatibility backports

Later versions can expand compatibility and optimization.

---

# 22. Git discipline

Recommended branch sequence:

```text
bootstrap/legacy-x360
feature/library-2
feature/session-manager
perf/ppc-jit
perf/xenos
compat/ppsspp-backports
release/0.1.0-alpha
```

Keep commits focused.

Examples:

```text
bootstrap: import legacy Xbox 360 PPSSPP source
xbox: overlay current launcher and platform files
library: build persistent multi-root PSP index
library: use filesystem abstraction for CSO artwork
session: make game switching deterministic
jit: expose active PPC backend and fallback telemetry
jit: repair PPC VFPU opcode ...
perf: remove forced 111 MHz global PSP clock
gpu: release launcher texture cache on rescan
compat: backport ... from PPSSPP v1.20.4
```

Never mix a large compatibility backport with unrelated UI changes in the same commit.

---

# 23. Documentation required before milestone close

Codex must leave:

```text
README.md
docs/BUILD_XBOX360.md
docs/ARCHITECTURE.md
docs/BASELINE.md
docs/PERFORMANCE.md
docs/COMPATIBILITY.md
docs/BACKPORT_LEDGER.md
docs/LIBRARY.md
docs/JIT_PPC.md
docs/TESTING.md
```

`README.md` must clearly identify PPSSPP Xenon as a community Xbox 360 port/modernization derived from PPSSPP and retain the appropriate upstream licensing/attribution.

---

# 24. Final directive to Codex

Treat this as a **preservation + modernization** project.

Do not erase the working 360-specific engineering in pursuit of current upstream parity.

The preferred strategy is:

```text
Working Xbox 360 port
        +
Current Xbox launcher overlay
        +
Validated existing PPC JIT
        +
Selective modern PPSSPP correctness fixes
        +
Xenon/Xenos-specific profiling
        +
Persistent emulator-style ROM library
        =
PPSSPP Xenon
```

The primary measure of success is not how much upstream code was copied.

The measure is:

- more PSP games work
- working games run faster and more consistently
- the Xbox application remains stable
- users can browse and switch games like a normal emulator
- changes are measurable, testable, and reversible
