# Changelog

## v0.1.5

- Stable StickS3 home screen update: dimmer backlight, original CPU/power defaults, and a computer-name panel instead of 5H / 7D quota bars.
- Status dot colors now use green for running/done, yellow for approval, and red for errors.
- Recording upload, ASR, transcript rejection, and paste failures now play the error alert sound.
- Added a Windows Wi-Fi bridge runner script. Runtime state, alerts, recording, and paste handling stay on Wi-Fi.
- Bridge state now includes `computer_name`, with `VIBE_STICK_COMPUTER_NAME` as an override.

## v0.1.4

Initial public release of VibeStick — a tiny desktop companion for coding agents on M5Stack StickS3.

- Home screen shows Codex and Claude providers with live status (running / idle / done / approval / error / offline) and independent 5-hour / 7-day usage bars.
- Opt-in real Claude Code subscription usage (5H / 7D) via an undocumented Anthropic endpoint using local credentials; disabled by default, and the token / raw responses are never logged.
- Push-to-talk voice input: record on the StickS3, transcribe via any OpenAI-compatible ASR (e.g. SiliconFlow), and paste into the focused app; a local-command / fully-offline path is also supported.
- Alerts (done / approval / error) play from whichever provider raises them, on the StickS3 speaker.
- First-run helpers (`scripts/setup.sh`, `scripts/doctor.sh`), bridge token authentication, and a bilingual README (English + 中文) with clearly-marked physical steps.

Licensed under MIT.
