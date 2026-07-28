from __future__ import annotations

import os
import sys
from pathlib import Path

from vibe_stick.server.app import main


def _configure_background_stdio() -> None:
    if sys.stdout is not None and sys.stderr is not None:
        return

    app_data = os.environ.get("APPDATA")
    config_dir = Path(app_data) / "VibeStick" if app_data else Path.home() / ".vibestick"
    config_dir.mkdir(parents=True, exist_ok=True)
    log_path = config_dir / "bridge.log"
    log = log_path.open("a", encoding="utf-8", buffering=1)
    if sys.stdout is None:
        sys.stdout = log
    if sys.stderr is None:
        sys.stderr = log


if __name__ == "__main__":
    _configure_background_stdio()
    main()
