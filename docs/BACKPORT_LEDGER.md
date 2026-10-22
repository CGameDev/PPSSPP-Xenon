# Backport ledger

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
