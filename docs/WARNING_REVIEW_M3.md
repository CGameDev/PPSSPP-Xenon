# Warning assessment — M3

All M2 diagnostic emissions are resolved in both full solution Rebuilds. The
auditor excludes MSBuild's repeated summary, and its zero counts agree with the
final MSBuild totals. Earlier C4742/C4744/C4715 fixes remain clean.

| Code | Prior Debug / Release_LTCG | Change and check |
| --- | ---: | --- |
| C4010 | 1 / 1 | Reword the comment ending in a backslash. XDK preprocessing proves the old comment consumed currentDir_ initialization and the new comment preserves it; host checks verify game-drive root. |
| C4018 | 4 / 4 | Give u32_le/SceSize_le fields positive unsigned literal thresholds, preserving high-bit/maximum-value behavior. Keep signed smoption.priority comparison signed. Use an int tile index matching int tileCount. Host tests cover zero, thresholds, high-bit and maximum u32 values and tile bounds. The first instantiation diagnostic hid additional uses in the same TU; those fields were checked too. |
| C4101 | 16 / 16 | Move dir inside its non-Xbox branch; remove only unused uninitialized scalar temporaries from six decoder emitters and four unused framebuffer locals. Used volatile scratch objects remain in their original order; no algorithm/code statement is deleted. |
| C4102 | 1 / 1 | Guard bail label for platforms with its goto branches. Existing memory-view behavior/cleanup statements remain. |
| C4146 | 3 / 3 | Convert bounded register byte sizes to signed int before negation and use a signed constant frame size. Host execution of actual emitters produces the same 82 PPC instruction words as reference, with a fixed scratch-buffer address on both sides. Generated PPC instructions are never executed. |
| C4244 | 1 / 1 | Convert endian-wrapped s16 to float before morph multiplication, avoiding the wrapper's integer-returning overload. Old fractional truncation is reproduced; exhaustive short-range/weight/reversal and blended-normal checks pass. This corrects a numeric defect, rather than concealing it with a narrowing cast. |
| C4355 | 1 / 1 | Construct the cache with a null CodeBlock pointer, then bind the fully member-constructed owner through Init(this) before ordinary initialization. Original constructor only stores pointers. Other ports keep Init(); Reset retains the binding. Host ordering checks and XDK layout probes pass (Debug 56 bytes, release 48; alignment 4, unchanged versus M2). |
| C4509 | 11 / 11 | Move the unchanged owner loop/SEH block into a noinline helper containing POD locals. Keep RAII objects in main, outside SEH. Fault returns false and main clears pspInited as before. Eight host scenarios, including native Windows RaiseException/filter behavior, pass; exact owner-source comparison protects loop and surrounding lifecycle. One call per session, none per frame. |
| C4800 | 1 / 1 | Express the masked 0/1 VFPU negate bit as a bool with !=0. Check every relevant 20-bit prefix across all four lanes (4,194,304 checks). |
| C4804 | 1 / 1 | Replace xxHash's enum boolean division with a compile-time char-array assertion. A false condition still fails compilation; 32 seeded/length one-shot and chunked outputs agree with untouched reference. Original license retained. |
| D9030 | 3 / 0 | Disable /Gm MinimalRebuild only in the three affected Debug project groups, retaining /MP and all runtime optimization/diagnostic settings. No warning suppression. |
| LNK4221 | 3 / 0 | Exclude stdafx.cpp, the empty ppcAbi.cpp and non-Xbox-only ExtendedTrace.cpp from Debug/Release_LTCG Common compilation. XDK probes show zero executable code/no CRT initializers, and full solution linking succeeds. Forced header includes remain; other configurations are unchanged. Reinclude a unit if it gains Xbox implementation. |
| **Total after full Rebuild** | **0 / 0** | **No warning disable, warning-level reduction or runtime tuning.** |

The separate patch touches 18 source/project files plus the new owner-loop helper;
original archives remain unchanged. Both UI modes and all preview assets remain.
GPU struct sizes/matrix offsets/global alignment, cache layout and FFmpeg hashes
are checked. Hardware compatibility, resource growth and performance are NOT RUN.
Zero warnings do not establish regression-free Xbox behavior. See BASELINE.md and
evidence/m3/ for exact artifacts, failures and test boundaries.
