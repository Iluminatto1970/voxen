import subprocess
from pathlib import Path
from typing import Callable


class OpenCodeExecutor:
    """
    O Braço do Squad: executa comandos no mundo real (Terminal).
    Baseado na filosofia Antigravity: permissão total, responsabilidade total.
    """

    def __init__(self, workspace_dir: str = "workspace") -> None:
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self._skills: dict[str, Callable[..., dict]] = {}

    def execute_command(self, command: str) -> dict:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.workspace,
            )

            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }
        except Exception as exc:
            return {"status": "exception", "error": str(exc)}

    def write_file(self, file_path: str, content: str) -> str:
        full_path = self.workspace / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return f"Arquivo {file_path} escrito com sucesso."

    def register_skill(self, name: str, handler: Callable[..., dict]) -> None:
        self._skills[name] = handler

    def run_skill(self, name: str, **kwargs) -> dict:
        if name not in self._skills:
            return {
                "status": "error",
                "error": f"Skill '{name}' não registrada.",
            }
        try:
            response = self._skills[name](**kwargs)
            return {"status": "success", "result": response}
        except Exception as exc:
            return {"status": "exception", "error": str(exc)}


# Instância inicial para o Iluminatto
executor = OpenCodeExecutor()
