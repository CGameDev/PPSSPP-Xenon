$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Parts = @(
    (Join-Path $Root 'Xbox-original-upload.part01.b64'),
    (Join-Path $Root 'Xbox-original-upload.part02.b64'),
    (Join-Path $Root 'Xbox-original-upload.part03.b64'),
    (Join-Path $Root 'Xbox-original-upload.part04.b64')
)

$ExpectedSha256 = '6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35'
$ZipPath = Join-Path $Root 'Xbox-original-upload.zip'
$ExtractPath = Join-Path $Root 'extracted'

foreach ($Part in $Parts) {
    if (-not (Test-Path -LiteralPath $Part)) {
        throw "Missing source-overlay part: $Part"
    }
}

Write-Host 'Reconstructing Xbox-original-upload.zip...'
$Base64 = ($Parts | ForEach-Object { (Get-Content -Raw -LiteralPath $_).Trim() }) -join ''
[IO.File]::WriteAllBytes($ZipPath, [Convert]::FromBase64String($Base64))

$ActualSha256 = (Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ActualSha256 -ne $ExpectedSha256) {
    Remove-Item -LiteralPath $ZipPath -Force -ErrorAction SilentlyContinue
    throw "Xbox source overlay integrity check failed. Expected $ExpectedSha256 but got $ActualSha256"
}

Write-Host "Integrity verified: $ActualSha256"
Remove-Item -LiteralPath $ExtractPath -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive -LiteralPath $ZipPath -DestinationPath $ExtractPath -Force

$XboxPath = Join-Path $ExtractPath 'Xbox'
if (-not (Test-Path -LiteralPath $XboxPath -PathType Container)) {
    throw "Expected extracted Xbox source folder was not found: $XboxPath"
}

Write-Host ''
Write-Host 'PPSSPP Xenon Xbox source overlay reconstructed successfully.'
Write-Host "Source: $XboxPath"
Write-Host 'This Xbox tree is authoritative over same-path Xbox files imported from metalex10/PPSSPP-X360.'
