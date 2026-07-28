# Changelog

## v0.1.8

- Treat cancelled, interrupted, crashed, or unexpectedly stopped agent tasks as errors so the StickS3 plays the error alert sound.
- Reduce idle power use with 80 MHz CPU operation, Wi-Fi modem sleep, 5-second state polling, 30-second battery refreshes, and lower backlight brightness.

## v0.1.7

- Distinguish an unreachable bridge from an online bridge whose local Codex/Claude provider is not running; the StickS3 now shows `待命` for the latter instead of `离线`.

## v0.1.6

- Search picker uses a complete ASCII font and sanitizes discovered computer names so names and host details remain visible on StickS3.
- Firmware treats non-2xx bridge responses as failures instead of accepting error JSON as state.
- Recording start failures are shown on StickS3, and audio stop failures now trigger the configured error alert.
- Windows installer registers a hidden per-user Scheduled Task, starts the bridge immediately, and keeps the command runner as a manual fallback.
- Windows installer also starts a no-console recording overlay that appears only while the StickS3 is recording or transcribing.
- Windows documentation now states that recording uses the StickS3 microphone over Wi-Fi and that the Windows `.env` needs its own ASR configuration.

## v0.1.5

- Stable StickS3 home screen update: dimmer backlight, 5-second idle backlight sleep, 160 MHz CPU default, and a computer-name panel instead of 5H / 7D quota bars.
- Status dot colors now use green for running/done, yellow for approval, and red for errors.
- Recording upload, ASR, transcript rejection, and paste failures now play the error alert sound.
- Added a Windows Wi-Fi bridge runner script. Runtime state, alerts, recording, and paste handling stay on Wi-Fi.
- Bridge state now includes `computer_name`, with `VIBE_STICK_COMPUTER_NAME` as an override.
- Project names are no longer exposed in bridge state or rendered on the StickS3 home screen.
- Added simple LAN computer discovery: the StickS3 broadcasts over Wi-Fi, passes its bridge token, and stores the selected bridge host.

## v0.1.4

Initial public release of VibeStick — a tiny desktop companion for coding agents on M5Stack StickS3.

- Home screen shows Codex and Claude providers with live status (running / idle / done / approval / error / offline) and independent 5-hour / 7-day usage bars.
- Opt-in real Claude Code subscription usage (5H / 7D) via an undocumented Anthropic endpoint using local credentials; disabled by default, and the token / raw responses are never logged.
- Push-to-talk voice input: record on the StickS3, transcribe via any OpenAI-compatible ASR (e.g. SiliconFlow), and paste into the focused app; a local-command / fully-offline path is also supported.
- Alerts (done / approval / error) play from whichever provider raises them, on the StickS3 speaker.
- First-run helpers (`scripts/setup.sh`, `scripts/doctor.sh`), bridge token authentication, and a bilingual README (English + 中文) with clearly-marked physical steps.

Licensed under MIT.
