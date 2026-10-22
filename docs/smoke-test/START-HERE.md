# M6 first Xbox smoke-test kit

**Prepared locally only. No Xbox connection, transfer or launch has occurred.**
All hardware results start as NOT RUN. These instructions describe a future,
separately authorized manual test; the kit contains no deployment/launch tool.

## What is included

| Folder | Purpose |
| --- | --- |
| `candidate/Release_LTCG/` | Primary M6 smoke-test/performance candidate |
| `candidate/Debug/` | Separate M6 diagnostic candidate |
| `rollback/M5-Release_LTCG/` | Previous release candidate, not Xbox-proven |
| `rollback/M5-Debug/` | Previous diagnostic candidate, not Xbox-proven |
| `evidence/` | Build identities, local validation and source provenance |
| `licenses/` | Available source/dependency license notices |
| `results/` | Blank checklist, transition and environment records |

Each application folder contains `xx.xex`, matching `assets/`, `flash0/`,
`lang/`, and empty `memstick/PSP/` test-data directories. The executable name is
unchanged. Keep the folder together: `game:` must resolve to that executable's
application directory. Do not combine candidate and rollback files.

FFmpeg libraries are linked into the XEX; their `.lib` files, compiler/SDK files,
debug PDBs and browser previews are not runtime payload. The donor's optional
`assets/splash.png` is absent; the current splash uses its existing fallback.
No user ISO, saves, config, recent list or credentials are included.

## PC checks now

1. Extract the ZIP into a new local folder. From a terminal in that folder run:
   `python .\VERIFY-LOCAL.py` (Python 3, standard library only).
   This reads local files and checks all immutable packaged file hashes/sizes and
   required directories. Editable `results/` records, an added ISO and generated
   runtime data are outside that inventory. It has no network, console,
   copy-to-device or launch action.
   `VERIFY-LOCAL.ps1` is an optional alternative where script policy permits it;
   it passes under this PC's PowerShell 7. Windows PowerShell 5 blocked it under
   the current policy, which was left unchanged. The Python checker needs no
   PowerShell policy change.
2. Read `CHECKLIST.md` and `ROLLBACK.md`. Fill `results/environment.json` with
   the intended console/loader, display/storage, selected configuration and ISO
   title. Unknown fields stay NOT CONFIRMED; do not guess hardware compatibility.
3. Your ISO can be the first test title. Keep its master copy outside the kit.
   Record its local size and SHA-256 with `Get-FileHash -LiteralPath '<ISO path>'
   -Algorithm SHA256` and enter the value in the environment record. There is no
   need to upload it or add it to Git. No ISO was inspected in preparing this kit.

## Before a later authorized console test

- Confirm the owner-controlled console and loader can run these XDK-built XEX
  candidates, and select a writable, new application folder. No stock-retail boot
  compatibility or specific console setup is inferred from build success.
- If one exists, make an offline backup of the working installation **and its entire
  data/config tree**, including any external memstick path it uses. Verify the
  backup is readable. Leave the original installation untouched. If there is no
  prior working install, record that explicitly; the included M5 remains untested.
- Start with `candidate/Release_LTCG/`, preserving its entire directory tree.
  Debug is separate: do not swap its executable into the release folder during a
  test. Record which configuration was actually selected.
- After explicit authorization only, place a **copy** of your ISO beside that
  selected folder's `xx.xex`, using a short name such as `test.iso`. Select it from
  Games; it need not be named `psp.iso` because this build uses the launcher.
  The ISO is an intentional extra file outside the shipped checksum inventory.
- Keep all test saves disposable. Do not import your main saves or existing
  `ppsspp.ini`, `controls.ini`, `recent.txt` or `searchdirs.txt` for the first test.
- Keep `results/` and evidence on the PC; only the selected application folder is
  the prospective runtime payload. No transfer or launch is authorized yet.

## Runtime paths to preserve and collect

| Application-relative path | Use |
| --- | --- |
| `ppsspp.ini`, `controls.ini` | Loaded configuration; startup saves config |
| `recent.txt`, `searchdirs.txt` | Launcher persistence when produced |
| `memstick/PSP/SAVEDATA/` | Normal in-game saves |
| `memstick/PSP/PPSSPP_STATE/` | Menu states (`.ppst`) and optional thumbnails (`.jpg`) |
| `ppsspp_log.txt`, `crash_log.txt` | Logs if produced; absence alone is not a pass |

UI slots 1–5 map to core filename suffixes 0–4. Use **UI Slot 5** for the disposable
round trip; identify the actual title/version filename rather than renaming it.
At startup this build sets `game:\memstick\` and `game:\flash0\`. A fresh isolated
folder therefore keeps the intended test data away from the original install;
verify those locations after boot before trusting a save test.

## Performance context

The preserved owner defaults request PPC JIT, DirectX9, 111 MHz PSP clock, five
workers, separate CPU/I/O threads and 2x PSP output. Startup assigns several
settings and writes config, so INI editing is not a reliable way to override those
values here. They are not newly recommended tuning. Record them as source
requests, and use the same defaults/title/scene/output for M5–M6 comparisons.
An executing backend, real settings and frame times still need observation.

The menu chord is **LT + RT + left-stick click**. Avoid RB+RT while measuring:
that is the existing fast-forward binding. The pause backdrop is static navy;
Left/Right switches slots/session. Settings is unavailable; its legacy selection
closes the menu. Both launcher views remain; Recent stays grid-only.

Complete the basic gates first, then the soak/comparison phase. With one ISO,
same-title return/relaunch/reset is testable; different-title switching remains
NOT RUN until a second title is available. Stop on corruption, repeated crash,
missing font/artwork, broken input/audio, or any ambiguous save/load result.
Follow `ROLLBACK.md`; do not continue by writing over existing data.
