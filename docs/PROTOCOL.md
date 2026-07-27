# Protocol

VibeStick uses HTTP over Wi-Fi between the StickS3 firmware and the local bridge. USB is not a
runtime transport for state, events, recording, or paste injection.

Default bridge URL:

```text
http://<mac-ip>:8765
```

## UDP Discovery

The bridge listens on UDP port `8766`. A StickS3 can broadcast:

```json
{"type":"vibestick_discover","token":"<bridge-token>","device":"VibeStick"}
```

The bridge responds to the sender:

```json
{"type":"vibestick_bridge","name":"Desk PC","port":8765,"version":"0.1.5"}
```

The StickS3 uses the response sender IP as the bridge host. If the bridge has no configured token, it remembers the token from discovery for later HTTP requests.

## Firmware Headers

Firmware requests include:

```text
X-Vibe-Stick-Firmware-Name: vibestick
X-Vibe-Stick-Firmware-Version: 0.1.2
X-Vibe-Stick-Firmware-Transport: HTTP
X-Vibe-Stick-Firmware-Build-Date: <compile date>
```

Audio upload requests additionally include:

```text
X-Vibe-Stick-Sample-Rate: 16000
X-Vibe-Stick-Channels: 1
X-Vibe-Stick-Bits-Per-Sample: 16
```

When `VIBE_STICK_BRIDGE_TOKEN` is configured on the bridge and firmware, protected POST requests also include:

```text
X-Vibe-Stick-Token: <shared-token>
```

Protected endpoints are `/event`, `/quota/refresh`, `/recording/start`, `/recording/audio`, and `/recording/stop`. When the bridge has a configured or discovery-paired token, POST requests must include it. If no token is available yet, the personal-LAN bridge accepts requests so first-time Wi-Fi pairing stays simple.

## GET /state

Returns the current bridge state:

```json
{
  "time": "13:01",
  "wifi": true,
  "ble": false,
  "battery": null,
  "computer_name": "Gary-MacBook-Pro",
  "active_provider": "claude",
  "provider": {
    "id": "claude",
    "display_name": "Claude",
    "implemented": true,
    "status": "RUNNING",
    "quota_5h_remaining": 66,
    "quota_7d_remaining": 96,
    "quota_updated_at": "13:01",
    "quota_stale": false
  },
  "codex": {
    "status": "RUNNING",
    "quota_5h_remaining": 53,
    "quota_7d_remaining": 93,
    "quota_updated_at": "13:01",
    "quota_stale": false
  },
  "alert": {
    "event_id": "",
    "type": "NONE",
    "message": ""
  },
  "bridge_name": "vibestick-bridge",
  "bridge_version": "0.1.2"
}
```

`battery` is intentionally `null` from the bridge. The StickS3 displays its local PMIC battery reading.
`computer_name` is the bridge computer name, optionally overridden by `VIBE_STICK_COMPUTER_NAME`.

`active_provider` selects which normalized `provider` block the firmware should render. `provider.quota_5h_remaining` and `provider.quota_7d_remaining` are remaining percentages from `0` to `100`; `null` means unknown and the firmware renders `--%`. The legacy `codex` block remains present for backward compatibility.

## GET /health

Returns bridge health metadata:

```json
{
  "ok": true,
  "bridge_name": "vibestick-bridge",
  "bridge_version": "0.1.2"
}
```

## POST /event

Receives generic firmware or debug events.

Examples:

```json
{"event":"button_short","source":"sticks3"}
```

```json
{"event":"test_agent_status","source":"manual_test","status":"DONE","message":"test done"}
```

Manual `DONE`, `ERROR`, and `APPROVAL` statuses produce alert fields for local testing.

## POST /quota/refresh

Requests a quota refresh for the active provider. Codex refreshes from local session events. Claude refreshes the cached usage snapshot only when `VIBE_STICK_CLAUDE_USAGE` is enabled; failures keep the provider quota fields `null` so the firmware shows `--%`.

```json
{
  "refreshed": true,
  "state": {
    "time": "13:01",
    "wifi": true,
    "battery": null
  }
}
```

## POST /recording/start

Starts a recording session:

```json
{
  "event": "button_long_start",
  "source": "sticks3",
  "audio_source": "sticks3_pcm",
  "session_id": "<firmware-generated-id>"
}
```

## POST /recording/audio

Uploads raw little-endian signed PCM for the active session:

```text
POST /recording/audio?session_id=<id>
Content-Type: application/octet-stream
```

The bridge writes a local WAV file under:

```text
~/Library/Application Support/VibeStick/Recordings/
```

The bridge rejects audio uploads larger than `VIBE_STICK_MAX_RECORDING_AUDIO_BYTES`. The default is `2000000` bytes.

## POST /recording/stop

Stops the session and runs transcription:

```json
{"event":"button_long_stop","source":"sticks3","paste":true}
```

When transcription succeeds, the bridge pastes the transcript into the focused macOS app. Recording status does not trigger agent alert sounds.
