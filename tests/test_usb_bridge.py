import unittest
from unittest import mock

from vibe_stick.server.usb_bridge import UsbBridgeSession


class UsbBridgeTests(unittest.TestCase):
    def test_get_state_returns_bridge_state(self) -> None:
        store = mock.Mock()
        state = mock.Mock()
        state.to_jsonable.return_value = {"time": "09:41", "computer_name": "WinBox"}
        store.get_state.return_value = state
        session = UsbBridgeSession(store=store)

        response = session.handle_request({"id": "1", "method": "GET", "path": "/state"})

        self.assertTrue(response["ok"])
        self.assertEqual(response["body"]["computer_name"], "WinBox")
        self.assertEqual(response["body"]["bridge_name"], "vibestick-bridge")

    def test_audio_upload_accumulates_base64_chunks_until_final(self) -> None:
        store = mock.Mock()
        store.upload_recording_audio.return_value = {"recording": {"status": "recording"}}
        session = UsbBridgeSession(store=store)

        first = session.handle_request(
            {
                "id": "1",
                "method": "POST",
                "path": "/recording/audio?session_id=abc12345",
                "encoding": "base64",
                "body": "AQI=",
                "final": False,
            }
        )
        second = session.handle_request(
            {
                "id": "2",
                "method": "POST",
                "path": "/recording/audio?session_id=abc12345",
                "encoding": "base64",
                "body": "AwQ=",
                "final": True,
            }
        )

        self.assertEqual(first["body"]["received"], 2)
        self.assertTrue(second["ok"])
        store.upload_recording_audio.assert_called_once()
        self.assertEqual(store.upload_recording_audio.call_args.args[0], b"\x01\x02\x03\x04")


if __name__ == "__main__":
    unittest.main()
