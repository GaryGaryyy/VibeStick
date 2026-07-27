from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, urlparse

from vibe_stick import __version__ as BRIDGE_VERSION
from vibe_stick.config.dotenv import load_dotenv_files
from vibe_stick.server.app import BRIDGE_NAME, BridgeStateStore, _with_bridge_metadata

PROTOCOL_PREFIX = "VSJ1 "
DEFAULT_BAUD = 921600


@dataclass
class UsbBridgeSession:
    store: BridgeStateStore = field(default_factory=BridgeStateStore)
    audio_chunks: dict[str, bytearray] = field(default_factory=dict)

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        request_id = str(request.get("id") or "")
        try:
            body = self._dispatch(request)
            return {"id": request_id, "ok": True, "status": 200, "body": body}
        except Exception as exc:  # pragma: no cover - defensive boundary around serial input
            return {"id": request_id, "ok": False, "status": 500, "error": str(exc)}

    def _dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        method = str(request.get("method") or "GET").upper()
        path = str(request.get("path") or "")
        body = request.get("body")
        body_dict = body if isinstance(body, dict) else {}
        parsed = urlparse(path)

        if method == "GET" and parsed.path == "/state":
            return _with_bridge_metadata(self.store.get_state().to_jsonable())
        if method == "GET" and parsed.path == "/health":
            return {"ok": True, "bridge_name": BRIDGE_NAME, "bridge_version": BRIDGE_VERSION}
        if method != "POST":
            raise ValueError(f"Unsupported USB bridge method/path: {method} {path}")

        if parsed.path == "/event":
            return self.store.update_from_event(body_dict).to_jsonable()
        if parsed.path == "/quota/refresh":
            state = self.store.refresh_quota()
            return {"refreshed": True, "state": state.to_jsonable()}
        if parsed.path == "/recording/start":
            return self.store.start_recording(body_dict)
        if parsed.path == "/recording/audio":
            return self._handle_audio_upload(parsed.query, request)
        if parsed.path == "/recording/stop":
            return self.store.stop_recording(body_dict)
        raise ValueError(f"Unknown USB bridge path: {path}")

    def _handle_audio_upload(self, query: str, request: dict[str, Any]) -> dict[str, Any]:
        query_values = parse_qs(query)
        session_id = _first(query_values, "session_id") or str(request.get("session_id") or "")
        if not session_id:
            raise ValueError("recording/audio requires session_id")
        encoding = str(request.get("encoding") or "")
        if encoding != "base64":
            raise ValueError("recording/audio requires base64 encoding over USB")
        payload = str(request.get("body") or "")
        chunk = base64.b64decode(payload.encode("ascii"), validate=True) if payload else b""
        buffer = self.audio_chunks.setdefault(session_id, bytearray())
        buffer.extend(chunk)

        if not bool(request.get("final", False)):
            return {"received": len(buffer), "session_id": session_id}

        pcm = bytes(buffer)
        self.audio_chunks.pop(session_id, None)
        return self.store.upload_recording_audio(
            pcm,
            session_id=session_id,
            sample_rate=int(request.get("sample_rate") or 16000),
            channels=int(request.get("channels") or 1),
            bits_per_sample=int(request.get("bits_per_sample") or 16),
        )


def _first(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key) or []
    return values[0] if values else ""


def run_usb_bridge(port: str = "", baud: int = DEFAULT_BAUD) -> None:
    load_dotenv_files()
    serial_module = _import_serial()
    session = UsbBridgeSession()
    while True:
        for candidate in _candidate_ports(serial_module, port):
            try:
                _serve_port(serial_module, candidate, baud, session)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"USB bridge port {candidate} unavailable: {exc}", flush=True)
                time.sleep(1.0)
        if port:
            time.sleep(1.0)
        else:
            time.sleep(2.0)


def _serve_port(serial_module: Any, port: str, baud: int, session: UsbBridgeSession) -> None:
    print(f"VibeStick USB bridge listening on {port}", flush=True)
    with serial_module.Serial(port, baudrate=baud, timeout=0.25, write_timeout=1.0) as serial_port:
        while True:
            raw = serial_port.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith(PROTOCOL_PREFIX):
                continue
            payload = line[len(PROTOCOL_PREFIX):]
            try:
                request = json.loads(payload)
            except json.JSONDecodeError as exc:
                response = {"id": "", "ok": False, "status": 400, "error": str(exc)}
            else:
                response = session.handle_request(request if isinstance(request, dict) else {})
            encoded = PROTOCOL_PREFIX + json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n"
            serial_port.write(encoded.encode("utf-8"))
            serial_port.flush()


def _candidate_ports(serial_module: Any, configured: str) -> list[str]:
    if configured:
        return [configured]
    ports = list(serial_module.tools.list_ports.comports())
    preferred = []
    fallback = []
    for info in ports:
        text = " ".join(str(part or "") for part in (info.device, info.description, info.manufacturer, info.hwid))
        if any(token in text.lower() for token in ("esp32", "usb jtag", "usb serial", "cp210", "wch")):
            preferred.append(info.device)
        else:
            fallback.append(info.device)
    return preferred + fallback


def _import_serial() -> Any:
    try:
        import serial
        import serial.tools.list_ports
    except ImportError as exc:
        raise SystemExit(
            "pyserial is required for the USB bridge. Install with: "
            "python -m pip install pyserial"
        ) from exc
    return serial


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run VibeStick USB serial bridge.")
    parser.add_argument("--port", default="", help="Serial port, such as COM5. Omit to scan.")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        run_usb_bridge(port=args.port, baud=args.baud)
    except KeyboardInterrupt:
        print("USB bridge stopped.", flush=True)
        raise SystemExit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
