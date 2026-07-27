param(
    [string]$TaskName = "VibeStick Bridge"
)

$ErrorActionPreference = "Stop"
$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$BridgeDir = Join-Path $RootDir "bridge"
$ConfigDir = Join-Path $env:APPDATA "VibeStick"
$VenvDir = Join-Path $ConfigDir ".venv"
$BridgeRunnerPath = Join-Path $ConfigDir "run-vibestick-wifi-bridge.cmd"
$ConfigEnvPath = Join-Path $ConfigDir ".env"
$ExampleEnvPath = Join-Path $RootDir ".env.example"
$SourceEnvPath = Join-Path $RootDir ".env"
$HudTaskName = "VibeStick HUD"

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
if (Test-Path $SourceEnvPath) {
    Copy-Item $SourceEnvPath $ConfigEnvPath -Force
} elseif (-not (Test-Path $ConfigEnvPath) -and (Test-Path $ExampleEnvPath)) {
    Copy-Item $ExampleEnvPath $ConfigEnvPath
    $config = Get-Content $ConfigEnvPath -Raw
    $config = $config -replace '(?m)^VIBE_STICK_RECORDING_USE_MAC_MIC=.*$', 'VIBE_STICK_RECORDING_USE_MAC_MIC=0'
    Set-Content -Path $ConfigEnvPath -Value $config -Encoding ASCII
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

$UserId = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$TaskAction = New-ScheduledTaskAction `
    -Execute $Python `
    -Argument "-m vibe_stick --host 0.0.0.0 --port 8765" `
    -WorkingDirectory $ConfigDir
$TaskTrigger = New-ScheduledTaskTrigger -AtLogOn -User $UserId
$TaskPrincipal = New-ScheduledTaskPrincipal `
    -UserId $UserId `
    -LogonType Interactive `
    -RunLevel Limited
$TaskSettings = New-ScheduledTaskSettingsSet `
    -Hidden `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Stop-ScheduledTask -TaskName $HudTaskName -ErrorAction SilentlyContinue
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $TaskAction `
    -Trigger $TaskTrigger `
    -Principal $TaskPrincipal `
    -Settings $TaskSettings `
    -Force | Out-Null

$Pythonw = Join-Path $VenvDir "Scripts\pythonw.exe"
$HudAction = New-ScheduledTaskAction `
    -Execute $Pythonw `
    -Argument "-m vibe_stick.windows_hud" `
    -WorkingDirectory $ConfigDir
$HudTrigger = New-ScheduledTaskTrigger -AtLogOn -User $UserId
$HudPrincipal = New-ScheduledTaskPrincipal `
    -UserId $UserId `
    -LogonType Interactive `
    -RunLevel Limited
Register-ScheduledTask `
    -TaskName $HudTaskName `
    -Action $HudAction `
    -Trigger $HudTrigger `
    -Principal $HudPrincipal `
    -Settings $TaskSettings `
    -Force | Out-Null

Start-ScheduledTask -TaskName $TaskName
Start-ScheduledTask -TaskName $HudTaskName
Start-Sleep -Seconds 1
$TaskState = (Get-ScheduledTask -TaskName $TaskName).State
$HudTaskState = (Get-ScheduledTask -TaskName $HudTaskName).State

Write-Host "VibeStick Windows config directory:"
Write-Host $ConfigDir
Write-Host "Wi-Fi bridge runner:"
Write-Host $BridgeRunnerPath
Write-Host "Configuration file:"
Write-Host $ConfigEnvPath
Write-Host "Fill VIBE_STICK_ASR_API_KEY in that file before voice transcription."
Write-Host "Background task: $TaskName ($TaskState)"
Write-Host "Recording overlay task: $HudTaskName ($HudTaskState)"
Write-Host "The bridge now starts silently at Windows logon and has been started for this user."
Write-Host "Manual fallback: $BridgeRunnerPath"
Write-Host "On the StickS3, long-press the side button to discover this PC, then select it with the blue button."
Write-Host "If Windows Firewall prompts, allow Python on private networks so TCP 8765 and UDP 8766 can receive LAN traffic."
