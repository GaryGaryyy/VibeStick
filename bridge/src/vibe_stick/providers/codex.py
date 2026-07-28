from __future__ import annotations

from datetime import datetime
from pathlib import Path

from vibe_stick.codex.local_observer import LocalCodexObservation
from vibe_stick.codex.local_observer import observe_codex as observe_local_codex
from vibe_stick.protocol.state import AgentStatus
from vibe_stick.providers.base import ProviderObservation


def observe_codex(project_root: Path) -> ProviderObservation:
    return observation_from_local_codex(observe_local_codex(project_root))


def observation_from_local_codex(observation: LocalCodexObservation) -> ProviderObservation:
    quota = observation.quota
    alert_type = observation.alert_type or "NONE"
    alert_message = observation.alert_message
    alert_event_id = ""
    if observation.alert_timestamp is not None and observation.status in {
        AgentStatus.DONE,
        AgentStatus.APPROVAL,
        AgentStatus.ERROR,
    }:
        alert_type = alert_type if alert_type != "NONE" else observation.status.value
        alert_event_id = _stable_event_id(alert_type.lower(), observation.alert_timestamp)

    return ProviderObservation(
        provider_id="codex",
        display_name="Codex",
        online=observation.codex_online,
        status=observation.status,
        quota_5h_remaining=quota.quota_5h_remaining if quota is not None else None,
        quota_7d_remaining=quota.quota_7d_remaining if quota is not None else None,
        quota_updated_at=quota.quota_updated_at if quota is not None else "",
        quota_stale=quota.quota_stale if quota is not None else False,
        alert_type=alert_type,
        alert_message=alert_message,
        alert_event_id=alert_event_id,
        latest_event_timestamp=observation.latest_event_timestamp,
    )


def _stable_event_id(prefix: str, timestamp: datetime) -> str:
    return f"evt_{timestamp.astimezone().strftime('%Y%m%d_%H%M%S')}_{prefix}"
