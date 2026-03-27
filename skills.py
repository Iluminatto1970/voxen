import os
from pathlib import Path


def skill_analyze_project(workspace_dir: str = "workspace") -> dict:
    """
    Skill: mapeia a estrutura do projeto para dar contexto ao Squad.
    """
    workspace = Path(workspace_dir)
    files = []

    if not workspace.exists():
        return {
            "msg": "Workspace não encontrado. Crie o ambiente antes da análise.",
            "files_count": 0,
            "structure": [],
        }

    for root, _, filenames in os.walk(workspace):
        for filename in filenames:
            full_path = Path(root) / filename
            files.append(str(full_path))

    files.sort()

    return {
        "msg": "Análise de terreno concluída, Iluminatto.",
        "files_count": len(files),
        "structure": files,
    }
