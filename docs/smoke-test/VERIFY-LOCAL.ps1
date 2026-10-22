# Read-only, local package verification. No device/network or launch commands.
param()
$ErrorActionPreference = 'Stop'
$kitRoot = [System.IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\','/')
$manifest = Get-Content -LiteralPath (Join-Path $kitRoot 'MANIFEST.json') -Raw | ConvertFrom-Json
if ($manifest.schema_version -ne 1) { throw 'Unsupported manifest version.' }
$prefix = $kitRoot + [System.IO.Path]::DirectorySeparatorChar
foreach ($entry in $manifest.files) {
    $filePath = [System.IO.Path]::GetFullPath((Join-Path $kitRoot $entry.path))
    if (-not $filePath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path outside kit: $($entry.path)"
    }
    $item = Get-Item -LiteralPath $filePath
    if ($item.PSIsContainer -or $item.Length -ne $entry.bytes) { throw "Size/type mismatch: $($entry.path)" }
    if ((Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
        throw "Hash mismatch: $($entry.path)"
    }
}
foreach ($relative in $manifest.required_directories) {
    $directoryPath = [System.IO.Path]::GetFullPath((Join-Path $kitRoot $relative))
    if (-not $directoryPath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Directory outside kit: $relative"
    }
    if (-not (Test-Path -LiteralPath $directoryPath -PathType Container)) { throw "Missing directory: $relative" }
}
Write-Output "PASS: $($manifest.files.Count) packaged files and $($manifest.required_directories.Count) required directories."
Write-Output 'Immutable listed files only; editable results, added ISO and generated data are not verified. No Xbox contacted or launched.'
