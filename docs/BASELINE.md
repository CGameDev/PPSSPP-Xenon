# Baseline build checkpoint — M1, 2026-10-21

The original owner source is recovered. **Debug and Release_LTCG both build locally.** These are untested Xbox executables, not runtime-qualified releases. [M0](BASELINE_M0.md) and its original failures remain historical evidence.

## Authentic source recovery

The local owner download `PPSSPP-Xenon-Codex-Milestone-v1.0.zip` matches recorded package SHA-256 `ea8eaf39d8899f231d1ba1cee7687cbc67e071154ed9972f2883950c8efc8a3b`. Its embedded 56,233-byte `Xbox-original-upload.zip` matches the unchanged original authority:

`6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35`

All 30 ZIP entries pass CRC. Compared with the damaged copy, only byte offsets 5883 and 42887 differ. Base64 parts 1 and 4 were restored directly from the authenticated archive; parts 2/3 and the expected hash are unchanged. No source was guessed or manually repaired. The recovery receipt records before/after part hashes and all recovered file hashes.

## Inputs and assembly

- Legacy donor: `metalex10/PPSSPP-X360@540db97d96136b2139e5f12dd3c0bb18f2e1cd1f`.
- Modern reference only: PPSSPP v1.20.4, `fa50bb1976065c4f8b1b47af227d367fe9771555`; no core backport.
- `prepare_baseline.py` reads committed donor objects, preserves notices and overlays authentic owner Xbox files last into fresh, ignored staging. Its pristine manifest covers 6,409 files. Donor Git metadata and untracked build output are excluded.
- The missing stb_truetype v1.26 header is pinned to upstream commit `6e9f34d5429cf16790ec43c9bac3f1ee4ad1f760`, retained unmodified with its license. The owner launcher already references that API.
- Original source is reconstructed from the public pinned donor rather than duplicating thousands of third-party files in this PR. Project patches, dependency source and recipes are tracked here; SDK material, generated trees, libraries and XEX files are excluded from Git.

## Xbox FFmpeg

Six static libraries were rebuilt from the donor's existing FFmpeg source and Xbox recipes for Debug (`ppcD`, `-MTd`) and Release (`ppc`, `-MT`). Both detect 32-bit PPC, big-endian and w32threads, with AltiVec/network/programs disabled as in the historical recipe. No codec source or feature selection changed. Configure reports LGPL 2.1-or-later.

Host tools: GNU Make 3.82 built from GNU source with VS2010, C99-to-C89 1.0.2 from upstream, and installed Git Bash. Native Make requires Windows source paths and bypassing the old MSVC dependency-scanner pipeline. Header changes require a fresh build tree. The driver copies resulting archives to the required `.lib` names; no desktop/prebuilt target libraries are borrowed.

Every object header was verified: **218 PPCBE objects per profile, 436 total**, machine `0x01F2`. Tool/configuration/library hashes are in [M1 evidence](evidence/m1/).

## Bounded compatibility changes

The archival owner source remains pristine. `baseline-overlay/` applies these separate changes to staging:

1. Map two newer folder-atlas names to the existing legacy folder glyph. Both grid/list modes remain.
2. Bridge the absent DeleteSlot API with the core's existing current-title slot filename generator and file helpers. Empty/missing paths and failures are handled; the toast reports failures truthfully. A C++98 host test exercises disposable files and preserves unrelated slots.
3. Mark every legacy Deploy entry `ExcludedFromBuild=true`; correct the Release_LTCG FFmpeg library path. The local build driver refuses missing exclusions.
4. Embed a guarded combined-source identity instead of `unknown`.

Fresh preparation and patch replay were compared against the exact built files. No emulation clock/worker settings, JIT, GPU algorithms, audio or session loop were changed.

## Verification

Installed compilers: VS2010 SP1 host `16.00.40219.01`, XDK PowerPC `16.00.11886.00`; .NET Framework 4 MSBuild with normal project references.

| Check | Result |
| --- | --- |
| Original owner archive hash / every ZIP CRC | PASS |
| Python host tests / compilation | 17 PASS / PASS |
| C++98 deletion helper, VS2010 host | PASS, disposable fixtures |
| Fresh assembly and compatibility replay | PASS |
| Debug/Release FFmpeg builds and all object architectures | PASS |
| Debug Xbox solution build | PASS, local XEX |
| Release_LTCG Xbox solution build | PASS, local XEX; 62 warnings retained |
| ISO/CSO/PBP boot, sound/input, saves/states/switching | NOT RUN |
| Xbox memory, frame pacing, FPS/VPS and regression | NOT RUN |
| Detailed CCLOS styling / production renderer | Provisional / not integrated |

Final XEX sizes/hashes are in [baseline-builds.json](evidence/m1/baseline-builds.json). The XDK embeds timestamps/paths: repeatable procedure does not imply byte-for-byte deterministic binaries across machines. Final incremental build receipts retain earlier compile/link warnings rather than calling the entire build warning-free.

## Retained failures and limits

The first restored build exposed the font header, then atlas/API mismatches. Initial Release_LTCG linking preceded library staging and failed; it passed after dependencies were staged. Failures are preserved.

After first successful Debug image generation, the SDK Deploy target automatically attempted `xbecopy` despite DeployOnBuild=false. It failed with X1001, unable to connect to an empty/default target. No transfer or launch succeeded. The SDK invokes Deploy after ImageXex. Explicit project metadata exclusions now prevent its copy task; subsequent local Debug/Release_LTCG builds passed. Do not rely on DeployOnBuild alone.

Release_LTCG retains existing C4742/C4744 cross-unit GPUgstate/GPUStateCache alignment/type warnings and C4715 missing-return warnings in owner artwork loaders. Earlier compilation also reports SEH/destructor and comment-continuation warnings. These are unresolved runtime risks. No warnings were suppressed to obtain a pass.

No baseline tag, release, runtime acceptance or performance improvement is claimed. Keep PR #2 draft. Next: investigate retained warnings and obtain a separately authorized hardware checkpoint with rollback, exact identity, boot/audio/input/save/state checks and twenty session transitions. Both UI views remain selected; detailed visual design remains open.
