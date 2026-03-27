class VoxenPolicyEngine:
    """
    Regras de seguranca e gates operacionais.
    """

    def __init__(self) -> None:
        self.blocked_patterns = [
            "rm -rf /",
            "mkfs",
            "shutdown",
            "reboot",
            "chmod -R 777 /",
            ":(){ :|:& };:",
        ]

    def pre_execution(self, command: str) -> tuple[bool, str]:
        lowered = command.lower().strip()
        for pattern in self.blocked_patterns:
            if pattern in lowered:
                return False, f"Comando bloqueado por politica: {pattern}"
        return True, "Comando aprovado pela politica de execucao."

    def pre_deploy(self, qa_approved: bool, target: str) -> tuple[bool, str]:
        if not qa_approved:
            return False, "Deploy bloqueado: QA nao aprovado."
        if target.lower() not in {"vercel", "aws", "staging"}:
            return False, "Deploy bloqueado: alvo nao permitido."
        return True, "Deploy aprovado pela politica."
