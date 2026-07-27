import os
import json
import unittest
from unittest import mock
from pathlib import Path
from tempfile import TemporaryDirectory

from vibe_stick.server import app


class ServerSecurityTests(unittest.TestCase):
    def test_loopback_host_does_not_require_token(self) -> None:
        self.assertFalse(app._host_requires_token("127.0.0.1"))
        self.assertFalse(app._host_requires_token("localhost"))
        self.assertFalse(app._host_requires_token("::1"))

    def test_non_loopback_host_requires_token(self) -> None:
        self.assertTrue(app._host_requires_token("0.0.0.0"))
        self.assertTrue(app._host_requires_token(""))
        self.assertTrue(app._host_requires_token("192.168.1.10"))

    def test_placeholder_token_is_treated_as_missing(self) -> None:
        with mock.patch.dict(os.environ, {"VIBE_STICK_BRIDGE_TOKEN": "change-this-shared-token"}):
            self.assertEqual(app._bridge_token(), "")

    def test_real_token_is_used(self) -> None:
        with mock.patch.dict(os.environ, {"VIBE_STICK_BRIDGE_TOKEN": "abc123-secret"}):
            self.assertEqual(app._bridge_token(), "abc123-secret")

    def test_discovery_response_remembers_s3_token(self) -> None:
        with TemporaryDirectory() as tmp:
            token_path = Path(tmp) / "paired-token.txt"
            payload = json.dumps({"type": "vibestick_discover", "token": "s3-token"})

            with mock.patch.object(app, "PAIRED_TOKEN_PATH", token_path):
                with mock.patch.dict(os.environ, {}, clear=True):
                    response = app._discovery_response(payload.encode("utf-8"), 8765)

                    self.assertEqual(app._bridge_token(), "s3-token")

        self.assertIsNotNone(response)
        data = json.loads(response.decode("utf-8"))
        self.assertEqual(data["type"], "vibestick_bridge")
        self.assertEqual(data["port"], 8765)

    def test_discovery_ignores_unknown_packets(self) -> None:
        self.assertIsNone(app._discovery_response(b'{"type":"other"}', 8765))


if __name__ == "__main__":
    unittest.main()
