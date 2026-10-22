# HAD-CV M2 checkpoint

Owner scope: investigate and safely fix the original 62 warnings on PR #2,
fully rebuild Debug and Release_LTCG, keep both views, and perform no Xbox work.

Completed: a separate two-file source patch corrects global declaration alignment
and loader failure returns/cleanup; compile-only PowerPC ABI checks, actual-loader
host failure tests, source replay and both local rebuilds provide evidence.
The original source authority, both views and verified FFmpeg dependencies remain.

The original 62 warnings are gone. Full rebuilds expose 46 Debug/40 Release_LTCG
other legacy warnings, inventoried rather than suppressed. Session-loop exception
handling and numeric/emitter behavior need separate focused regression work.
Runtime, compatibility, performance and detailed visual acceptance remain open.
No console deployment/launch, release or baseline tag is part of this checkpoint.
PR #2 stays draft. See BASELINE.md, WARNING_REVIEW_M2.md and evidence/m2/.
