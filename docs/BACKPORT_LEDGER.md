# Backport ledger

M7 is an original local correction, not an upstream intake. The pinned donor's
PGF::getBits used native word byte order; the owner log stops during font parsing.
Only that helper is changed to existing u32_le reads with defined bit boundaries.
Original licensing is retained, including PGF.cpp's existing JPCSP attribution
and GPL3 provenance note. Font assets, glyph/state formats and GPU/JIT/session/UI
code are unchanged. All 18 font tables and 8,448 oracle cases pass; both full
builds are clean. Xbox resolution/performance remain unverified. See
PGF_FONT_FIX_M7.md and evidence/m7 for reproduction, scope and rollback.

M5 is an original presentation-only patch for RenderInGameMenu/RenderToast. It reuses M4 helpers, font and primitive APIs, without upstream code, action/core changes or tuning. Original source and licenses stay intact. See HADCV_M5.md.

M4 adds an original launcher-only CCLOS-style visual layer and bounded fitting/scroll helpers. No upstream backport, new asset dependency, core/session code or tuning change. See HADCV_M4.md and evidence/m4/.

M3 adds original warning fixes, not an upstream modernization merge: owner SEH
loop extraction, correct floating morph-normal multiplication, typed comparisons
and offsets, delayed cache binding, a standard xxHash compile-time assertion and
bounded unused-code/project cleanup. Original licenses remain. Both views stay.

M2 applies no upstream core backport. Original patch: aligned extern declarations
matching existing globals and deterministic artwork-loader failure cleanup.
No GPU type layout, emulation algorithm or optimization settings change.

M1 applies no core backport. Dependency intake: unmodified stb_truetype v1.26,
nothings/stb commit `6e9f34d5429cf16790ec43c9bac3f1ee4ad1f760`, MIT option,
satisfying the owner's existing packing API. Atlas/API adaptation is original
project glue under baseline-overlay with precise diffs and host tests. Xbox
FFmpeg is rebuilt from the pinned donor without codec-source changes. M0 follows.

No emulator changes or backports have been applied in M0. PPSSPP `v1.20.4` is
fixed at peeled commit `fa50bb1976065c4f8b1b47af227d367fe9771555` for comparison.
The legacy implementation and damaged owner archive remain separate from new host
tooling and original design studies.

For every later backport record upstream repository/tag/commit, license, exact
files and rationale, XDK/PPC/big-endian adaptations, baseline/candidate identity,
host and Xbox validation outcomes, performance evidence and a rollback commit.
Never combine a core compatibility backport and a presentation change merely to
reduce the number of commits.
