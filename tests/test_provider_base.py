import unittest

from vibe_stick.protocol.state import AgentStatus
from vibe_stick.providers.base import ProviderObservation


class ProviderBaseTests(unittest.TestCase):
    def test_provider_observation_uses_agent_status(self) -> None:
        observation = ProviderObservation(
            provider_id="codex",
            display_name="Codex",
            online=True,
            status=AgentStatus.RUNNING,
            quota_5h_remaining=91,
            quota_7d_remaining=99,
            quota_updated_at="09:38",
            quota_stale=False,
            alert_type="NONE",
            alert_message="",
            alert_event_id="",
        )

        self.assertEqual(observation.status.value, "RUNNING")
        self.assertEqual(observation.latest_event_timestamp, None)


if __name__ == "__main__":
    unittest.main()
