$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "=== FrameForge Self-Contained Build ===" -ForegroundColor Cyan

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    py -m venv .venv
    $Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
}

Write-Host "Installing build dependencies..." -ForegroundColor Yellow
& $Python -m pip install --upgrade pip
& $Python -m pip install --upgrade pyinstaller
if (Test-Path "requirements.txt") {
    & $Python -m pip install -r requirements.txt
}

$BuildRoot = Join-Path $ProjectRoot ".build"
$FfmpegRoot = Join-Path $BuildRoot "ffmpeg"
$FfmpegZip = Join-Path $BuildRoot "ffmpeg.zip"
$FfmpegExe = Join-Path $FfmpegRoot "ffmpeg.exe"
$FfprobeExe = Join-Path $FfmpegRoot "ffprobe.exe"

New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null

# Gyan.dev Windows Essentials build.
$FfmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

if (-not ((Test-Path $FfmpegExe) -and (Test-Path $FfprobeExe))) {
    Write-Host "Downloading FFmpeg Essentials..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $FfmpegUrl -OutFile $FfmpegZip

    $ExtractRoot = Join-Path $BuildRoot "ffmpeg_extract"
    Remove-Item -Recurse -Force $ExtractRoot -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $ExtractRoot | Out-Null

    Expand-Archive -Path $FfmpegZip -DestinationPath $ExtractRoot -Force

    $FoundFfmpeg = Get-ChildItem $ExtractRoot -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
    $FoundFfprobe = Get-ChildItem $ExtractRoot -Recurse -Filter "ffprobe.exe" | Select-Object -First 1

    if (-not $FoundFfmpeg -or -not $FoundFfprobe) {
        throw "Could not find ffmpeg.exe and ffprobe.exe in the downloaded archive."
    }

    Remove-Item -Recurse -Force $FfmpegRoot -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $FfmpegRoot | Out-Null

    Copy-Item $FoundFfmpeg.FullName $FfmpegExe -Force
    Copy-Item $FoundFfprobe.FullName $FfprobeExe -Force
}

Write-Host "FFmpeg ready." -ForegroundColor Green

Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue

Write-Host "Building FrameForge..." -ForegroundColor Green
& $Python -m PyInstaller --clean --noconfirm "FrameForge.spec"

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed."
}

$Exe = Join-Path $ProjectRoot "dist\FrameForge.exe"
if (-not (Test-Path $Exe)) {
    throw "PyInstaller did not create dist\FrameForge.exe."
}

# Stage the files exactly as Inno Setup expects them.
$Stage = Join-Path $ProjectRoot "dist\FrameForge"
Remove-Item -Recurse -Force $Stage -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

Move-Item $Exe (Join-Path $Stage "FrameForge.exe")

# Bundle FFmpeg alongside the application.
Copy-Item $FfmpegExe (Join-Path $Stage "ffmpeg.exe") -Force
Copy-Item $FfprobeExe (Join-Path $Stage "ffprobe.exe") -Force

if (Test-Path "assets") {
    Copy-Item "assets" (Join-Path $Stage "assets") -Recurse -Force
}

Write-Host ""
Write-Host "=== Build complete ===" -ForegroundColor Cyan
Write-Host "Inno Setup source folder:"
Write-Host $Stage
Write-Host ""
Write-Host "Open installer\FrameForge.iss in Inno Setup Compiler and press Compile."
