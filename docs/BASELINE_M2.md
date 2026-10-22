# Baseline warning checkpoint — M2

The original **62 Release_LTCG link warnings are resolved**: 30 C4742 alignment
mismatches, 30 associated C4744 type mismatches, and two C4715 missing returns.
Debug and Release_LTCG are fully rebuilt locally with the licensed Xbox compiler.
These remain untested Xbox executables. Both switchable library views remain.

## Changes and preservation

`baseline-overlay/warning-fixes.patch` is applied after the M1 adapters. The
byte-exact owner archive and its original authority hash remain unchanged:
`6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35`.
The donor stays pinned at `540db97d96136b2139e5f12dd3c0bb18f2e1cd1f`.

- GPUState.h now applies MEMORY_ALIGNED16 to the two **extern global variables**,
  matching their existing definitions in GPUState.cpp. Neither struct definition
  changes. Compile-only XDK checks confirm 1,616/420-byte type sizes, 4-byte type
  alignment and every matrix offset in both configurations before and after the
  fix. Consumers now see the globals' existing 16-byte alignment. Applying
  alignment to the struct types instead would risk padding/layout changes.
- LoadGameIcon and LoadPNGTexture now free decoded pixels and return a defined
  result when texture creation fails. Failed locks release the texture and return
  null, allowing existing fallback handling. Empty icon data is rejected before
  indexing the vector. Successful copy/swizzle/pitch behavior is unchanged.
- The local build driver accepts `-Rebuild`, retaining all deployment checks.
  Three rejection cases prove missing/implicit/enabled deployment metadata stops
  before MSBuild. All four real project Deploy entries remain explicitly excluded.
- Generated provenance identifies M2. No compiler optimization, warning policy,
  clock/worker setting, codec profile, renderer algorithm or session loop changes.

Fresh preparation reproduces the built patched source byte-for-byte. Only
GPU/GPUState.h and Xbox/XboxLauncher.cpp change among donor/owner source and
project files compared with M1; the generated version string also advances.
All twelve FFmpeg libraries are reused byte-for-byte from verified M1 builds,
covering 436 PPCBE objects. No FFmpeg source/header changed, so it is not rebuilt.
The design HTML, preview images and launcher grid/list behavior remain unchanged.
Detailed CCLOS styling remains provisional.

## Actual checks

| Check | Result |
| --- | --- |
| Original archive hash and every member CRC | PASS |
| Host test suite | 20 PASS, no local skips |
| Actual patched loaders with injected failures and pixel/pitch checks | 12 cases PASS, C++98 /W4 /WX |
| Original loader negative control | Both C4715 diagnostics reproduced; expected rejection |
| XDK layout/alignment probes | M1 and M2, Debug and Release_LTCG: four compile-only passes |
| Fresh patch replay versus built source | Exact byte match |
| FFmpeg identity and architecture | 12 identical libraries; 436 PPCBE objects |
| Debug full Rebuild | PASS, 0 original-target warnings; 46 other warnings |
| Release_LTCG full Rebuild | PASS, 0 original-target warnings; 40 other warnings |
| Deployment, Xbox launch or runtime/performance tests | NOT RUN |

[Build identities](evidence/m2/baseline-builds.json), full rebuild logs, warning
inventories and source/preservation receipts are in [M2 evidence](evidence/m2/).
The warning auditor counts emissions before MSBuild repeats its summary; the
counts agree with MSBuild's final totals. These builds are **not warning-free**.

A fresh replay check caught a launcher encoding difference in the first staged
copy. The exact replay bytes replaced that file and both full rebuilds were
repeated before final artifact identities were recorded. Initial diagnostic logs
are retained separately; the final logs and receipts identify accepted outputs.

## Other warnings and remaining limits

The 62-warning M1 log was an incremental final link. Full solution rebuilding also
emits older compile/library diagnostics. [The warning assessment](WARNING_REVIEW_M2.md)
records counts, locations and reasons for deferring behavioral changes. In
particular, C4509 concerns SEH with C++ destructors in the owner session loop;
C4018/C4244 involve conversions, and PPC emitter/JIT warnings require their own
correctness tests. They are not certified harmless. No diagnostic is suppressed
and no warning level or optimization is weakened to make this checkpoint pass.

No console connection, deployment or launch is requested by M2. The historical M1
failed automatic copy attempt remains documented in [M1](BASELINE_M1.md); its
explicit exclusions are preserved. Xbox boot, graphics, audio/input, savedata,
states, switching, memory growth and performance remain NOT RUN. No baseline tag
or release is created, and PR #2 remains draft. Any hardware work needs a separate
owner instruction; this checkpoint authorizes none.

[M0](BASELINE_M0.md), [M1](BASELINE_M1.md) and their evidence remain historical.
M1 evidence hashes refer to commit d68b9a609b3e145e72a3fa97613b78de738215a5;
M2's new evidence index binds current project bytes without rewriting old records.
