# Baseline warning checkpoint — M3

**Debug and Release_LTCG both complete full local Rebuilds with 0 warnings and
0 errors.** The remaining M2 totals (46 Debug / 40 Release_LTCG) are resolved;
the earlier 62-warning fixes also remain clean. Both switchable library views
and the navy/teal design previews are preserved. Nothing was deployed or launched
on an Xbox. Runtime compatibility and performance remain NOT RUN.

## Reviewable changes

`baseline-overlay/remaining-warnings.patch` changes 18 source/project files over
M2. `Xbox/XenonEmulationLoop.h` holds the existing owner emulation loop in a
non-inlined helper so its SEH handler no longer shares a function with main's
RAII objects. The exact loop body and surrounding lifecycle are compared with
the authenticated owner source. The exception filter, core timing, input/menu
sequence and return/reset/exit decisions are retained. The helper is called once
per session; no per-frame helper call or tuning change is added.

The numeric warning investigation found a real morph-normal defect: multiplying
an endian-wrapped signed 16-bit sample by a float selected an overload returning
the wrapped integer type, truncating fractional normals. Convert the sample to
float before multiplying, matching the intended floating-point accumulation.
A negative control reproduces the old zero result for a fractional normal;
786,432 sample/weight/reversal cases and a blended-normal case pass afterward.

The trailing-backslash launcher comment also swallowed the following root-directory
assignment during XDK preprocessing. Rewording the comment restores the existing
intended initialization to the game drive; before/after preprocessing and host
root checks verify it. Both grid/list controls and renderers remain intact.

Other changes give unsigned fields unsigned comparison constants, use a signed
tile-loop index matching tileCount, make bounded emitter offsets explicitly
signed, bind the block cache after member construction, type the masked VFPU
negate flag as bool, remove unused scalar locals, guard an unused platform label
and replace xxHash's boolean-division compile-time check with an equivalent
negative-array-size check. [The warning review](WARNING_REVIEW_M3.md) maps every
code/count to its change and verification.

Debug Common/Core/GPU projects disable obsolete MinimalRebuild (/Gm), retaining
multiprocess compilation (/MP). This resolves their incompatible build options.
Three Common units containing no executable code or CRT initializers are excluded
from Debug/Release_LTCG; full linking confirms required symbols are still present.
No warning is disabled, warning level reduced or optimization policy weakened.

## Evidence

| Check | Result |
| --- | --- |
| Original archive hash and every member CRC | PASS, authority unchanged |
| Existing host unit tests | 20 PASS, no local skips |
| State-deletion helper / actual artwork-loader tests | PASS, retained |
| Morph normals | 786,432 cases plus multi-morph blend PASS; old defect reproduced |
| Unsigned limits, tile bounds, VFPU negate flags and initial root | PASS, 4,194,304 prefix/lane checks |
| Actual session loop | 8 host cases PASS, including native Windows SEH fault/filter |
| Original loop/lifecycle versus extracted helper | Exact source comparison PASS |
| PPC emitter | All 82 generated prologue/epilogue words match reference; scratch address normalized |
| Cache construction/reinitialization | PASS; XDK class size/alignment unchanged per configuration |
| xxHash | 32 one-shot/streaming outputs match reference; false size check rejected |
| GPU layout | Four XDK compile-only probes PASS, existing sizes/offsets/alignment preserved |
| Excluded Common units | XDK COFF inspection: zero code bytes, no CRT initializers |
| Fresh preparation versus final built source | Exact byte match |
| Debug full Rebuild | PASS, 0 warnings / 0 errors |
| Release_LTCG full Rebuild | PASS, 0 warnings / 0 errors |
| Console deployment, launch, runtime or performance | NOT RUN |

The XDK is PowerPC 16.00.11886.00 with MSBuild 4 and installed licensed VS2010.
Host regressions use actual staged functions; new fixtures pass with warnings as
errors. Emitter tests use the real project's /W3 (its unchanged primitives have
additional /W4 narrowing diagnostics); other new MSVC fixtures use /W4. Original
reference/negative controls intentionally retain diagnostics and are not compiled
with /WX. Hosted GCC checks rebuild the fixture inputs from the fixed public donor
and authenticated owner overlay; no Xbox executable is executed by these tests.

[Build identities](evidence/m3/baseline-builds.json), full logs, zero-warning
inventories, source hashes, target probes and host outputs are in
[M3 evidence](evidence/m3/). XEX timestamps/paths mean rebuilds are not claimed
byte-for-byte deterministic. This is a warning-clean build checkpoint, not a
runtime-qualified release or a performance measurement.

## Source, dependencies and preservation

The original owner archive retains SHA-256
`6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35`.
The legacy donor stays at `540db97d96136b2139e5f12dd3c0bb18f2e1cd1f`.
Separate patches apply after archive verification; donor/owner source encodings
are preserved byte-for-byte outside intentional hunks and line-ending normalization.
All twelve FFmpeg libraries remain identical to M2, with all 436 objects PPCBE.
FFmpeg source, headers and codec profiles are unchanged and were not rebuilt.
Original licenses/notices remain, and no SDK contents or generated binaries are
committed. The two functional corrections above and the bounded lifetime changes
are explicit; no JIT/core modernization, clock/worker tuning or visual redesign
is included. Detailed CCLOS styling remains provisional.

Every legacy Deploy entry remains explicitly excluded, and the local driver still
rejects enabled/missing deployment metadata. M3 performs no console connection,
deployment or launch. Historical M1's failed automatic copy attempt remains
recorded; no historical failure is erased.

## Retained build failure and limits

The first Debug build exposed a further same-file unsigned comparison; all
unsigned wrapped comparisons in that path were checked and corrected. The first
Release attempt exhausted local disk space. Only older task-generated compiler
intermediates and Common/Core/GPU libraries under verified task staging roots
were removed; original sources, FFmpeg, XEX outputs and packaged milestones remain.
Both full builds were repeated after the final emitter refinement and passed;
accepted output identities are separate from initial diagnostics.

No Xbox boot, rendering/audio/input, savedata/states/switching, memory growth or
performance result is claimed. Keep PR #2 draft; no baseline tag, merge, release,
deployment or hardware run is part of this checkpoint.

[M0](BASELINE_M0.md), [M1](BASELINE_M1.md), [M2](BASELINE_M2.md) and their evidence
remain historical. M2 hashes apply at commit
`4ec6ba48525aa8be4e71eb05b6f113943f56327b`; M3 adds its own current evidence index.
