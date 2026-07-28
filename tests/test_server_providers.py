import os
import unittest
from datetime import datetime, timezone
from unittest import mock

from vibe_stick.protocol.state import AgentStatus, ProviderState, default_state
from vibe_stick.codex.quota import QuotaSnapshot
from vibe_stick.providers.base import ProviderObservation
from vibe_stick.server import app


class ServerProviderTests(unittest.TestCase):
    def test_configured_provider_accepts_known_values_only(self) -> None:
        with mock.patch.dict(os.environ, {"VIBE_STICK_PROVIDER": "claude"}):
            self.assertEqual(app._configured_provider(), "claude")
        with mock.patch.dict(os.environ, {"VIBE_STICK_PROVIDER": "bogus"}):
            self.assertEqual(app._configured_provider(), "auto")

    def test_computer_name_prefers_environment_override(self) -> None:
        with mock.patch.dict(os.environ, {"VIBE_STICK_COMPUTER_NAME": "Desk PC"}):
            self.assertEqual(app._computer_name(), "Desk PC")

    def test_computer_name_sanitizes_display_value(self) -> None:
        with mock.patch.dict(os.environ, {"VIBE_STICK_COMPUTER_NAME": "小雕 PC"}):
            self.assertEqual(app._computer_name(), "PC")

    def test_select_active_provider_respects_pinned_config(self) -> None:
        self.assertEqual(app._select_active_provider("claude", "codex", self._obs("codex"), self._obs("claude")), "claude")

    def test_select_active_provider_auto_uses_online_provider(self) -> None:
        selected = app._select_active_provider(
            "auto",
            "codex",
            self._obs("codex", online=False),
            self._obs("claude", online=True),
        )

        self.assertEqual(selected, "claude")

    def test_select_active_provider_auto_uses_recent_activity_when_both_online(self) -> None:
        selected = app._select_active_provider(
            "auto",
            "codex",
            self._obs("codex", latest=datetime(2026, 6, 28, 9, 0, tzinfo=timezone.utc)),
            self._obs("claude", latest=datetime(2026, 6, 28, 9, 1, tzinfo=timezone.utc)),
        )

        self.assertEqual(selected, "claude")

    def test_select_active_provider_auto_keeps_last_when_none_online(self) -> None:
        selected = app._select_active_provider(
            "auto",
            "claude",
            self._obs("codex", online=False),
            self._obs("claude", online=False),
        )

        self.assertEqual(selected, "claude")

    def test_select_alert_observation_uses_non_active_provider_alert(self) -> None:
        active = self._obs("claude")
        codex = self._obs(
            "codex",
            status=AgentStatus.DONE,
            alert_type="DONE",
            alert_event_id="evt_codex_done",
            alert_message="Codex task completed",
        )

        selected = app._select_alert_observation(active, codex, active)

        self.assertIs(selected, codex)

    def test_select_alert_observation_prefers_active_provider_alert(self) -> None:
        active = self._obs(
            "claude",
            status=AgentStatus.APPROVAL,
            alert_type="APPROVAL",
            alert_event_id="evt_claude_approval",
            alert_message="Claude is waiting for approval",
        )
        codex = self._obs(
            "codex",
            status=AgentStatus.DONE,
            alert_type="DONE",
            alert_event_id="evt_codex_done",
            alert_message="Codex task completed",
        )

        selected = app._select_alert_observation(active, codex, active)

        self.assertIs(selected, active)

    def test_running_provider_disappearance_becomes_error_alert(self) -> None:
        store = app.BridgeStateStore.__new__(app.BridgeStateStore)
        store._last_observed_status = {"codex": AgentStatus.RUNNING}
        observation = self._obs("codex", online=False, status=AgentStatus.OFFLINE)

        store._mark_unexpected_stops(observation)

        self.assertEqual(observation.status, AgentStatus.ERROR)
        self.assertEqual(observation.alert_type, "ERROR")
        self.assertIn("stopped unexpectedly", observation.alert_message)

    def test_idle_provider_disappearance_does_not_alert(self) -> None:
        store = app.BridgeStateStore.__new__(app.BridgeStateStore)
        store._last_observed_status = {"codex": AgentStatus.IDLE}
        observation = self._obs("codex", online=False, status=AgentStatus.OFFLINE)

        store._mark_unexpected_stops(observation)

        self.assertEqual(observation.status, AgentStatus.OFFLINE)
        self.assertEqual(observation.alert_type, "NONE")

    def test_claude_usage_interval_has_minimum(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(app._claude_usage_interval_seconds(), 300)
        with mock.patch.dict(os.environ, {"VIBE_STICK_CLAUDE_USAGE_INTERVAL_SECONDS": "5"}):
            self.assertEqual(app._claude_usage_interval_seconds(), 30)
        with mock.patch.dict(os.environ, {"VIBE_STICK_CLAUDE_USAGE_INTERVAL_SECONDS": "90"}):
            self.assertEqual(app._claude_usage_interval_seconds(), 90)

    def test_failed_claude_usage_refresh_keeps_cached_quota_stale(self) -> None:
        store = app.BridgeStateStore.__new__(app.BridgeStateStore)
        store._claude_quota = QuotaSnapshot(66, 96, "09:40", False)
        store._claude_usage_last_attempt = 0.0
        store._claude_usage_last_success = 1.0

        with mock.patch.object(app, "fetch_claude_usage", return_value=None):
            with mock.patch.object(app, "save_quota") as save_quota:
                store._refresh_claude_usage_locked(force=True)

        self.assertEqual(store._claude_quota.quota_5h_remaining, 66)
        self.assertEqual(store._claude_quota.quota_7d_remaining, 96)
        self.assertTrue(store._claude_quota.quota_stale)
        save_quota.assert_called_once_with(app.CLAUDE_QUOTA_PATH, store._claude_quota)

    def test_failed_claude_usage_without_cache_remains_unknown(self) -> None:
        store = app.BridgeStateStore.__new__(app.BridgeStateStore)
        store._claude_quota = QuotaSnapshot()
        store._claude_usage_last_attempt = 0.0
        store._claude_usage_last_success = 0.0

        with mock.patch.object(app, "fetch_claude_usage", return_value=None):
            with mock.patch.object(app, "save_quota") as save_quota:
                store._refresh_claude_usage_locked(force=True)

        self.assertIsNone(store._claude_quota.quota_5h_remaining)
        self.assertIsNone(store._claude_quota.quota_7d_remaining)
        save_quota.assert_not_called()

    def test_successful_claude_usage_refresh_saves_quota(self) -> None:
        store = app.BridgeStateStore.__new__(app.BridgeStateStore)
        store._claude_quota = QuotaSnapshot()
        store._claude_usage_last_attempt = 0.0
        store._claude_usage_last_success = 0.0
        refreshed = QuotaSnapshot(65, 95, "09:41", False)

        with mock.patch.object(app, "fetch_claude_usage", return_value=object()):
            with mock.patch.object(app, "claude_usage_to_quota", return_value=refreshed):
                with mock.patch.object(app, "save_quota") as save_quota:
                    store._refresh_claude_usage_locked(force=True)

        self.assertEqual(store._claude_quota, refreshed)
        save_quota.assert_called_once_with(app.CLAUDE_QUOTA_PATH, refreshed)

    def test_claude_quota_can_seed_from_saved_provider_state(self) -> None:
        state = default_state()
        state.provider = ProviderState(
            id="claude",
            display_name="Claude",
            implemented=True,
            status=AgentStatus.IDLE,
            quota_5h_remaining=26,
            quota_7d_remaining=92,
            quota_updated_at="22:44",
            quota_stale=False,
        )

        snapshot = app._claude_quota_from_state(state)

        self.assertEqual(snapshot.quota_5h_remaining, 26)
        self.assertEqual(snapshot.quota_7d_remaining, 92)
        self.assertEqual(snapshot.quota_updated_at, "22:44")
        self.assertTrue(snapshot.quota_stale)

    def test_claude_quota_does_not_seed_from_other_provider_state(self) -> None:
        state = default_state()
        state.provider = ProviderState(
            id="codex",
            display_name="Codex",
            implemented=True,
            status=AgentStatus.IDLE,
            quota_5h_remaining=26,
            quota_7d_remaining=92,
            quota_updated_at="22:44",
            quota_stale=False,
        )

        snapshot = app._claude_quota_from_state(state)

        self.assertIsNone(snapshot.quota_5h_remaining)
        self.assertIsNone(snapshot.quota_7d_remaining)

    def _obs(
        self,
        provider_id: str,
        *,
        online: bool = True,
        latest: datetime | None = None,
        status: AgentStatus = AgentStatus.IDLE,
        alert_type: str = "NONE",
        alert_message: str = "",
        alert_event_id: str = "",
    ) -> ProviderObservation:
        return ProviderObservation(
            provider_id=provider_id,
            display_name=provider_id.title(),
            online=online,
            status=status,
            quota_5h_remaining=None,
            quota_7d_remaining=None,
            quota_updated_at="",
            quota_stale=False,
            alert_type=alert_type,
            alert_message=alert_message,
            alert_event_id=alert_event_id,
            latest_event_timestamp=latest,
        )


if __name__ == "__main__":
    unittest.main()
