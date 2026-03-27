from pathlib import Path


class VoxenOrchestrator:
    """
    O General: direciona o Squad para frentes lucrativas com contexto isolado.
    """

    def __init__(self, base_workspace: str = "workspace") -> None:
        self.base_workspace = Path(base_workspace)
        self.base_workspace.mkdir(parents=True, exist_ok=True)
        self.modes = {
            "micro_saas": {
                "context": "Foco: Conversão e Assinatura. Stack: Next.js/Stripe.",
                "state_file": "voxen_state_micro_saas.json",
            },
            "dev_tool_cli": {
                "context": "Foco: Performance e Segurança. Stack: Rust/Python.",
                "state_file": "voxen_state_dev_tool_cli.json",
            },
            "support_agent": {
                "context": "Foco: Retenção e Resolução. Stack: RAG/VectorDB.",
                "state_file": "voxen_state_support_agent.json",
            },
        }

    def list_modes(self) -> list[str]:
        return list(self.modes.keys())

    def get_workspace_for_mode(self, mode_name: str) -> Path:
        return self.base_workspace / mode_name

    def get_state_file_for_mode(self, mode_name: str) -> str:
        config = self.modes.get(mode_name)
        if not config:
            return "voxen_state.json"
        return config["state_file"]

    def deploy_war_room(self, mode_name: str) -> str:
        if mode_name not in self.modes:
            return "Modo inválido, Iluminatto. Não perca tempo."

        workspace = self.get_workspace_for_mode(mode_name)
        workspace.mkdir(parents=True, exist_ok=True)
        context = self.modes[mode_name]["context"]

        mission_file = workspace / "MISSION_SCOPE.md"
        mission_file.write_text(
            f"# Missão Atual: {mode_name}\n\nContexto: {context}\n",
            encoding="utf-8",
        )

        return (
            f"Squad reconfigurado para {mode_name}. "
            f"Workspace isolado em {workspace}. O exército está em posição."
        )


orchestrator = VoxenOrchestrator()
