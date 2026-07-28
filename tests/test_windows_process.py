import unittest
from unittest import mock

from vibe_stick.desktop import process


class WindowsProcessTests(unittest.TestCase):
    def test_non_windows_returns_default_options(self) -> None:
        with mock.patch.object(process.platform, "system", return_value="Darwin"):
            self.assertEqual(process.hidden_subprocess_kwargs(), {})

    def test_windows_returns_hidden_console_options(self) -> None:
        class FakeStartupInfo:
            def __init__(self) -> None:
                self.dwFlags = 0
                self.wShowWindow = None

        startup_info = FakeStartupInfo()
        with mock.patch.object(process.platform, "system", return_value="Windows"):
            with mock.patch.object(
                process.subprocess,
                "STARTUPINFO",
                return_value=startup_info,
                create=True,
            ):
                with mock.patch.object(
                    process.subprocess,
                    "CREATE_NO_WINDOW",
                    0x08000000,
                    create=True,
                ):
                    with mock.patch.object(
                        process.subprocess,
                        "STARTF_USESHOWWINDOW",
                        0x00000001,
                        create=True,
                    ):
                        with mock.patch.object(process.subprocess, "SW_HIDE", 0, create=True):
                            options = process.hidden_subprocess_kwargs()

        self.assertEqual(options["creationflags"], 0x08000000)
        self.assertIs(options["startupinfo"], startup_info)
        self.assertEqual(startup_info.dwFlags, 0x00000001)
        self.assertEqual(startup_info.wShowWindow, 0)


if __name__ == "__main__":
    unittest.main()
