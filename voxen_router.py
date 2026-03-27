from voxen_manager import AgentRole


class VoxenIntentRouter:
    """
    Roteador automatico de intencao -> agente + skill + workflow.
    """

    def __init__(self) -> None:
        self.routes = [
            {
                "keywords": ["bug", "erro", "debug", "falha", "stacktrace"],
                "role": AgentRole.QA,
                "workflow": "debug",
                "skill": "automation_cli",
                "specialist": "qa-automation-engineer",
            },
            {
                "keywords": ["teste", "test", "coverage", "cobertura"],
                "role": AgentRole.QA,
                "workflow": "test",
                "skill": "automation_cli",
                "specialist": "test-engineer",
            },
            {
                "keywords": ["deploy", "publicar", "release", "producao"],
                "role": AgentRole.GROWTH,
                "workflow": "deploy",
                "skill": "growth_leads",
                "specialist": "devops-engineer",
            },
            {
                "keywords": ["landing", "lead", "campanha", "conversao", "marketing"],
                "role": AgentRole.GROWTH,
                "workflow": "create",
                "skill": "growth_leads",
                "specialist": "seo-specialist",
            },
            {
                "keywords": ["frontend", "ui", "ux", "componente", "layout"],
                "role": AgentRole.DEVELOPER,
                "workflow": "create",
                "skill": "web_fullstack",
                "specialist": "frontend-specialist",
            },
            {
                "keywords": ["api", "backend", "endpoint", "database", "cli", "script"],
                "role": AgentRole.DEVELOPER,
                "workflow": "create",
                "skill": "automation_cli",
                "specialist": "backend-specialist",
            },
            {
                "keywords": ["planejar", "roadmap", "sprint", "estrategia", "scope"],
                "role": AgentRole.MANAGER,
                "workflow": "plan",
                "skill": "automation_cli",
                "specialist": "project-planner",
            },
        ]

    def route(self, intent: str) -> dict:
        text = intent.lower()
        best = {
            "role": AgentRole.DEVELOPER,
            "workflow": "create",
            "skill": "automation_cli",
            "specialist": "backend-specialist",
            "score": 0,
        }

        for route in self.routes:
            score = sum(1 for kw in route["keywords"] if kw in text)
            if score > best["score"]:
                best = {
                    "role": route["role"],
                    "workflow": route["workflow"],
                    "skill": route["skill"],
                    "specialist": route.get("specialist", "backend-specialist"),
                    "score": score,
                }

        return best
