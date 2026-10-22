# Warning assessment — M2

The M1 final incremental Release_LTCG log emits 62 warnings: C4742 ×30,
C4744 ×30 and C4715 ×2. It was not a full solution warning inventory.
`tools/audit_build_warnings.py` stops at the summary boundary so MSBuild's
repeated diagnostics are counted once. Both final M2 full Rebuilds have zero
emissions of those three codes. No warning is disabled or hidden by the patch.

## Original 62: cause, fix and evidence

| Code | Cause | Fix and validation |
| --- | --- | --- |
| C4742 / C4744, 60 total | GPUState.cpp defines gstate/gstate_c with variable alignment 16, while GPUState.h extern declarations expose alignment 4 to other translation units. The linker therefore reports conflicting symbol types/alignment. | Apply the same existing MEMORY_ALIGNED16 macro to both extern variables. Do not align or edit the struct types. XDK probes confirm type sizes 1616/420, type alignment 4, matrix offsets 1024/1072/1120/1184/1232 before/after, and new variable declaration alignment 16. Full LTCG linking reports no mismatch. |
| C4715, 2 total | LoadGameIcon and LoadPNGTexture place free/return inside successful CreateTexture branches. A failed creation falls off the non-void function and leaks decoded pixels. | Move unconditional cleanup/return outside the creation branch. Release and return null after failed LockRect. Guard empty icon data. Twelve host cases exercise early failures, invalid dimensions, failed create/lock and successful two-row swizzle/pitch/padding. Original functions reproduce both C4715 under /W4 /WX; patched actual functions pass. |

Only GPU/GPUState.h and Xbox/XboxLauncher.cpp change among donor/owner C/C++ and
project files against M1. The generated identity string separately advances to
M2. Original archive, full struct definitions, GPU global definitions, codecs,
compiler settings, session code and grid/list renderer code remain as before.
Fresh patch replay matches the final built source bytes.

## Other diagnostics exposed by full rebuilding

| Code | Debug | Release_LTCG | Inspection and disposition |
| --- | ---: | ---: | --- |
| C4010 | 1 | 1 | XboxLauncher.cpp comment ends in a backslash immediately before currentDir_ initialization. Treat as a potential preprocessing/initial-scan issue, not a harmless cosmetic warning. Kept separate from the two loader fixes; review preprocessed constructor behavior before changing it. |
| C4018 | 4 | 4 | Swap.h templated comparisons (three instantiations) and Directx9/helper/global.cpp. Signed/unsigned comparisons require call-site bounds/negative-value tests. No blind cast added. |
| C4101 | 16 | 16 | Unreferenced locals: FileUtil.cpp and Directx9 vertex decoder/framebuffer paths. Declarations remain; their wider code is unchanged. Removing them would be a separate cleanup. |
| C4102 | 1 | 1 | MemArena.cpp unused bail label under this platform configuration. No flow-control edits. |
| C4146 | 3 | 3 | PPC emitter prologue/epilogue negates unsigned register/frame sizes before immediate encoding. Changing signedness requires emitter instruction/ABI tests. |
| C4244 | 1 | 1 | Swap.h multiplication instantiated with float and s16, possible narrowing. Needs value/rounding boundary tests; no conversion semantics changed. |
| C4355 | 1 | 1 | PpcJit constructor passes this to its block-cache initializer. Object lifetime/use needs focused review; no constructor rewrite. |
| C4509 | 11 | 11 | Owner XboxMain session loop combines SEH with C++ objects having destructors. A structural cleanup/exception-safety change needs lifecycle regression tests. No exception behavior or session loop altered. |
| C4800 | 1 | 1 | PpcCompVFPU passes an integer negate flag to a boolean parameter. No JIT flag/constant semantics changed. |
| C4804 | 1 | 1 | xxhash compile-time size assertion uses boolean arithmetic. This is an unchanged third-party compile-time guard, not an executed bool division. |
| D9030 | 3 | 0 | Debug Common/Core/GPU multi-file compilations combine /Gm and /MP. A compile-only two-file probe reproduces D9030 with both flags, and neither flag alone emits it. Preserve existing build options in this source-fix checkpoint. |
| LNK4221 | 3 | 0 | Debug Common library members stdafx/ppcAbi/ExtendedTrace provide no new public symbols. No object exclusion or project restructuring. |
| **Total** | **46** | **40** | **These are retained, not certified harmless or suppressed.** |

The final rebuild logs and per-emission JSON inventories are in evidence/m2/.
Targeted source fixes are established by compile/link/host evidence. This does
not establish Xbox behavior or performance equivalence. No console deployment,
launch or runtime test was performed. Both views remain; PR #2 stays draft.
