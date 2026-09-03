#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED_SHA256="6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35"
ZIP_PATH="$ROOT/Xbox-original-upload.zip"
EXTRACT_PATH="$ROOT/extracted"

PARTS=(
  "$ROOT/Xbox-original-upload.part01.b64"
  "$ROOT/Xbox-original-upload.part02.b64"
  "$ROOT/Xbox-original-upload.part03.b64"
  "$ROOT/Xbox-original-upload.part04.b64"
)

for part in "${PARTS[@]}"; do
  [[ -f "$part" ]] || { echo "Missing source-overlay part: $part" >&2; exit 1; }
done

echo "Reconstructing Xbox-original-upload.zip..."
cat "${PARTS[@]}" | tr -d '\r\n\t ' | base64 -d > "$ZIP_PATH"

ACTUAL_SHA256="$(sha256sum "$ZIP_PATH" | awk '{print $1}')"
if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
  rm -f "$ZIP_PATH"
  echo "Xbox source overlay integrity check failed." >&2
  echo "Expected: $EXPECTED_SHA256" >&2
  echo "Actual:   $ACTUAL_SHA256" >&2
  exit 1
fi

echo "Integrity verified: $ACTUAL_SHA256"
rm -rf "$EXTRACT_PATH"
mkdir -p "$EXTRACT_PATH"
unzip -q "$ZIP_PATH" -d "$EXTRACT_PATH"

if [[ ! -d "$EXTRACT_PATH/Xbox" ]]; then
  echo "Expected extracted Xbox source folder was not found: $EXTRACT_PATH/Xbox" >&2
  exit 1
fi

echo
echo "PPSSPP Xenon Xbox source overlay reconstructed successfully."
echo "Source: $EXTRACT_PATH/Xbox"
echo "This Xbox tree is authoritative over same-path Xbox files imported from metalex10/PPSSPP-X360."
