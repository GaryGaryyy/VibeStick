import time
import unittest

from vibe_stick import windows_hud


class WindowsHudTests(unittest.TestCase):
    def test_active_state_returns_display_text(self) -> None:
        self.assertEqual(
            windows_hud._active_text({"active": True, "text": "正在聆听"}),
            "正在聆听",
        )

    def test_inactive_or_expired_state_is_hidden(self) -> None:
        self.assertEqual(windows_hud._active_text({"active": False, "text": "正在聆听"}), "")
        self.assertEqual(
            windows_hud._active_text(
                {"active": True, "text": "正在识别", "expires_at_epoch": time.time() - 1}
            ),
            "",
        )


if __name__ == "__main__":
    unittest.main()
