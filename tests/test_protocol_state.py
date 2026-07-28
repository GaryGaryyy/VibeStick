import unittest

from vibe_stick.protocol.state import AgentStatus, ProviderState, default_state, state_from_dict


class ProtocolStateTests(unittest.TestCase):
    def test_bridge_state_never_serializes_remote_battery(self) -> None:
        state = state_from_dict(
            {
                "wifi": True,
                "battery": 82,
                "codex": {"status": "RUNNING", "project": "VibeStick"},
                "alert": {"type": "NONE"},
            }
        )

        self.assertIsNone(state.to_jsonable()["battery"])
        self.assertEqual(state.to_jsonable()["computer_name"], "Computer")

    def test_bridge_state_preserves_computer_name(self) -> None:
        state = state_from_dict({"computer_name": "Long Windows Workstation"})

        self.assertEqual(state.to_jsonable()["computer_name"], "Long Windows Workstation")

    def test_legacy_codex_block_populates_generic_provider(self) -> None:
        state = state_from_dict(
            {
                "codex": {
                    "status": "RUNNING",
                    "project": "VibeStick",
                    "quota_5h_remaining": 66,
                    "quota_7d_remaining": 96,
                    "quota_updated_at": "09:38",
                }
            }
        )

        payload = state.to_jsonable()
        self.assertEqual(payload["active_provider"], "codex")
        self.assertEqual(payload["provider"]["id"], "codex")
        self.assertEqual(payload["provider"]["status"], "RUNNING")
        self.assertNotIn("project", payload["provider"])
        self.assertEqual(payload["provider"]["quota_5h_remaining"], 66)
        self.assertEqual(payload["codex"]["status"], "RUNNING")
        self.assertNotIn("project", payload["codex"])

    def test_generic_provider_block_serializes_status_string(self) -> None:
        state = default_state()
        state.active_provider = "claude"
        state.provider = ProviderState(
            id="claude",
            display_name="Claude",
            implemented=True,
            status=AgentStatus.ERROR,
            quota_5h_remaining=None,
            quota_7d_remaining=None,
            quota_updated_at="",
            quota_stale=False,
        )

        payload = state.to_jsonable()

        self.assertEqual(payload["active_provider"], "claude")
        self.assertEqual(payload["provider"]["id"], "claude")
        self.assertEqual(payload["provider"]["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
