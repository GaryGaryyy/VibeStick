import unittest
from datetime import datetime, timezone

from vibe_stick.codex.local_observer import LocalCodexObservation
from vibe_stick.codex.local_observer import _command_is_codex_process
from vibe_stick.codex.quota import QuotaSnapshot
from vibe_stick.protocol.state import AgentStatus
from vibe_stick.providers.codex import observation_from_local_codex


class CodexProviderTests(unittest.TestCase):
    def test_codex_process_detection_accepts_chatgpt_embedded_app_server(self) -> None:
        self.assertTrue(
            _command_is_codex_process(
                "/Applications/ChatGPT.app/Contents/Resources/codex "
                "-c features.code_mode_host=true app-server --analytics-default-enabled"
            )
        )

    def test_codex_process_detection_accepts_standalone_app_and_cli(self) -> None:
        self.assertTrue(_command_is_codex_process("/Applications/Codex.app/Contents/MacOS/Codex"))
        self.assertTrue(_command_is_codex_process("/opt/homebrew/bin/codex -c foo=true app-server"))
        self.assertTrue(_command_is_codex_process(r"C:\Users\me\AppData\Local\Programs\Codex\codex.exe app-server"))

    def test_codex_process_detection_rejects_related_non_agent_commands(self) -> None:
        self.assertFalse(
            _command_is_codex_process(
                "/Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/"
                "Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer)"
            )
        )
        self.assertFalse(_command_is_codex_process("rg -i codex|chatgpt|app-server"))

    def test_codex_local_observation_maps_to_provider_observation(self) -> None:
        timestamp = datetime(2026, 6, 28, 9, 41, tzinfo=timezone.utc)
        observation = observation_from_local_codex(
            LocalCodexObservation(
                status=AgentStatus.DONE,
                project="VibeStick",
                quota=QuotaSnapshot(66, 96, "09:40", False),
                quota_found=True,
                alert_type="DONE",
                alert_message="Codex task completed",
                alert_timestamp=timestamp,
                latest_event_timestamp=timestamp,
                codex_online=True,
            )
        )

        self.assertEqual(observation.provider_id, "codex")
        self.assertEqual(observation.display_name, "Codex")
        self.assertEqual(observation.status, AgentStatus.DONE)
        self.assertEqual(observation.quota_5h_remaining, 66)
        self.assertEqual(observation.quota_7d_remaining, 96)
        self.assertEqual(observation.alert_type, "DONE")
        self.assertEqual(observation.alert_event_id, f"evt_{timestamp.astimezone().strftime('%Y%m%d_%H%M%S')}_done")
        self.assertEqual(observation.latest_event_timestamp, timestamp)

    def test_missing_codex_quota_maps_to_unknown_bars(self) -> None:
        observation = observation_from_local_codex(
            LocalCodexObservation(
                status=AgentStatus.IDLE,
                project="VibeStick",
                quota=None,
                quota_found=False,
                codex_online=True,
            )
        )

        self.assertIsNone(observation.quota_5h_remaining)
        self.assertIsNone(observation.quota_7d_remaining)
        self.assertEqual(observation.alert_type, "NONE")


if __name__ == "__main__":
    unittest.main()
