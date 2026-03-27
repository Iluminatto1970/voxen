class SkillFactory:
    """
    Repositório de conhecimento: define contexto de stack e regras de execução.
    """

    def __init__(self) -> None:
        self.skills = {
            "web_fullstack": {
                "stack": ["Next.js", "Tailwind", "PostgreSQL"],
                "best_practices": "Use Server Components e mantenha o schema do DB normalizado.",
                "test_cmd": "npm run test",
            },
            "automation_cli": {
                "stack": ["Python", "Typer", "Rich"],
                "best_practices": "Documente com docstrings e use type hints em tudo.",
                "test_cmd": "pytest",
            },
            "growth_leads": {
                "stack": ["n8n", "WhatsApp API", "Stripe"],
                "best_practices": "Foco em conversão e log completo de eventos de clique.",
                "test_cmd": "python scripts/check_webhooks.py",
            },
        }

    def get_skill_context(self, skill_name: str) -> str:
        skill = self.skills.get(skill_name)
        if not skill:
            return "Skill genérica: use boas práticas de Clean Code."
        return (
            f"Você está no modo {skill_name}. "
            f"Stack: {', '.join(skill['stack'])}. "
            f"Regras: {skill['best_practices']}"
        )

    def get_test_command(self, skill_name: str) -> str:
        skill = self.skills.get(skill_name)
        if not skill:
            return ""
        return skill.get("test_cmd", "")


factory = SkillFactory()
