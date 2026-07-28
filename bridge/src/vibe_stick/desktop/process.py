"""Subprocess options for desktop integrations."""

from __future__ import annotations

import platform
import subprocess


def hidden_subprocess_kwargs() -> dict[str, object]:
    """Return Windows subprocess flags that prevent console windows from flashing."""
    if platform.system() != "Windows":
        return {}

    kwargs: dict[str, object] = {
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
    }
    startup_info_class = getattr(subprocess, "STARTUPINFO", None)
    if startup_info_class is not None:
        startup_info = startup_info_class()
        startup_info.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
        startup_info.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
        kwargs["startupinfo"] = startup_info
    return kwargs
