from __future__ import annotations

import os
from pathlib import Path

from vibe_stick.config.paths import APP_SUPPORT_DIR


def load_dotenv_files(*extra_paths: Path) -> None:
    paths = [APP_SUPPORT_DIR / ".env", Path.cwd() / ".env", *extra_paths]
    seen: set[Path] = set()
    for path in paths:
        resolved = path.expanduser()
        if resolved in seen:
            continue
        seen.add(resolved)
        _load_dotenv_file(resolved)


def _load_dotenv_file(path: Path) -> None:
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        os.environ[key] = _clean_value(value)


def _clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
