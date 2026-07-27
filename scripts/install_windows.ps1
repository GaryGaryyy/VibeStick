param(
    [string]$Port = "",
    [switch]$UsbOnly
)

$ErrorActionPreference = "Stop"
$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$BridgeDir = Join-Path $RootDir "bridge"
$ConfigDir = Join-Path $env:APPDATA "VibeStick"
$VenvDir = Join-Path $ConfigDir ".venv"
$RunnerPath = Join-Path $ConfigDir "run-vibestick-usb-bridge.cmd"
$HttpRunnerPath = Join-Path $ConfigDir "run-vibestick-http-bridge.cmd"

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
if (Test-Path (Join-Path $RootDir ".env")) {
    Copy-Item (Join-Path $RootDir ".env") (Join-Path $ConfigDir ".env") -Force
}

if (-not (Test-Path $VenvDir)) {
    py -3 -m venv $VenvDir
}

$Python = Join-Path $VenvDir "Scripts\python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install "${BridgeDir}[windows]"

$PortArg = ""
if ($Port.Trim()) {
    $PortArg = " --port $Port"
}

@"
@echo off
cd /d "$ConfigDir"
"$Python" -m vibe_stick.server.usb_bridge$PortArg
"@ | Set-Content -Path $RunnerPath -Encoding ASCII

@"
@echo off
cd /d "$ConfigDir"
"$Python" -m vibe_stick --host 0.0.0.0 --port 8765
"@ | Set-Content -Path $HttpRunnerPath -Encoding ASCII

Write-Host "VibeStick Windows config directory:"
Write-Host $ConfigDir
Write-Host "USB bridge runner:"
Write-Host $RunnerPath
if (-not $UsbOnly) {
    Write-Host "HTTP bridge runner:"
    Write-Host $HttpRunnerPath
}
Write-Host "Run the USB bridge runner after plugging StickS3 into this Windows computer."
