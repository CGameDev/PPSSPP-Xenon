# PPSSPP Xenon — User-Provided Xbox Source Overlay

This directory preserves the **original `Xbox.zip` uploaded by the project owner** when the PPSSPP Xenon modernization milestone was prepared.

The source archive is stored losslessly as four ordered Base64 chunks because the repository connector used for the initial seed could not directly write arbitrary ZIP bytes:

```text
Xbox-original-upload.part01.b64
Xbox-original-upload.part02.b64
Xbox-original-upload.part03.b64
Xbox-original-upload.part04.b64
```

## Recommended reconstruction

Codex should **not manually reconstruct this archive**. Use the supplied script from the repository root.

### Windows / PowerShell

```powershell
& .\source-overlay\reconstruct.ps1
```

### Linux / macOS / shell

```bash
bash source-overlay/reconstruct.sh
```

Both scripts:

1. verify that all four source chunks exist;
2. reconstruct `Xbox-original-upload.zip`;
3. calculate SHA-256;
4. refuse to continue if the archive does not match the original upload;
5. extract the source to `source-overlay/extracted/Xbox/`.

## Integrity

Expected SHA-256 of the reconstructed ZIP:

```text
6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35
```

Do not use the overlay if this hash does not match.

## Expected extracted source

```text
source-overlay/extracted/Xbox/
```

This contains the owner-provided Xbox-specific source including the launcher/game-library work, Xbox main loop, host, audio, input, project files, FPS overlay, and JIT allocation support that were supplied with the project.

## Source precedence

The extracted `Xbox/` tree represents newer Xbox-specific work supplied by the project owner and is **authoritative over same-path Xbox files from the older public `metalex10/PPSSPP-X360` source**.

Bootstrap order:

1. Import the complete legacy source tree from `metalex10/PPSSPP-X360` so the project has the full `Common/`, `Core/`, `GPU/`, `native/`, Xbox project files, PPC JIT, and other dependencies.
2. Run the appropriate reconstruction script in this directory.
3. Copy `source-overlay/extracted/Xbox/` over the imported repository's `Xbox/` tree, replacing same-path files with the owner-provided versions.
4. Preserve all other full-source directories from the legacy import.
5. Build and establish the legacy/overlay baseline before beginning modernization.

## Git hygiene

`Xbox-original-upload.zip` and `source-overlay/extracted/` are generated working files. They do not need to be committed after reconstruction unless there is a deliberate project reason.

The four `.b64` files are the archival copy tracked by Git.

## Re-upload verification

This handoff was re-checked and refreshed on **2026-09-03**. See:

`REUPLOAD_VERIFICATION_2026-09-03.md`
