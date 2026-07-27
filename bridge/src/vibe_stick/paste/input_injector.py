from __future__ import annotations

import platform
import subprocess
import time
from dataclasses import dataclass


@dataclass
class PasteResult:
    success: bool
    message: str


def make_paste_injector() -> "PasteInjector":
    system = platform.system()
    if system == "Darwin":
        return MacPasteInjector()
    if system == "Windows":
        return WindowsPasteInjector()
    return UnsupportedPasteInjector(system)


class PasteInjector:
    def paste(self, text: str, press_enter: bool = False) -> PasteResult:
        raise NotImplementedError


class MacPasteInjector(PasteInjector):
    def paste(self, text: str, press_enter: bool = False) -> PasteResult:
        text = text.strip()
        if not text:
            return PasteResult(False, "No text to paste")
        if platform.system() != "Darwin":
            return PasteResult(False, "Automatic paste is only available on macOS")

        previous_text = self._read_clipboard()
        set_result = self._set_clipboard(text)
        if not set_result.success:
            return set_result

        script = [
            'tell application "System Events" to keystroke "v" using command down',
        ]
        if press_enter:
            script.extend([
                "delay 0.12",
                'tell application "System Events" to key code 36',
            ])

        args = ["osascript"]
        for line in script:
            args.extend(["-e", line])
        result = subprocess.run(args, check=False, capture_output=True, text=True, timeout=5)
        time.sleep(0.2)
        if previous_text is not None:
            self._set_clipboard(previous_text)

        if result.returncode != 0:
            message = (result.stderr or result.stdout or "macOS paste failed").strip()
            return PasteResult(False, message)
        return PasteResult(True, "Pasted into the focused app")

    def _read_clipboard(self) -> str | None:
        try:
            result = subprocess.run(
                ["pbpaste"],
                check=False,
                capture_output=True,
                text=True,
                timeout=2,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        if result.returncode != 0:
            return None
        return result.stdout

    def _set_clipboard(self, text: str) -> PasteResult:
        try:
            result = subprocess.run(
                ["pbcopy"],
                input=text,
                check=False,
                capture_output=True,
                text=True,
                timeout=2,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return PasteResult(False, f"Clipboard write failed: {exc}")
        if result.returncode != 0:
            message = (result.stderr or "Clipboard write failed").strip()
            return PasteResult(False, message)
        return PasteResult(True, "Clipboard updated")


class WindowsPasteInjector(PasteInjector):
    def paste(self, text: str, press_enter: bool = False) -> PasteResult:
        text = text.strip()
        if not text:
            return PasteResult(False, "No text to paste")
        if platform.system() != "Windows":
            return PasteResult(False, "Windows paste injector can only run on Windows")

        set_result = self._set_clipboard(text)
        if not set_result.success:
            return set_result

        try:
            self._send_ctrl_v(press_enter=press_enter)
        except OSError as exc:
            return PasteResult(False, f"Windows paste failed: {exc}")
        time.sleep(0.1)
        return PasteResult(True, "Pasted into the focused app")

    def _set_clipboard(self, text: str) -> PasteResult:
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Set-Clipboard -Value ([Console]::In.ReadToEnd())",
        ]
        try:
            result = subprocess.run(
                command,
                input=text,
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return PasteResult(False, f"Clipboard write failed: {exc}")
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "Clipboard write failed").strip()
            return PasteResult(False, message)
        return PasteResult(True, "Clipboard updated")

    def _send_ctrl_v(self, *, press_enter: bool) -> None:
        import ctypes

        user32 = ctypes.windll.user32
        keybd_event = user32.keybd_event
        keybd_event.argtypes = [
            ctypes.c_ubyte,
            ctypes.c_ubyte,
            ctypes.c_uint,
            ctypes.c_void_p,
        ]
        vk_control = 0x11
        vk_v = 0x56
        vk_enter = 0x0D
        key_up = 0x0002

        keybd_event(vk_control, 0, 0, None)
        keybd_event(vk_v, 0, 0, None)
        keybd_event(vk_v, 0, key_up, None)
        keybd_event(vk_control, 0, key_up, None)
        if press_enter:
            time.sleep(0.12)
            keybd_event(vk_enter, 0, 0, None)
            keybd_event(vk_enter, 0, key_up, None)


class UnsupportedPasteInjector(PasteInjector):
    def __init__(self, system: str) -> None:
        self.system = system or "this platform"

    def paste(self, text: str, press_enter: bool = False) -> PasteResult:
        del press_enter
        if not text.strip():
            return PasteResult(False, "No text to paste")
        return PasteResult(False, f"Automatic paste is not available on {self.system}")
