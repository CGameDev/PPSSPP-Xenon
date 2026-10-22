# HAD-CV M5 checkpoint

Authorized scope: match the in-game menu to CCLOS styling on PR #2, preserve
save/load/reset and both launcher views/performance, rebuild both configurations,
assess console-test readiness, and perform no Xbox deployment or launch.

Frozen parent: M4 6fccfb0. Separate patch modifies only two presentation bodies.
Source comparison preserves the complete remaining launcher, action handler,
activation setter, class state, Core/GPU/Common/FFmpeg and session loop. Existing
notification guards/lifetime/fade stay exact. No new per-frame session call or
resource/cache/filesystem policy is introduced.

Verification: 20 existing tests; previous actual-source regressions; 137 identical
action snapshots plus request expectations; 42 presentation frames; 136 in-game
and 56 launcher browser checks; exact M4 launcher frame equality; fresh source
replay; source/library hashes; both full XDK Rebuilds warning-clean. Normal menu
draw counts fall; absent-atlas and long-ellipsis costs are disclosed in BASELINE.
The initial disk failure and bounded generated-file cleanup are retained.

Preview styling stays provisional. Software is at a first smoke-test checkpoint;
console setup/data and actual boot, operations, transitions and frame times remain
unverified. No console contact, deployment, launch, tag, merge or release. Keep
the PR draft. Detailed gates are in CONSOLE_TEST_READINESS.md; rollback is the M5
commit, preserving earlier source recovery/dependencies/warning fixes.
