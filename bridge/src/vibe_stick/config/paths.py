from __future__ import annotations

import os
import platform
from pathlib import Path


def _app_support_dir() -> Path:
    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA", "").strip()
        if appdata:
            return Path(appdata) / "VibeStick"
        return Path.home() / "AppData" / "Roaming" / "VibeStick"
    return Path.home() / "Library" / "Application Support" / "VibeStick"


APP_SUPPORT_DIR = _app_support_dir()
STATE_PATH = APP_SUPPORT_DIR / "state.json"
QUOTA_PATH = APP_SUPPORT_DIR / "quota.json"
CLAUDE_QUOTA_PATH = APP_SUPPORT_DIR / "claude-quota.json"
RECORDING_PATH = APP_SUPPORT_DIR / "recording.json"
HUD_STATE_PATH = APP_SUPPORT_DIR / "hud-state.json"
RECORDINGS_DIR = APP_SUPPORT_DIR / "Recordings"


def ensure_app_support() -> Path:
    APP_SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    return APP_SUPPORT_DIR
