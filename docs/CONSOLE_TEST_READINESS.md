# First console test readiness — M6

## M7 local correction candidate

The owner supplied the M6 failure log/config/recent; no crash log was found. The
log stops during Latin-font parsing. A reproduced PGF bit-reader endian defect is
corrected in a separate M7 candidate, with both full builds warning-clean and
UI/action traces unchanged. See [PGF_FONT_FIX_M7.md](PGF_FONT_FIX_M7.md).
The complete lockup is not confirmed resolved; M7 has not run on Xbox. Preserve
M6 evidence. No agent deployment/launch is authorized or performed.

## Latest owner-run result: launch failed

On 2026-10-22 the owner reported M6 Release_LTCG displaying the launcher and ISO
artwork, then a black-screen hard lock after launch. Guide did not respond and
the console required restarting. Game boot is **FAIL**, not validated. Preserve
existing logs/config before any retry. See [SMOKE_TEST_REPORT_01.md](SMOKE_TEST_REPORT_01.md).
The agent performed no Xbox connection, deployment or launch. Source audit found
two consecutive inherited first-launch frame starts; their causal role is not
established. No native change or fix claim is made yet.

The readiness/kit instructions below record the pre-test handoff. Remaining
gameplay/save/reset/performance gates have not passed. The sealed kit is retained
for evidence and is not a recommendation to repeat the failed launch unchanged.

## Pre-test handoff

**Software is at the first console smoke-test gate.** Recovery, Xbox dependencies,
both clean builds and host checks are complete. No further UI milestone is needed
before an initial test. A working console boot or stable game session has not yet
been established, so a percentage-to-release estimate would be misleading.

The owner explicitly said not to deploy or launch. No console was contacted or
inspected. The following is a future test handoff, not authorization to execute it.
Keep automatic deployment excluded and PR #2 draft.

## Prepared local test kit

The M6 smoke-test kit now contains both exact M6 configurations with matching
`assets/`, `flash0/`, `lang/` and empty disposable test-data folders. Separate M5
Debug/Release folders provide prior candidates, not Xbox-verified backups.
An immutable file manifest, PC-only verifier, ISO-based checklist, blank result
records and rollback instructions are included. The owner's ISO is available but
has not been inspected or bundled. No configuration/save data was imported.

Start with [smoke-test/START-HERE.md](smoke-test/START-HERE.md),
[CHECKLIST.md](smoke-test/CHECKLIST.md) and [ROLLBACK.md](smoke-test/ROLLBACK.md).
Reproduce locally with `python tools/prepare_smoke_test.py --destination <new-local-folder>`
after reconstructing the two recorded stages/builds. Preparation validates XEX
hashes against the committed M5/M6 receipts and all runtime bytes against each
source manifest, then refuses an existing destination or ZIP. It has no network,
deployment, launch, delete or restore operation. The kit remains local; binaries,
fonts, flash0 and any eventual ISO are not committed or attached to GitHub.

Future console/loader compatibility, actual writable target path, backup status
and explicit first transfer/launch authorization are still unresolved gates.
This package does not establish a working boot or Xbox performance.

## Cleared locally

- Authentic owner archive and pinned donor; original authority unchanged.
- Both XEX configurations fully linked, zero warnings/errors, hashes recorded in
  evidence/m6/baseline-builds.json; all 436 FFmpeg objects verified PPCBE.
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
application. Preserve M5 rollback XEX/data and existing config/memstick/state files.
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
6. Compare M5/M6 with identical title, scene, settings and output mode: median,
   p95/max frame intervals, FPS/VPS, audio underruns, menu cost, switch latency and
   texture/process high-water marks. Include notification visibility. Do not tune
   clocks/workers while establishing the comparison baseline.

A first smoke test can establish basic usability and expose blockers. Completing
that test does not certify compatibility across PSP games or justify a release.
Boot, rendering/audio/input, serialization, reset, recovery, memory stability and
performance are currently **NOT RUN on Xbox**.
