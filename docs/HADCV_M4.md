# HAD-CV M4 checkpoint

Authorized scope: implement the first CCLOS-style launcher on the same PR, keep
both switchable views and emulator performance, show updated provisional
previews, fully rebuild Debug/Release_LTCG, and do no Xbox deployment or launch.

Input identity is M3 `6f65400`, the unchanged authenticated owner archive and
pinned donor. The bounded implementation is a separate launcher-only patch plus
presentation helper. Source comparison and exact fresh replay retain the
emulator/session/IGM paths, class state, loaders, cache/resource policy and all
prior warning fixes. The only input logic addition converts view scroll units.

Continuous verification: 20 existing tests; actual-source M3 regressions; native
launcher method traces for both views, fitting, input and inactive paths; M3/M4
drawing budgets; 56 browser scenarios; both full XDK Rebuilds warning-clean;
archive/FFmpeg identity and all four explicit deployment exclusions. Source and
output hashes bind the evidence. See BASELINE.md and evidence/m4/.

Both view types are approved. Detailed visual acceptance remains provisional;
host previews are not console captures. Hardware performance/compatibility,
legibility, repeated sessions and leak checks remain NOT RUN. Drawing counts
provide a bounded host cost comparison, not a claim of measured Xbox speed.

The owner's latest instruction authorizes this reversible implementation while
deferring hardware testing. No connection, deployment, launch, tag, merge or
release. PR #2 stays draft. Revert the M4 commit to restore M3 presentation.
