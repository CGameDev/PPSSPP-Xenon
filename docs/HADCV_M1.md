# HAD-CV M1 checkpoint

Owner request: recover authentic Xbox source and missing Xbox FFmpeg dependencies,
continue the baseline on PR #2 and keep both UI views.

Delivered: byte-exact source recovery, separate recovery commit, verified source
assembly, source-built Debug/Release Xbox FFmpeg, bounded compatibility patches,
local-only build driver, Debug/Release_LTCG XEX outputs, host tests and evidence.
The expected archive hash is unchanged. M0 failures remain in history/reports.

Both original grid/list modes and both design concepts remain. No final styling
is locked; no production CCLOS renderer, CPU tuning, session rewrite or modern
core backport is included.

Build gates pass. Runtime, savedata/states/switching, performance, retained warnings
and detailed visual acceptance remain open. No release or baseline tag is created;
PR #2 stays draft. Next: warning review, then separately authorized hardware checks.

One legacy SDK auto-copy attempt failed before deployment was explicitly excluded.
No transfer or launch succeeded. Current drivers reject enabled deployment metadata;
successful final builds operate locally. See BASELINE.md.
