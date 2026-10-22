# Rollback and evidence preservation

These are future manual instructions. No console file has been changed by kit
preparation. No script in this kit deploys, launches, deletes or restores files.

## Preferred rollback: leave the working installation untouched

1. Before a later authorized test, copy the entire existing working application
   and its actual config/memstick/state locations to an offline PC backup. Record
   the original application path, selected executable, loader shortcut and backup
   destination. Confirm backup files are readable before starting.
2. Test M6 in its own new folder. Do not replace the working application's XEX or
   reuse its saves/config. Each configuration has its own `game:` root and data.
3. If anything fails, stop the test application using the console's normal exit
   path. If unresponsive, use the owner's normal recovery/power procedure; do not
   keep pressing save/load/reset or repeatedly relaunch a crashing title.
4. Preserve the failed M6 folder and its logs/state/config on the PC before
   changing it. Label the configuration, ISO identity, step, observed failure and
   whether a forced shutdown was needed.
5. With separate authorization for any launch, return to the original working
   application/shortcut. Since its files were not replaced, no file restoration
   should be necessary. Keep M6 test saves separate from your main playthrough.

## If the original installation was accidentally overwritten

Stop. Preserve the changed installation first. Restore the **entire matching
pre-test backup** to its recorded original path, with the emulator closed. Do not
merge newer test states/config into the backup or restore only an XEX over a
different runtime-data set. Confirm restored hashes/file inventory against your
backup, then separately authorize and observe a launch. Never delete the only
copy of either the backup or failure evidence.

## Included M5 candidates

`rollback/M5-Release_LTCG/` and `rollback/M5-Debug/` contain complete previous
software candidates with matching runtime data and fresh empty test saves. Their
XEX hashes come from the recorded M5 build evidence. **Neither has been verified
on your Xbox.** They are useful for an isolated M5/M6 comparison or software
fallback, but cannot replace a known-working owner backup.

Keep their whole folders intact. For a future comparison, use the matching
configuration and a separate copy of the same ISO. Do not copy M6 states into M5,
mix candidate/rollback assets, or assume serialized states are cross-build safe.
If there is no known-working installation yet, record rollback as an untested
earlier candidate plus recovery to the console's normal loader/dashboard.

## Data and failure record

Preserve `ppsspp.ini`, `controls.ini`, `recent.txt`, `searchdirs.txt`, the entire
`memstick/`, `ppsspp_log.txt` and `crash_log.txt` when produced. Empty/missing logs
are observations, not a pass. Collect files only while the emulator is stopped.
The first test intentionally uses disposable data; preserving those files must
not overwrite pre-existing saves or the offline working-install backup.
