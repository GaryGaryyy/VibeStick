import threading
import unittest
from unittest import mock

from vibe_stick.paste.input_injector import PasteResult
from vibe_stick.protocol.state import AlertType, default_state
from vibe_stick.server import app


class ServerEventsTests(unittest.TestCase):
    def test_button_short_presses_enter_and_clears_alert(self) -> None:
        store = app.BridgeStateStore.__new__(app.BridgeStateStore)
        store._lock = threading.RLock()
        store._state = default_state()
        store._save_state_locked = mock.Mock()
        injector = mock.Mock()
        injector.press_enter.return_value = PasteResult(True, "Pressed Enter")

        with mock.patch.object(app, "make_paste_injector", return_value=injector):
            state = store.update_from_event({"event": "button_short"})

        injector.press_enter.assert_called_once_with()
        self.assertEqual(state.alert.type, AlertType.NONE)
        store._save_state_locked.assert_called_once_with()

    def test_button_short_sets_error_alert_when_enter_fails(self) -> None:
        store = app.BridgeStateStore.__new__(app.BridgeStateStore)
        store._lock = threading.RLock()
        store._state = default_state()
        store._save_state_locked = mock.Mock()
        injector = mock.Mock()
        injector.press_enter.return_value = PasteResult(False, "Accessibility permission missing")

        with mock.patch.object(app, "make_paste_injector", return_value=injector):
            state = store.update_from_event({"event": "button_short"})

        self.assertEqual(state.alert.type, AlertType.ERROR)
        self.assertIn("Accessibility", state.alert.message)


if __name__ == "__main__":
    unittest.main()
