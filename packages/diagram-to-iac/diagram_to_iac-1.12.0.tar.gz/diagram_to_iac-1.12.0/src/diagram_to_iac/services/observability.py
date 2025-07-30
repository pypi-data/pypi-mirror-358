from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import threading
from typing import Any, Dict


class LogBus:
    """Simple JSONL logging service."""

    def __init__(self, log_dir: str | Path | None = None) -> None:
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).resolve().parents[3] / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.log_path = self.log_dir / f"run-{timestamp}.jsonl"
        self._lock = threading.Lock()

    def log(self, event: Dict[str, Any]) -> None:
        """Append an event as a JSON line with timestamp."""
        payload = event.copy()
        payload.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        line = json.dumps(payload)
        with self._lock:
            try:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception as exc:  # noqa: BLE001
                # Logging should never raise; print error and continue
                print(f"LogBus write failed: {exc}")


_global_bus: LogBus | None = None


def _get_bus() -> LogBus:
    global _global_bus
    if _global_bus is None:
        _global_bus = LogBus()
    return _global_bus


def log_event(event_type: str, **kwargs: Any) -> None:
    """Write a structured log event using the global bus."""
    event = {"type": event_type, **kwargs}
    _get_bus().log(event)


def get_log_path() -> Path:
    """Return the path of the current log file."""
    return _get_bus().log_path


def reset_log_bus() -> None:
    """Create a fresh global log bus with a new log file."""
    global _global_bus
    # Nothing to close since LogBus opens files on demand
    _global_bus = LogBus()
