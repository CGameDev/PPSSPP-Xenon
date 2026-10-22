# HAD-CV M7 checkpoint

Trigger: owner-reported M6 Release_LTCG hard lock; supplied log/config/recent,
with no crash log found. Frozen parent: `32d0cdb50237bf241c04a2944bbbbdca64abb875`.

The last log entry occurs during Latin-font PGF parsing. Reproduced a native
big-endian bit-reader defect against pinned runtime fonts: ltn0 produces 76/324
invalid glyph-start offsets under the old BE model. An isolated correction uses
the existing little-endian word wrapper and defined 0/32-bit boundary handling.
Only getBits and generated build identity change; no UI, action, GPU/JIT/session,
cache/allocation or tuning change. Original source/archive remain preserved.

8,448 bit-oracle cases; all 18 font tables; exact UI/action trace equality;
23 existing tests/regressions; exact 3,876-file replay; byte-identical FFmpeg;
both full Rebuilds zero warnings/errors; four Deploy exclusions. Local candidate
kit is hash/CRC checked. Source/emulation limits and initial host-warning policy
are explicit in PGF_FONT_FIX_M7.md and evidence/m7.

Confirmed source defect, not a confirmed complete explanation/resolution of the
hardware lockup. Old PRX module warnings and consecutive inherited frame starts
remain unchanged. Raw owner files stay local. No Xbox contact/deploy/launch;
M7 runtime/performance NOT RUN. Keep PR #2 draft and preserve M6 failure evidence.
