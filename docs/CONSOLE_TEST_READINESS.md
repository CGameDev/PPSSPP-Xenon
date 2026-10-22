# First console test readiness — M5

**Software is at the first console smoke-test gate.** Recovery, Xbox dependencies,
both clean builds and host checks are complete. No further UI milestone is needed
before an initial test. A working console boot or stable game session has not yet
been established, so a percentage-to-release estimate would be misleading.

The owner explicitly said not to deploy or launch. No console was contacted or
inspected. The following is a future test handoff, not authorization to execute it.
Keep automatic deployment excluded and PR #2 draft.

## Cleared locally

- Authentic owner archive and pinned donor; original authority unchanged.
- Both XEX configurations fully linked, zero warnings/errors, hashes recorded in
  evidence/m5/baseline-builds.json; all 436 FFmpeg objects verified PPCBE.
- Existing source-derived regressions and exact action/session preservation.
- Both launcher views, menu layout, input requests and notification timing tested
  with host stubs; no real serialization or Xbox execution is implied.
- Known UI data exists locally: Roboto-Condensed.ttf, ui_atlas.zim, unknown.png and
  ppge_atlas.zim. Existing flash0 files are present. The asset identities and
  limitations are in evidence/m5/console-readiness.json. The absent optional
  splash.png follows the existing failure fallback; the new splash does not draw it.

## Remaining before the first boot

Confirm a compatible owner-controlled Xbox environment/loader and writable,
isolated application folder. Pair the exact candidate XEX with its matching
assembled runtime assets and flash0 data; the local XEX ZIP alone is not a complete
application. Preserve M4 rollback XEX/data and existing config/memstick/state files.
Choose a legal homebrew/autotest or owner-provided test title outside Git. Console
settings, paths, storage and content have not been verified in this task.

## First hardware checkpoint, after separate authorization

1. Cold boot into the library. Check fonts/artwork, TV-safe layout, controller,
   device browsing and both views, including RT selection retention.
2. Start the controlled test title. Record the actual CPU/GPU backend, sound,
   input and frame timing; compilation does not establish an executing PPC JIT.
3. Open the menu with **LT + RT + left-stick click** (existing source binding).
   Check focus, B/Continue, held-button transitions and return to gameplay.
4. Using disposable test slots, verify a real save/load round trip by game state,
   not just toast wording. Check empty slots, deletion and failure feedback, then
   reset and resume with sound/input intact. Preserve backups before state writes.
5. Return to the library, choose the same and a different title, and repeat at
   least 20 transitions. Observe crash recovery, file handles, audio and memory
   after caches stabilize. Collect game:\ppsspp_log.txt and game:\crash_log.txt
   when present; retain failed evidence.
6. Compare M4/M5 with identical title, scene, settings and output mode: median,
   p95/max frame intervals, FPS/VPS, audio underruns, menu cost, switch latency and
   texture/process high-water marks. Include notification visibility. Do not tune
   clocks/workers while establishing the comparison baseline.

A first smoke test can establish basic usability and expose blockers. Completing
that test does not certify compatibility across PSP games or justify a release.
Boot, rendering/audio/input, serialization, reset, recovery, memory stability and
performance are currently **NOT RUN on Xbox**.
