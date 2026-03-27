import json
import re
from pathlib import Path


class VoxenRegistry:
    """
    Registro local de squads no estilo Voxen.
    """

    def __init__(self, squads_dir: str = "squads") -> None:
        self.squads_dir = Path(squads_dir)
        self.squads_dir.mkdir(parents=True, exist_ok=True)

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip().lower())
        slug = slug.strip("-")
        return slug or "squad-sem-nome"

    def list_squads(self) -> list[str]:
        squads = []
        for item in self.squads_dir.iterdir():
            if item.is_dir() and (item / "squad.json").exists():
                squads.append(item.name)
        squads.sort()
        return squads

    def create_squad(self, name: str, description: str, mode: str, steps: list[dict]) -> Path:
        squad_name = self._slugify(name)
        squad_dir = self.squads_dir / squad_name
        squad_dir.mkdir(parents=True, exist_ok=True)
        (squad_dir / "output").mkdir(parents=True, exist_ok=True)
        (squad_dir / "_memory").mkdir(parents=True, exist_ok=True)

        squad_definition = {
            "name": squad_name,
            "display_name": name,
            "description": description,
            "mode": mode,
            "steps": steps,
        }
        (squad_dir / "squad.json").write_text(
            json.dumps(squad_definition, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        memory_file = squad_dir / "_memory" / "memories.jsonl"
        if not memory_file.exists():
            memory_file.write_text("", encoding="utf-8")
        return squad_dir

    def load_squad(self, name: str) -> dict | None:
        squad_name = self._slugify(name)
        squad_file = self.squads_dir / squad_name / "squad.json"
        if not squad_file.exists():
            return None
        try:
            return json.loads(squad_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
