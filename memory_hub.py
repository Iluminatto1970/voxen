import json
import re
from datetime import datetime
from pathlib import Path


class MemoryHub:
    """
    Memoria de longo prazo baseada em JSONL com recall por similaridade lexical.
    """

    def __init__(self, memory_file: str) -> None:
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            self.memory_file.write_text("", encoding="utf-8")

    def _tokenize(self, text: str) -> set[str]:
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        return set(tokens)

    def remember(self, kind: str, content: str, metadata: dict | None = None) -> dict:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "kind": kind,
            "content": content,
            "metadata": metadata or {},
        }
        with self.memory_file.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def all_entries(self) -> list[dict]:
        entries = []
        for line in self.memory_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries

    def recall(self, query: str, limit: int = 5) -> list[dict]:
        q_tokens = self._tokenize(query)
        scored = []
        for entry in self.all_entries():
            content_tokens = self._tokenize(entry.get("content", ""))
            overlap = len(q_tokens.intersection(content_tokens))
            if overlap > 0:
                scored.append((overlap, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:limit]]
