# PPSSPP Xenon — User-Provided Xbox Source Overlay

This directory preserves the **original `Xbox.zip` uploaded by the project owner** when the PPSSPP Xenon modernization milestone was prepared.

The GitHub connector used to seed this repository can write UTF-8 text files but not arbitrary ZIP bytes. To preserve the uploaded source exactly, the ZIP was Base64-encoded and split into four ordered text chunks:

```text
Xbox-original-upload.part01.b64
Xbox-original-upload.part02.b64
Xbox-original-upload.part03.b64
Xbox-original-upload.part04.b64
```

## Integrity

Expected SHA-256 of the reconstructed ZIP:

```text
6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35
```

Do not use the overlay if the reconstructed archive does not match this hash.

## Reconstruct on Linux/macOS/Codex

From the repository root:

```bash
cat source-overlay/Xbox-original-upload.part01.b64 \
    source-overlay/Xbox-original-upload.part02.b64 \
    source-overlay/Xbox-original-upload.part03.b64 \
    source-overlay/Xbox-original-upload.part04.b64 \
  | base64 -d > source-overlay/Xbox-original-upload.zip

sha256sum source-overlay/Xbox-original-upload.zip

rm -rf source-overlay/extracted
mkdir -p source-overlay/extracted
unzip source-overlay/Xbox-original-upload.zip -d source-overlay/extracted
```

The expected extracted source root is:

```text
source-overlay/extracted/Xbox/
```

## Reconstruct on Windows PowerShell

From the repository root:

```powershell
$parts = @(
    'source-overlay\Xbox-original-upload.part01.b64',
    'source-overlay\Xbox-original-upload.part02.b64',
    'source-overlay\Xbox-original-upload.part03.b64',
    'source-overlay\Xbox-original-upload.part04.b64'
)

$base64 = ($parts | ForEach-Object { Get-Content -Raw $_ }) -join ''
[IO.File]::WriteAllBytes(
    'source-overlay\Xbox-original-upload.zip',
    [Convert]::FromBase64String($base64)
)

Get-FileHash 'source-overlay\Xbox-original-upload.zip' -Algorithm SHA256

Remove-Item 'source-overlay\extracted' -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive 'source-overlay\Xbox-original-upload.zip' -DestinationPath 'source-overlay\extracted'
```

The expected SHA-256 is again:

```text
6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35
```

## Source precedence

The extracted `Xbox/` tree represents newer Xbox-specific work supplied by the project owner and is **authoritative over same-path Xbox files from the older public `metalex10/PPSSPP-X360` source**.

Bootstrap order:

1. Import the complete legacy source tree from `metalex10/PPSSPP-X360` so the project has the full `Common/`, `Core/`, `GPU/`, `native/`, Xbox project files, PPC JIT, and other dependencies.
2. Reconstruct and extract this overlay.
3. Copy the extracted `Xbox/` tree over the imported repository's `Xbox/` tree, replacing same-path files with the owner-provided versions.
4. Preserve all other full-source directories from the legacy import.
5. Build and establish the legacy/overlay baseline before beginning modernization.

Do not commit generated reconstructed ZIP/extracted working files unless there is a deliberate project reason to do so; the four `.b64` source chunks are the archival copy already tracked by Git.
