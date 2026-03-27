import json
import time
from datetime import datetime
from pathlib import Path


class VoxenEvaluator:
    """
    Avaliacao continua de execucoes e comandos.
    """

    def __init__(self, metrics_file: str) -> None:
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.metrics_file.exists():
            self.metrics_file.write_text("", encoding="utf-8")

    def timer(self) -> float:
        return time.perf_counter()

    def record(self, kind: str, status: str, payload: dict | None = None, started_at: float | None = None) -> None:
        elapsed_ms = None
        if started_at is not None:
            elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "kind": kind,
            "status": status,
            "elapsed_ms": elapsed_ms,
            "payload": payload or {},
        }
        with self.metrics_file.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _read_entries(self) -> list[dict]:
        entries = []
        for line in self.metrics_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries

    def summary(self) -> dict:
        entries = self._read_entries()
        total = len(entries)
        if total == 0:
            return {"total": 0, "success_rate": 0.0, "avg_ms": 0.0, "kinds": {}}

        success = sum(1 for e in entries if e.get("status") in {"success", "completed", "approved"})
        durations = [e.get("elapsed_ms") for e in entries if isinstance(e.get("elapsed_ms"), (int, float))]
        avg_ms = round(sum(durations) / len(durations), 2) if durations else 0.0

        kinds: dict[str, int] = {}
        for entry in entries:
            kind = entry.get("kind", "unknown")
            kinds[kind] = kinds.get(kind, 0) + 1

        return {
            "total": total,
            "success_rate": round((success / total) * 100, 2),
            "avg_ms": avg_ms,
            "kinds": kinds,
        }
