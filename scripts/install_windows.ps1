$ErrorActionPreference = "Stop"
$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$BridgeDir = Join-Path $RootDir "bridge"
$ConfigDir = Join-Path $env:APPDATA "VibeStick"
$VenvDir = Join-Path $ConfigDir ".venv"
$BridgeRunnerPath = Join-Path $ConfigDir "run-vibestick-wifi-bridge.cmd"

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
if (Test-Path (Join-Path $RootDir ".env")) {
    Copy-Item (Join-Path $RootDir ".env") (Join-Path $ConfigDir ".env") -Force
}

if (-not (Test-Path $VenvDir)) {
    py -3 -m venv $VenvDir
}

$Python = Join-Path $VenvDir "Scripts\python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install $BridgeDir

@"
@echo off
cd /d "$ConfigDir"
"$Python" -m vibe_stick --host 0.0.0.0 --port 8765
"@ | Set-Content -Path $BridgeRunnerPath -Encoding ASCII

Write-Host "VibeStick Windows config directory:"
Write-Host $ConfigDir
Write-Host "Wi-Fi bridge runner:"
Write-Host $BridgeRunnerPath
Write-Host "Run the Wi-Fi bridge runner on Windows. On the StickS3, long-press the side button to discover this PC, then select it with the blue button."
Write-Host "If Windows Firewall prompts, allow Python on private networks so TCP 8765 and UDP 8766 can receive LAN traffic."
