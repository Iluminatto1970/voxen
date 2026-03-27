class VoxenModelProfiles:
    """
    Perfis por provedor/modelo para guiar prompts e estilo de execucao.
    """

    def __init__(self) -> None:
        self.profiles = {
            "gpt": {
                "style": "Objetivo, estruturado e orientado a entrega.",
                "constraints": "Evitar overengineering e manter foco em MVI.",
            },
            "gemini": {
                "style": "Analitico com comparacoes e alternativas.",
                "constraints": "Sempre fechar com decisao executavel.",
            },
            "claude": {
                "style": "Raciocinio cuidadoso e explicacoes claras.",
                "constraints": "Priorizar seguranca e revisao incremental.",
            },
            "local": {
                "style": "Prompts curtos e objetivos para menor latencia.",
                "constraints": "Quebrar tarefas em passos pequenos.",
            },
        }

    def list_profiles(self) -> list[str]:
        return sorted(self.profiles.keys())

    def describe(self, name: str) -> dict:
        return self.profiles.get(name, self.profiles["gpt"])
