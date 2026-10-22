# First Xbox test checklist — all results NOT RUN

Use `results/checklist.csv` for PASS / FAIL / NOT RUN / NOT APPLICABLE, observations
and evidence filenames. PASS requires an observed outcome, not a build, toast or
assumption. The authorization gate must be explicit before console actions.

## Preparation gates

- [ ] P01 Local kit verifier passes; candidate and rollback identities recorded.
- [ ] P02 Compatible console/loader, writable isolated folder and display mode
      are confirmed. All currently unknown environment fields are resolved.
- [ ] P03 Existing working install, config, normal saves and states are backed up
      and readable; original paths recorded in `results/environment.json`.
- [ ] P04 Owner's ISO title, size and SHA-256 recorded; master copy preserved.
- [ ] P05 Explicit authorization for the particular transfer and first launch is
      recorded. **This preparation task does not satisfy this gate.**

## Basic smoke test — after authorization

| ID | Action | Observed pass condition |
| --- | --- | --- |
| S01 | Cold boot chosen M6 configuration | Launcher appears; correct navy/teal shell; readable text and no missing-font/artwork error |
| S02 | Browse Games in grid and compact; RT switch | Same selected item stays visible; folders and long titles fit TV safe area |
| S03 | Select test ISO and press A | Title reaches a recognizable interactive scene; note title/region/disc ID when available |
| S04 | Check buttons, both relevant sticks and audio | Controls respond, sound is present, no sustained crackle/desync over a 5-minute basic check |
| S05 | Open LT+RT+left-stick-click menu | Static navy pause backdrop and right-side menu appear; Slot 1 initially selected |
| S06 | Navigate five slots and switch Left/Right to session | Correct focus/labels; no save/reset triggered just by navigation |
| S07 | B/Continue, including holding then releasing A/B | Gameplay resumes; no unintended PSP action or stuck input; repeat menu open/close three times |
| S08 | At a reproducible scene, save to disposable UI Slot 5 | Menu returns; state file appears under this test folder's PPSSPP_STATE; record filename/size; toast alone is insufficient |
| S09 | Change a visible game condition, then load UI Slot 5 with X | Earlier actual game condition returns, with responsive controls/audio; confirm the saved position/progress |
| S10 | Reopen and delete only UI Slot 5 with Y | Test state disappears; slot shows empty; unrelated state/save files stay unchanged |
| S11 | Choose Reset Game on the session page | Same title restarts and becomes interactive with working audio/input |
| S12 | Choose Exit to Menu; reselect the same ISO | Library returns and same title boots again in the same app session |
| S13 | Create a disposable normal in-game save if supported | Save appears in this test folder's SAVEDATA and is readable after return/relaunch; otherwise record why unavailable |
| S14 | Exit to Xbox and cold-start same candidate again | Controlled exit; app starts again; Recent and isolated test data persist as expected |

Save/load/delete must touch only this isolated test installation. Treat missing or
ambiguous state restoration as FAIL/STOP even if a success toast was displayed.
Do not reuse a main-playthrough slot, rename state files or import old states.
Settings is intentionally unavailable: it is not an acceptance failure that it
closes the menu without opening a settings screen.

## Follow-up after basic gates pass

- [ ] E01 Test an empty-slot load once in the disposable environment; record actual
      error/recovery behavior. Do not infer success from the existing toast text.
- [ ] E02 Complete 20 transitions using `results/transitions.csv`: alternate
      same-title return/relaunch and reset. Check input/audio and any memory
      evidence each time. With only one ISO, do not mark different-title switching
      as passed; record that coverage separately as NOT RUN.
- [ ] E03 If a second title becomes available, test A → library → B → library → A.
- [ ] E04 In a separate M5 application folder, use the same ISO/scene/defaults and
      output mode for comparison. Use clean disposable data for both builds; do
      not share state files across versions. M5 is a comparison candidate, not a
      known-good console rollback.
- [ ] E05 Record FPS/VPS and visual/audio observations. If real frame-time/memory
      instrumentation exists, record median/p95/max and stabilized high-water
      values with its name and raw evidence. Otherwise mark those metrics NOT
      MEASURED; an FPS display or video is not a frame-time measurement.

After each phase retain notes, photos/video as useful, both logs when present,
candidate hash/configuration and the complete isolated data folder. On a crash,
stop and preserve the failure before any retry. Basic smoke-test success is not a
compatibility, performance or release certification.
