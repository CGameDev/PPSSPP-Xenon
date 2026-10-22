# CCLOS-style in-game menu checkpoint — M5

The in-game menu and notifications now match the launcher's navy/teal style.
**Debug and Release_LTCG both finish full local Rebuilds with 0 warnings / 0 errors.**
Both launcher views and existing save/load/delete/reset actions remain. No Xbox
connection, deployment or launch was performed. Styling remains provisional.

## Scope and preservation

The separate `baseline-overlay/cclos-ingame-menu.patch` changes exactly two
XboxLauncher.cpp bodies: RenderInGameMenu and RenderToast. All other launcher
source matches M4 exactly after removing those bodies, including UpdateInGameMenu,
ShowToast, input bindings, SaveState calls, flags, asset loading, helpers and
primitives. The header and class state are identical. The existing notification
guards, two-second lifetime and last-500ms fade calculation match exactly.

The menu uses static panels, teal focus, five saved/empty slot rows, the existing
five session actions and contextual hints. Settings is labelled unavailable;
its existing handler still closes the menu without opening settings. Notifications
use a bounded navy panel and fitted teal text. No new texture, shader, allocation,
cache policy, animation, decoder, thread, persistence or filesystem query is added.
Five existing save-presence queries per visible menu frame are preserved, not
claimed eliminated. Save/load toasts retain the owner's existing wording; a toast
alone does not establish serialization success.

Among 3,878 source/project/font/image files compared with M4, only launcher.cpp
changes. The generated identity moves m4→m5. Core, GPU, Common, FFmpeg, XboxMain,
session helper and all projects remain unchanged. All 14 launcher host frames
match M4 exactly, preserving both switchable views and RT selection behavior.
Fresh preparation reproduces the built source/helper/header/project bytes.

## Verification

| Check | Result |
| --- | --- |
| Original owner archive authority / all member CRCs | PASS, unchanged |
| Twelve FFmpeg libraries / 436 PPCBE objects | PASS, byte-identical to M4 |
| Full Debug Rebuild | PASS, 0 warnings / 0 errors |
| Full Release_LTCG Rebuild | PASS, 0 warnings / 0 errors |
| Existing host tests | 20 PASS, no local skips |
| Existing numeric/session/emitter/cache/hash regressions | PASS, including native Windows host SEH |
| In-game action snapshots versus M4 | 137 identical; explicit expected requests also pass |
| Actual action source and inline menu activation setter | Exact equality |
| All slots, empty/saved, delete success/failure, held inputs | PASS with host service stubs |
| All five session actions, B cancellation priority and navigation | PASS with host stubs |
| Notification expiry/fade, long text and inactive paths | PASS |
| Actual presentation trace frames | 42 PASS, packed glyph bounds included |
| In-game browser combinations | 136 PASS, no overflow/errors/network |
| Both launcher views / browser combinations | Identical native traces; 56 browser checks PASS |
| Fresh byte replay, unchanged class/session/Core/GPU | PASS |
| Hosted Source preflight on 0dfdac4 | All three jobs PASS, including both launcher and in-game checks |
| Xbox runtime, actual serialization/reset/switching and performance | NOT RUN |

Host checks execute extracted native methods with stubbed device, input and state
services. They never execute Xbox code or write real save states. New code compiles
with warnings as errors; historical reference diagnostics remain visible under
the same comparison policy established in M4.

## Drawing cost and limits

| Scenario | M4 → M5 draws | M4 → M5 triangles |
| --- | --- | --- |
| Normal menu with existing atlas | 127 → 47 | 778 → 518 |
| Menu with notification | 129 → 49 | 806 → 546 |
| Atlas absent | 26 → 47 | 576 → 518 |
| Normal notification during gameplay | 2 → 2 | 28 → 28 |
| Deliberately long notification | 2 → 2 | 128 → 130 |

Normal menus remove the existing 100 moving symbols and their trigonometry.
When the atlas is absent, the old menu already skipped them; the styled panels
then use more draws. A fitted ellipsis can add a glyph in the long notification
fixture. These bounds are recorded rather than treated as free work. Inactive
menu/toast paths still return before resource/drawing work. The emulation loop
has no new call sites; ordinary notifications retain two draws. Emulation/tuning
source is untouched.
Actual Xbox frame-time/performance equivalence still needs hardware measurement.

## Preview, readiness and evidence

Open the [in-game preview](../design/cclos-ingame-preview.html) or
[both launcher views](../design/cclos-preview.html). These are host drawing traces
with simulated states and approximate browser text rasterization, not console
captures. Detailed visual acceptance and TV legibility remain open.

We have reached the **first console smoke-test gate on the software side**.
No additional UI milestone is required before that test. Matching runtime data,
a suitable console/loader, a writable isolated test folder, rollback copies and
test content still need confirmation for that future checkpoint. Read
[CONSOLE_TEST_READINESS.md](CONSOLE_TEST_READINESS.md). First boot, real input and
save/load/reset, repeated returns/relaunches and measured performance are all
unverified; this is not a runtime-qualified release.

[M5 evidence](evidence/m5/) retains full build logs/audits, source and XEX hashes,
host traces, preservation/readiness checks and browser reports. The first Release
attempt hit local disk-space failure. Only older task-generated intermediates
and project libraries inside checked M4 staging roots were removed; sources,
FFmpeg, XEX and milestone packages remain. Both accepted configurations were
fully rebuilt after the final two-draw notification refinement.

[Hosted verification](https://github.com/CGameDev/PPSSPP-Xenon/actions/runs/39720412280)
passes all three jobs on the implementation commit, including strict GCC compilation
of the current launcher/menu fixtures. CI logs and identities are retained under
evidence/m5/. Native Windows SEH was separately checked locally; hosted tests do
not execute Xbox code or establish real serialization.

All four Deploy entries stay explicitly excluded and the local driver refuses
unsafe metadata. M5 performs no console actions. Earlier M1's failed automatic
copy attempt remains historical; it did not transfer or launch. PR #2 stays
draft: no deployment, launch, baseline tag, merge or release. No SDK/private CCLOS
assets, game data or generated binaries are committed. Revert the M5 checkpoint
to restore M4 presentation; [M4](BASELINE_M4.md) and earlier evidence remain at
their recorded commits.
