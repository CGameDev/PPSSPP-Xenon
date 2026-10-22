# M7 — Xenon PGF font bit-reader correction

**Local candidate only; not tested on Xbox.** The owner's M6 Release_LTCG launch
hard-locked the console. The supplied log narrows the investigation and exposes
a reproducible font-decoding defect, but does not prove every cause of the hang.
No console connection, deployment or launch was performed by the agent.

## Evidence from the owner's files

`ppsspp_log.txt`, `ppsspp.ini` and `recent.txt` were read from the supplied paths
and copied unchanged to local incident storage. Raw user files remain outside
Git; their lengths/hashes are in `evidence/m7/incoming-evidence.json`. The owner
reports that no `crash_log.txt` was found. No ISO was accessed.

The log identifies the M6 version, loads the game's EBOOT, initializes memory and
the PPC JIT dispatcher, and starts `user_main` and `GameMain`. It completes loading
`jpn0.pgf`. The final entry is **37:13:891**, reading a PGF header immediately
after starting `ltn0.pgf` (67,660 bytes). This is the last recorded operation, not
a proven instruction where the console froze. It establishes more progress than
the screenshots alone, but not interactive gameplay or full JIT correctness.

The initial missing-config/controller messages are followed by successful config
save messages, consistent with first creation. The log also reports missing PRX
keys 59/5B, faked undecryptable modules and a deferred-thread-info error; execution
continues to font loading afterward. These remain separate compatibility findings;
M7 does not alter decryption or thread/callback handling. INI settings agree with
the existing owner defaults, including JIT requested, separate CPU/I/O threads,
five workers and 111 MHz PSP clock. No tuning change is included.

## Confirmed source defect and bounded correction

The PGF header/metric tables already use little-endian wrappers, but `getBits`
reads packed bitstreams through `const u32 *`. That interprets each word in native
host byte order. On Xenon, glyph tables and bitmap fields consequently decode
differently from the file's little-endian bit order.

The separate `baseline-overlay/pgf-endian-fix.patch` changes only the `getBits`
body in `Core/Font/PGF.cpp`:

- Read words through the existing `u32_le` type; convert each word once to `u32`.
- Handle a zero-bit request without a memory read.
- Handle an exact 32-bit boundary in the single-word branch, avoiding an
  unnecessary next-word read and undefined 32-bit mask shifts.
- Use unsigned masks and accumulation for widths up to 32 bits.

No font asset, PGF format, state layout, glyph cache, allocation, thread, UI,
save/load/reset action, GPU/JIT/session code or emulator setting changes. The
helper remains constant work: zero, one or two word reads per call, with no new
loop/allocation. Correct endian conversion is required work; Xbox timing has not
been measured. This is an original local correction, not an upstream backport.

## Reproduction and validation

The actual old/new reader bodies are extracted from staged source. The host
fixture explicitly models native big-endian words for the old reader and
little-endian words for the correction, then compares against an independent
bit-at-a-time oracle. It does not execute PPC machine code.

| Check | Result |
| --- | --- |
| Widths 0–32 and starting bit positions 0–255 | 8,448 oracle cases PASS |
| Exact-boundary word count and zero-width no-read | PASS |
| Character/glyph pointer tables for all 18 bundled fonts | PASS |
| `ltn0.pgf` old BE invalid glyph-start offsets | 76 of 324; corrected 0 |
| `jpn0.pgf` old BE invalid glyph-start offsets | 193 of 29,075; corrected 0 |
| Scope after reversing the new patch | Only `getBits` body differs |
| 23 existing unit tests and actual-source regressions | PASS, no local skips |
| M6 launcher/menu traces and 137 action snapshots | Exact equality |
| Fresh replay across 3,876 source/helper/project/assets/identity files | Exact bytes |
| Changed compared with M6 | `Core/Font/PGF.cpp` and generated identity only |
| Twelve FFmpeg libraries / 436 PPCBE objects | Unchanged |
| Full Debug Rebuild | PASS, 0 warnings / 0 errors |
| Full Release_LTCG Rebuild | PASS, 0 warnings / 0 errors |
| Four Deploy exclusions | Explicitly excluded |
| M7 Xbox runtime, resolved hard lock and performance | NOT RUN / NOT ESTABLISHED |

The MSVC fixture uses production-equivalent `/W3 /WX`; an initial desktop `/W4`
probe flagged the inherited bit-count narrowing in both old/new readers. No
production warning suppression or project warning-level change was made. GCC CI
adds undefined-behavior instrumentation to the host reader fixture.

Reproduce the font regression after current preparation:

```text
python tests/run_pgf_regressions.py --source-root artifacts/baseline-m7 --build-root artifacts/m7-pgf-tests
```

Both full build logs, warning audits, library identities, preservation receipt and
font-table results are in `docs/evidence/m7/`. The original owner archive remains
unchanged. The older M6 build/kit and owner failure evidence are preserved.

## Candidate and next checkpoint

The local M7-PGF candidate ZIP contains separate Release_LTCG/Debug application
folders with matching runtime files and empty test saves, plus a local verifier.
It contains no owner ISO, logs/config/saves or SDK files. It has not been deployed
or launched. Do not overwrite the failed M6 application/evidence or working backup.

A future separately authorized retest should isolate this font correction: use a
new folder and the same ISO, capture the version/complete log, and check whether
all internal fonts complete loading and gameplay becomes interactive. Preserve
failure evidence after any repeat lock. The inherited consecutive first-launch
frame starts and graphics-state/thread issues remain audit targets; deliberately
changing none of those in M7 keeps this candidate's comparison interpretable.
Missing encrypted-module support may still limit this title independently.

Rollback is the M6 source/build snapshot or the owner's verified working install;
M6 itself failed this title and M5 remains untested. Reverting the M7 implementation
restores the prior reader. This correction is not a claim of a successful console
fix, general malformed-font safety or compatibility/performance certification.
