# Build and recovery instructions

**Current result: no qualified Xbox executable.** Start with [BASELINE.md](BASELINE.md).

Run the read-only preflight from this repository root with Python 3:

```powershell
python tools/verify_source_overlay.py
python -m unittest discover -s tests -v
python -m compileall -q tools tests
```

The preflight prints JSON to stdout and exits 0 for PASS, 1 for FAIL. It does not
write output files. Redirect stdout to preserve a receipt if desired. As of M0,
the real archive must fail; synthetic test success does not override that result.
Do not run the older destructive reconstruction scripts against a directory
holding previous good extracted source. They remain preserved historical tools.

After trusted archive recovery, reconstruct with the documented hash check in a
fresh staging location, preserve the complete donor licensing/attribution and
copy owner Xbox files last. Do not overwrite local changes or import donor Git
metadata. Pin the donor and modern reference identities in BASELINE.md.

The inspected solution entry is `Xbox/PPSSPP.sln`; its executable project is
`Xbox/xx/xx.vcxproj`. `Xbox/Xbox.vcxproj.vcxproj` is a different, older project,
not the solution's executable target. The recovered owner solution must be
rechecked instead of assuming this structure is unchanged.

Use the licensed VS2010/XDK environment for `Debug|Xbox 360`, then
`Release_LTCG|Xbox 360`. Build locally with `/t:Build`, not Deploy. Verify targets
and disable deployment; M0 does not authorize any console connection. Prefer
normal project-reference builds for baseline qualification. Record command,
environment/compiler identity, clean source manifest, exit code, dependencies,
XEX and resource hashes and all warnings/errors.

Resolve the missing FFmpeg libraries from compatible source/configuration under
`ffmpeg/Xbox/ppcD/lib` (Debug) and `ffmpeg/Xbox/ppc/lib` (Release). Inspect the
Release_LTCG relative library directory: the legacy project differs from Release
and must be validated. Keep FFmpeg and all included codecs' license notices.
Do not commit SDK headers/libraries, generated build output or a borrowed XEX.

The legacy version-generation command currently produces `unknown`; ensure Git
is found and exact version provenance is embedded before accepting a baseline.
Compilation, linking, boot, behavior and performance each need separate receipts.
