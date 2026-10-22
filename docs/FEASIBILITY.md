# Xbox 360 feasibility and preservation boundaries

## Assessment

A CCLOS-style launcher is feasible in the existing XDK/D3D9 shell. A working,
faster or broadly compatible emulator has **not** been established. Recovery of
authentic owner source and a full linkable baseline must precede production UI
integration, CPU tuning or compatibility backports.

The destination repository currently contains a handoff, not a full emulator.
The legacy donor is a 0.9.x-era codebase with real Xenon support. This assessment
uses inspected code at the [pinned donor commit](https://github.com/metalex10/PPSSPP-X360/tree/540db97d96136b2139e5f12dd3c0bb18f2e1cd1f),
not assumptions about current desktop PPSSPP.

## Evidence and implications

| Area | Observed evidence | Implication / next proof |
| --- | --- | --- |
| CPU | `Core/MIPS/MIPS.cpp:32–39` selects the PPC JIT include under `PPC`; lines 178–179 construct `MIPSComp::Jit` for CPU_JIT. Core project includes PPC compiler/cache units; Debug compilation emitted CoreXbox.lib. | Existing JIT should be preserved and verified against interpreter/autotests. Compilation does not prove the executing backend or correctness. |
| Configuration | `Xbox/xx/xx.vcxproj` defines `NO_JIT` in front-end configurations; `Core/CoreXbox.vcxproj` Debug/Release definitions include `PPC` and `BIG_ENDIAN`, without `NO_JIT`. | A front-end macro alone does not prove the Core static library uses the interpreter. Confirm linked backend through runtime telemetry after a full build. Audit each configuration independently. |
| GPU | `GPU/Directx9/`, `GPU/GPUXbox.vcxproj`; GPUXbox.lib compiled. | Reuse the Xenos/XDK rendering path. Retain device ownership and render-state restoration between launcher and emulation. |
| Dependencies | Front-end references Xbox FFmpeg ppcD/ppc libraries that are missing from the donor checkout. | Reproduce the compatible FFmpeg build from recorded source/configuration; do not substitute host Windows/x86 libraries or unrelated prebuilt binaries. |
| Compiler | VS2010-era solution/project files; installed tools compiled the legacy libraries. | Respect old C++ syntax, ABI and big-endian rules; current upstream is a source of selective fixes. |
| Startup tuning | Legacy `XboxMain.cpp:288` sets 5 workers; line 301 forces 111 MHz; CPU_JIT requested at 228/310. | Preserve settings while establishing baseline. Measure controlled changes by title; no performance improvement claim yet. |
| Owner launcher | Handoff describes persisted recents, grid/list, metadata/artwork, states and return-to-library. ZIP contains named launcher/main sources but fails integrity. | Those behaviors remain preservation requirements, not verified owner-source implementation findings. Audit actual source only after recovery. |
| Licensing | Donor `LICENSE` is GPLv2; source headers include GPLv2-or-later notices, with separate third-party licenses. | Preserve all notices, corresponding source and third-party attribution on eventual import/distribution. M0 imports no emulator implementation. |

The legacy `.gitmodules` names dependencies, but the examined checkout has their
files tracked normally and no active gitlinks. Do not blindly update them to
moving upstream heads. Pin exact compatible dependency revisions during recovery.

## UI integration plan

Both tile and compact views are retained following owner review in this chat.
The detailed mockups are provisional. They reuse the approved navy/teal aesthetic:
calm dark canvas, clear teal focus, simple panels, upper navigation and lower
controller prompts. No proprietary CCLOS assets were copied into this public repo.

1. Recover and hash the owner source; import the pinned donor with its licenses,
   then apply owner same-path files last. Record a per-file manifest.
2. Recover Xbox FFmpeg dependencies, correct build-path/version-generation issues,
   and obtain full unchanged Debug and Release_LTCG builds.
3. Prove boot, sound/input, savedata, return-to-library and second-game launch.
   Preserve rollback artifacts and measure baseline resources/frame timing.
4. Audit the actual launcher entry/render/input boundaries. Add an optional CCLOS
   presentation path using the same library model and session action dispatcher.
   Keep the original launcher available until the new presentation passes.
5. Share selection/scroll state between tile/list views. Reuse embedded artwork
   with a bounded cache and fallback. No full scan, decode, I/O or network work
   on the input/render path. No extra background shader/video effect is required.
6. In-game menu styling must restore all GPU/input state and preserve save/load,
   reset and return semantics. Unimplemented settings stay visibly unavailable.
7. Compare the exact candidate to baseline on Xbox before accepting UI/runtime
   integration. Host browser responsiveness says nothing about Xenon performance.

Do not wholesale merge current upstream, rewrite the PPC JIT, replace the session
loop, change clock/worker defaults, add CHD dependencies or install console hooks
as part of this first UI milestone.
