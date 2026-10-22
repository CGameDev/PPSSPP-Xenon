# First owner-reported Xbox test — 2026-10-22

**Log follow-up:** the owner has now supplied ppsspp_log.txt, ppsspp.ini and
recent.txt and reports no crash log. The log reaches GameMain and stops during
ltn0.pgf parsing. A reproduced font-reader byte-order defect has a locally built
M7 correction candidate; see [PGF_FONT_FIX_M7.md](PGF_FONT_FIX_M7.md). No M7 Xbox
test or complete lockup resolution is claimed. The initial triage below is
retained as the pre-log record; raw incoming files remain local outside Git.

**Game launch FAIL: full console lockup reported. Do not treat M6 as a validated
gameplay candidate or repeat the launch before preserving failure evidence.**

## Observed and reported

The owner supplied two screenshots: the native launcher showing the selected ISO
and its artwork, followed by a black screen with a small green zero. The visible
filename is `Street Fighter Alpha 3 Max (USA).iso`. The owner confirmed **M6
Release_LTCG** and that the Guide button stopped responding; restarting the
console was required. This was an owner-run test. The agent did not connect,
deploy, launch or reproduce the issue on Xbox.

| Gate | Evidence/status |
| --- | --- |
| Launcher rendering, ISO listed and artwork visible | OBSERVED in owner screenshot |
| Entire ISO integrity or successful game boot | NOT established by artwork |
| Launch to interactive gameplay | FAIL, owner-reported hard lock |
| Guide response after freeze | No response, owner confirmed |
| Audio, save/load/delete/reset and session switching | NOT VERIFIED in this test |
| Actual FPS/frame times/memory stability/backend | NOT MEASURED / NOT VERIFIED |
| Exact executable hash on console | Not yet retrieved |
| Console/loader/storage details | Not yet recorded |

The packaged M6 Release_LTCG reference hash is
`f4941219ce9094de417efb96800174eca0b49fbd4eb2d042ea932e8b2aaa2856`.
Its local native build commit is `6657e9f0b0935fa108fb55eab72d151ed4a5a34c`.
This identifies the intended candidate; it does not authenticate the console's
copy. Local build/host/CI passes remain valid evidence of those checks, not of
runtime correctness. M5 has not been tested in this report.

## Source findings, not a root-cause claim

`XboxFpsOverlay.cpp` initializes `currentFps` to zero and updates it after a
sampling interval. The green zero is consistent with that startup display; it is
not an error code. The existing session helper calls the overlay on a next-frame
path. This suggests some launch progress if the expected XEX is running, but
does not locate the subsequent stall or prove usable gameplay.

The inherited first-launch branch calls `xbhost->BeginFrame()` after initialization,
then calls it again at the common entry immediately before `RunEmulationSession`.
`XboxHost::BeginFrame` delegates to `DX9::BeginFrame`, whose Xbox path calls
`BeginTiling`. There is no matching frame-end call between those two first-launch
starts. This is a concrete lifecycle audit target, inherited unchanged from the
owner source; it is not yet tied to the observed lockup. Graphics state after
the FPS overlay and CPU/GPU synchronization also require runtime evidence.

The file logger explicitly flushes each emitted message. However, channel enable/
level filtering and where execution stalled affect what survives a hard lock.
`crash_log.txt` is written by the existing exception filter, not by a general hang
watchdog, so an absent crash log would not rule out a hang. No setting, JIT/thread
profile, rendering backend or native source has been changed for this triage.

## Preserve and obtain next

With the emulator closed, copy existing `ppsspp_log.txt`, `crash_log.txt` if it
exists, and `ppsspp.ini` from the **same application directory as the tested
`xx.xex`** to the PC. Attach these text files, or report which are missing/empty.
Do not relaunch just to create them. No ISO upload is needed. Also retain the
tested XEX, application folder and any test data without overwriting them.

Screenshots were preserved locally outside Git; game artwork is not committed.
Their SHA-256 identities are:

- Launcher: `b08facdf9892f32726922fee9d59d624ea9e2aa170cf5b8a2b22293bfc35807b`
- Black screen: `522d781dda29d657802b76a177b85809900f0e9c4eb5a1e355b4f3b73c849f02`

Next decision: inspect logs/config and match the actual XEX identity, then prepare
a bounded correction or diagnostic build based on that evidence. Any future
transfer or launch remains separately authorized. The sealed v1 kit and original
build receipts remain unchanged as historical evidence.
