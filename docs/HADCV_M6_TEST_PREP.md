# HAD-CV M6 first-test preparation

Authorization: prepare required runtime files, test checklist and rollback
instructions; owner has an ISO available. No console deployment or launch.

The local v1 smoke kit reuses the exact recorded M6 Release_LTCG/Debug XEX files,
with matching assets, 18 flash0 fonts and language files. Separate exact M5
candidates provide comparison/fallback folders. All four application folders use
fresh empty test data. No ISO was accessed or included. M5 is not console-proven;
the owner's unchanged working install and verified offline backup take priority.

Package validation binds XEX hashes to committed build receipts and each runtime
file to its pinned source manifest. All 349 immutable files round-trip through
the ZIP with matching sizes/hashes; ZIP CRC and 24 required directories pass.
Python 3 and PowerShell 7 local verification pass. A corrupted-file negative
control fails as expected. Windows PowerShell 5 blocked the optional PS1 under
the existing execution policy; the policy was left unchanged and Python is the
documented primary checker. All 23 unit tests and existing host regressions pass.

Checklists cover the owner's ISO, both views, audio/input, menu chord/pages,
disposable Slot 5 save/change/load/delete, reset, same-title return/relaunch,
normal save persistence, 20 transitions and a controlled M5/M6 comparison.
Different-title switching remains NOT RUN with only one available ISO. Metrics
without real instrumentation stay NOT MEASURED. No native executable/source,
setting or performance behavior was changed; another rebuild was not needed.

The ZIP remains local. Only packaging code, docs and validation receipts are
tracked on PR #2; no binaries, fonts, SDK files, ISO or savedata are committed.
Console/loader compatibility, intended writable target, backup confirmation and
explicit transfer/first-launch authorization remain future gates. No Xbox was
contacted. All actual hardware results remain NOT RUN.
