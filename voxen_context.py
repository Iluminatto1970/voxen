import json
import re
from pathlib import Path


class VoxenContextEngine:
    """
    Descobre padroes de projeto e gera contexto minimo viavel (MVI).
    """

    def __init__(self, workspace_dir: str, cache_file: str | None = None) -> None:
        self.workspace = Path(workspace_dir)
        self.cache_file = Path(cache_file) if cache_file else self.workspace / "_memory" / "context_snapshot.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def _iter_files(self, limit: int = 4000) -> list[Path]:
        if not self.workspace.exists():
            return []
        files = []
        for path in self.workspace.rglob("*"):
            if not path.is_file():
                continue
            if "/.git/" in str(path):
                continue
            files.append(path)
            if len(files) >= limit:
                break
        return files

    def _guess_stack(self, files: list[Path]) -> list[str]:
        names = {f.name for f in files}
        suffixes = {f.suffix.lower() for f in files}
        stack = []

        if "package.json" in names:
            stack.append("node")
        if "pyproject.toml" in names or "requirements.txt" in names:
            stack.append("python")
        if "Cargo.toml" in names:
            stack.append("rust")
        if "go.mod" in names:
            stack.append("go")
        if ".tsx" in suffixes or ".jsx" in suffixes:
            stack.append("react")
        if "next.config.js" in names or "next.config.mjs" in names or "next.config.ts" in names:
            stack.append("nextjs")
        if "docker-compose.yml" in names or "Dockerfile" in names:
            stack.append("docker")

        return stack

    def _collect_keywords(self, files: list[Path], max_files: int = 120) -> list[str]:
        tokens_count: dict[str, int] = {}
        word_pattern = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{3,}")

        for file in files[:max_files]:
            try:
                content = file.read_text(encoding="utf-8")
            except Exception:
                continue
            for token in word_pattern.findall(content.lower()):
                if token in {"true", "false", "none", "null", "self", "this", "return", "class"}:
                    continue
                tokens_count[token] = tokens_count.get(token, 0) + 1

        sorted_tokens = sorted(tokens_count.items(), key=lambda x: x[1], reverse=True)
        return [token for token, _ in sorted_tokens[:40]]

    def analyze(self) -> dict:
        files = self._iter_files()
        relative_files = [str(f.relative_to(self.workspace)) for f in files]
        stack = self._guess_stack(files)
        keywords = self._collect_keywords(files)

        snapshot = {
            "workspace": str(self.workspace),
            "files_count": len(files),
            "stack": stack,
            "important_files": sorted(relative_files)[:200],
            "keywords": keywords,
        }
        self.cache_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        return snapshot

    def load_snapshot(self) -> dict | None:
        if not self.cache_file.exists():
            return None
        try:
            return json.loads(self.cache_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def mvi_context_for(self, intent: str, max_files: int = 20) -> dict:
        snapshot = self.load_snapshot() or self.analyze()
        intent_tokens = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", intent.lower()))
        selected = []

        for file_path in snapshot.get("important_files", []):
            file_tokens = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", file_path.lower()))
            overlap = len(intent_tokens.intersection(file_tokens))
            if overlap > 0:
                selected.append((overlap, file_path))

        selected.sort(key=lambda x: x[0], reverse=True)
        selected_files = [path for _, path in selected[:max_files]]

        return {
            "stack": snapshot.get("stack", []),
            "keywords": snapshot.get("keywords", [])[:20],
            "selected_files": selected_files,
            "intent": intent,
        }

    def domain_context(self) -> dict:
        snapshot = self.load_snapshot() or self.analyze()
        product = []
        technical = []
        business = []

        for file_path in snapshot.get("important_files", []):
            lower = file_path.lower()
            if any(token in lower for token in ["readme", "docs", "guide", "roadmap"]):
                product.append(file_path)
            elif any(token in lower for token in ["billing", "stripe", "growth", "sales", "landing"]):
                business.append(file_path)
            else:
                technical.append(file_path)

        return {
            "product": product[:20],
            "technical": technical[:20],
            "business": business[:20],
        }
