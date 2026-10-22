param(
    [Parameter(Mandatory=$true)][string]$SourceRoot,
    [ValidateSet('Debug','Release_LTCG')][string]$Configuration = 'Debug',
    [string]$XdkRoot = 'C:\Program Files (x86)\Microsoft Xbox 360 SDK',
    [string]$LogPath
)
$ErrorActionPreference = 'Stop'
$baselineRoot = (Resolve-Path -LiteralPath $SourceRoot).Path
$projectPath = Join-Path $baselineRoot 'Xbox\xx\xx.vcxproj'
[xml]$project = Get-Content -LiteralPath $projectPath -Raw
$namespace = New-Object System.Xml.XmlNamespaceManager($project.NameTable)
$namespace.AddNamespace('m', 'http://schemas.microsoft.com/developer/msbuild/2003')
$deployNodes = $project.SelectNodes('//m:ItemDefinitionGroup/m:Deploy', $namespace)
if ($deployNodes.Count -eq 0) { throw 'Expected legacy deployment metadata is missing.' }
foreach ($deploy in $deployNodes) {
    if ($deploy.ExcludedFromBuild -ne 'true') {
        throw 'Local-only build refused: every legacy Deploy entry must be explicitly excluded.'
    }
}
$libraryProfile = if ($Configuration -eq 'Debug') { 'ppcD' } else { 'ppc' }
$libraryPath = Join-Path $baselineRoot "ffmpeg\Xbox\$libraryProfile\lib"
& python (Join-Path $PSScriptRoot 'verify_xbox_libraries.py') $libraryPath
if ($LASTEXITCODE -ne 0) { throw 'Xbox FFmpeg architecture verification failed.' }
$msbuildPath = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\MSBuild.exe'
if (-not (Test-Path -LiteralPath $msbuildPath)) { throw 'MSBuild 4.0 is unavailable.' }
if (-not (Test-Path -LiteralPath (Join-Path $XdkRoot 'bin\win32\cl.exe'))) {
    throw 'The licensed Xbox 360 compiler is unavailable.'
}
if (-not $LogPath) { $LogPath = Join-Path $baselineRoot "build-$Configuration.log" }
$previousXdk = $env:XEDK
try {
    $env:XEDK = $XdkRoot
    & $msbuildPath (Join-Path $baselineRoot 'Xbox\PPSSPP.sln') /t:Build `
        "/p:Configuration=$Configuration" '/p:Platform=Xbox 360' /p:DeployOnBuild=false `
        /m:1 /nologo "/flp:logfile=$LogPath;verbosity=normal" /verbosity:minimal
    if ($LASTEXITCODE -ne 0) { throw "Build failed; preserve the log at $LogPath" }
    Write-Output "PASS: $Configuration local build. No deployment or launch target was requested."
} finally {
    $env:XEDK = $previousXdk
}
