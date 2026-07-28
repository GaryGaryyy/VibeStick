# States And Sounds

VibeStick v0.1.2 plays sounds only for key agent status changes on the home screen. Recording states do not play sounds.

| State | Trigger | Sound |
| --- | --- | --- |
| Completed / 完成 | Codex or Claude reports `DONE`, `COMPLETED`, or `SUCCESS` | 880 Hz 80 ms, 40 ms gap, 1320 Hz 120 ms |
| Error / 报错 | Codex or Claude reports `ERROR`, `FAILED`, or `FAILURE` | 240 Hz 100 ms, 60 ms gap, repeated 3 times |
| Recording failed / 识别失败 | Recording upload, ASR, transcript rejection, or paste injection fails | 240 Hz 100 ms, 60 ms gap, repeated 3 times |
| Waiting for approval / 等待审批 | Codex or Claude reports `APPROVAL`, `WAITING_APPROVAL`, `PENDING_APPROVAL`, or `NEEDS_APPROVAL` | 600 Hz 100 ms, 60 ms gap, 800 Hz 100 ms |

## No Sound

These states and events do not play sounds:

- Recording start.
- Recording in progress.
- Idle.
- Ready.
- Running.
- Thinking.
- Polling.
- Provider switching.
- Quota refresh.
- Quota stale.
- Screen refresh.
- `/state` polling.

## Implementation

Sound generation lives in `firmware/sticks3/src/vibe_audio.c`.

The firmware generates 16 kHz mono 16-bit PCM in memory and plays it through the ES8311 / I2S speaker path. No WAV, MP3, TTS, or network service is used for agent alert sounds.

Recording has priority. If recording is active, alert sounds are skipped instead of queued.

Duplicate prevention lives in `firmware/sticks3/src/main.c`. A sound is played only once for a new `alert.event_id`; if no event id exists, the firmware falls back to status-edge detection.
