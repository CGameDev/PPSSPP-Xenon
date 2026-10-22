# Current shell validation

For the first hardware handoff, use [smoke-test/START-HERE.md](smoke-test/START-HERE.md).
`tools/prepare_smoke_test.py` assembles local candidate/rollback folders only; its
integrity/no-overwrite tests are included in normal unittest discovery. No test
or packaging command authorizes console transfer or launch.

Prepare M6 as described in [BUILD_XBOX360.md](BUILD_XBOX360.md).
Use the VS2010 x86 host environment locally, or g++ in CI:

```text
python -m unittest discover -s tests -v
python tests/run_m3_regressions.py --source-root artifacts/baseline-m6 --reference-root <pinned-legacy> --build-root artifacts/m6-host-regressions
python tests/run_cclos_launcher.py --source-root artifacts/baseline-m6 --build-root artifacts/m6-launcher-tests --preview-data design/cclos-launcher-frames.js
python tests/run_cclos_ingame.py --source-root artifacts/baseline-m6 --build-root artifacts/m6-ingame-tests --preview-data design/cclos-ingame-frames.js
python tests/run_cclos_shell.py --source-root artifacts/baseline-m6 --build-root artifacts/m6-shell-tests
```

The shell tracers reconstruct M5 by reversing M6 in disposable artifacts, then
compile actual methods and compare host work/actions. Current code uses warnings
as errors. The boundary check requires every other source body to match after
explicitly listed geometry/include/blank-separator substitutions.

Run both full Rebuilds using the guarded build driver; audit both logs. Optional
Playwright checks `tests/cclos_preview_smoke.cjs` and
`tests/cclos_ingame_preview_smoke.cjs` cover 192 scene/viewport combinations with
fictional fixtures. No test here runs Xbox code or touches real savedata.

Hardware results remain NOT RUN. Use [CONSOLE_TEST_READINESS.md](CONSOLE_TEST_READINESS.md)
only after separate authorization. Host counts do not establish real serialization,
game compatibility, memory stability or Xbox frame times.
