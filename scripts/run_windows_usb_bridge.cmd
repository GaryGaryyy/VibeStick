@echo off
setlocal
set ROOT_DIR=%~dp0..
cd /d "%ROOT_DIR%"
python -m pip show pyserial >nul 2>nul
if errorlevel 1 (
  echo pyserial is required. Run scripts\install_windows.ps1 first.
  exit /b 1
)
set PYTHONPATH=%ROOT_DIR%\bridge\src
python -m vibe_stick.server.usb_bridge %*
