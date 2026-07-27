"""Small optional Windows recording overlay driven by the bridge HUD state file."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from vibe_stick.config.paths import HUD_STATE_PATH, ensure_app_support

POLL_MS = 100
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 58
WINDOW_TOP = 42


def main() -> None:
    try:
        import tkinter as tk
    except ImportError as exc:
        raise SystemExit(f"Windows HUD requires tkinter: {exc}") from exc

    root = tk.Tk()
    root.withdraw()
    root.title("VibeStick")
    root.configure(background="#101216")

    overlay = tk.Toplevel(root)
    overlay.withdraw()
    overlay.overrideredirect(True)
    overlay.attributes("-topmost", True)
    overlay.configure(background="#101216")

    label = tk.Label(
        overlay,
        text="",
        background="#101216",
        foreground="#f3f4f6",
        font=("Microsoft YaHei UI", 16),
        padx=24,
        pady=12,
    )
    label.pack(fill="both", expand=True)

    def refresh() -> None:
        payload = _read_state()
        text = _active_text(payload)
        if text:
            label.configure(text=text)
            screen_width = overlay.winfo_screenwidth()
            x = max(0, (screen_width - WINDOW_WIDTH) // 2)
            overlay.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{WINDOW_TOP}")
            overlay.deiconify()
            overlay.lift()
        else:
            overlay.withdraw()
        root.after(POLL_MS, refresh)

    ensure_app_support()
    root.after(0, refresh)
    root.mainloop()


def _read_state() -> dict[str, Any]:
    try:
        data = json.loads(Path(HUD_STATE_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _active_text(payload: dict[str, Any]) -> str:
    if not payload.get("active"):
        return ""
    expires = payload.get("expires_at_epoch")
    if isinstance(expires, (int, float)) and expires > 0 and time.time() >= expires:
        return ""
    return str(payload.get("text") or payload.get("status") or "").strip()


if __name__ == "__main__":
    main()
