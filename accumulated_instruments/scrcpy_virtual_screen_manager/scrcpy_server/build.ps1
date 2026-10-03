$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$Upstream = Join-Path $Root ".upstream"
$OutDir = Join-Path $Root "out"
$Artifact = Join-Path $OutDir "scrcpy-server-v4.1-audio-isolated"
$PatchScript = Join-Path $Root "patch_v4_1.py"

function Require-Command([string]$Name) {
    $Command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $Command) {
        throw "Required command '$Name' was not found in PATH."
    }
    return $Command
}

$null = Require-Command git
$null = Require-Command python
$null = Require-Command java

if (-not $env:ANDROID_SDK_ROOT) {
    $DefaultSdk = Join-Path $env:LOCALAPPDATA "Android\Sdk"
    if (Test-Path $DefaultSdk) {
        $env:ANDROID_SDK_ROOT = $DefaultSdk
        Write-Host "Using ANDROID_SDK_ROOT=$DefaultSdk"
    }
}
if (-not $env:ANDROID_SDK_ROOT -or -not (Test-Path $env:ANDROID_SDK_ROOT)) {
    throw "ANDROID_SDK_ROOT is not set to an existing Android SDK."
}

if (-not (Test-Path (Join-Path $Upstream ".git"))) {
    Write-Host "Cloning scrcpy v4.1..."
    git clone --depth 1 --branch v4.1 https://github.com/Genymobile/scrcpy.git $Upstream
    if ($LASTEXITCODE -ne 0) { throw "git clone failed." }
}
else {
    Write-Host "Resetting local scrcpy source to v4.1..."
    git -C $Upstream fetch --depth 1 origin tag v4.1
    if ($LASTEXITCODE -ne 0) { throw "git fetch v4.1 failed." }
    git -C $Upstream reset --hard v4.1
    if ($LASTEXITCODE -ne 0) { throw "git reset v4.1 failed." }
    git -C $Upstream clean -fd
    if ($LASTEXITCODE -ne 0) { throw "git clean failed." }
}

Write-Host "Applying Machine-Soul audio-isolation patch..."
python $PatchScript --source $Upstream
if ($LASTEXITCODE -ne 0) { throw "Server patch failed." }

$Gradle = Join-Path $Upstream "gradlew.bat"
$ServerDir = Join-Path $Upstream "server"
Write-Host "Building scrcpy v4.1 server..."
& $Gradle -p $ServerDir assembleRelease
if ($LASTEXITCODE -ne 0) { throw "Gradle server build failed." }

$Built = Join-Path $ServerDir "build\outputs\apk\release\server-release-unsigned.apk"
if (-not (Test-Path $Built)) {
    throw "Build succeeded but expected server artifact was not found: $Built"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Copy-Item -Force $Built $Artifact

$Hash = (Get-FileHash -Algorithm SHA256 $Artifact).Hash.ToLowerInvariant()
Write-Host ""
Write-Host "Built patched server:"
Write-Host "  $Artifact"
Write-Host "SHA-256:"
Write-Host "  $Hash"
Write-Host ""
Write-Host "The manager auto-detects this path on its next launch."
