import hashlib
import json
from datetime import datetime
from pathlib import Path


class MessageBus:
    """
    Barramento de mensagens com protecao contra loops.
    """

    def __init__(self, bus_file: str = "message_bus.json") -> None:
        self.bus_file = Path(bus_file)
        self.state = self._load_state()

    def _default_state(self) -> dict:
        return {"messages": [], "blocked": []}

    def _load_state(self) -> dict:
        if not self.bus_file.exists():
            return self._default_state()
        try:
            return json.loads(self.bus_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return self._default_state()

    def _save_state(self) -> None:
        self.bus_file.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _signature(self, sender: str, receiver: str, body: str) -> str:
        raw = f"{sender}|{receiver}|{body}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _is_loop(self, signature: str, max_repeat: int = 3, recent_window: int = 20) -> bool:
        recent = self.state["messages"][-recent_window:]
        count = sum(1 for item in recent if item.get("signature") == signature)
        return count >= max_repeat

    def publish(self, sender: str, receiver: str, body: str) -> dict:
        signature = self._signature(sender, receiver, body)
        now = datetime.now().isoformat()

        if self._is_loop(signature):
            blocked_entry = {
                "timestamp": now,
                "sender": sender,
                "receiver": receiver,
                "body": body,
                "reason": "loop_detected",
                "signature": signature,
            }
            self.state["blocked"].append(blocked_entry)
            self._save_state()
            return {"accepted": False, "reason": "loop_detected", "entry": blocked_entry}

        entry = {
            "timestamp": now,
            "sender": sender,
            "receiver": receiver,
            "body": body,
            "signature": signature,
        }
        self.state["messages"].append(entry)
        self._save_state()
        return {"accepted": True, "entry": entry}

    def get_recent_messages(self, limit: int = 20) -> list[dict]:
        return self.state["messages"][-limit:]
