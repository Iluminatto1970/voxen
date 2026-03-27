import re

from voxen_manager import AgentRole


class VoxenIntentRouter:
    """
    Roteador automatico de intencao -> agente + skill + workflow.
    """

    def __init__(self, specialists: list[dict] | None = None) -> None:
        self.specialist_overrides: dict[str, dict] = {}
        if specialists:
            self.register_specialists(specialists)
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

    def _role_from_workflow(self, workflow: str) -> AgentRole:
        wf = workflow.lower().strip()
        if wf in {"plan", "orchestrate"}:
            return AgentRole.MANAGER
        if wf in {"test", "debug"}:
            return AgentRole.QA
        if wf == "deploy":
            return AgentRole.GROWTH
        return AgentRole.DEVELOPER

    def _skill_from_specialist(self, specialist: dict) -> str:
        skills = specialist.get("skills") or []
        if skills:
            first = str(skills[0]).lower()
            if any(token in first for token in ["seo", "deployment", "server", "growth"]):
                return "growth_leads"
            if any(token in first for token in ["front", "react", "next", "tailwind"]):
                return "web_fullstack"
        return "automation_cli"

    def register_specialists(self, specialists: list[dict]) -> None:
        self.specialist_overrides = {}
        for specialist in specialists:
            specialist_id = str(specialist.get("id", "")).strip().lower()
            if not specialist_id:
                continue
            workflow = str(specialist.get("workflow", "create") or "create").strip().lower()
            self.specialist_overrides[specialist_id] = {
                "role": self._role_from_workflow(workflow),
                "workflow": workflow,
                "skill": self._skill_from_specialist(specialist),
                "focus": specialist.get("focus", []),
            }

    def route(self, intent: str) -> dict:
        text = intent.lower()
        forced_specialists = re.findall(r"@([a-z0-9_-]+)", text)
        for specialist_id in forced_specialists:
            if specialist_id in self.specialist_overrides:
                forced = self.specialist_overrides[specialist_id]
                return {
                    "role": forced["role"],
                    "workflow": forced["workflow"],
                    "skill": forced["skill"],
                    "specialist": specialist_id,
                    "score": 999,
                    "forced": True,
                }

        best = {
            "role": AgentRole.DEVELOPER,
            "workflow": "create",
            "skill": "automation_cli",
            "specialist": "backend-specialist",
            "score": 0,
            "forced": False,
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
                    "forced": False,
                }

        for specialist_id, specialist in self.specialist_overrides.items():
            keywords = [token for token in specialist.get("focus", []) if isinstance(token, str)]
            if not keywords:
                continue
            score = sum(1 for token in keywords if token and token in text)
            if score > best["score"]:
                best = {
                    "role": specialist["role"],
                    "workflow": specialist["workflow"],
                    "skill": specialist["skill"],
                    "specialist": specialist_id,
                    "score": score,
                    "forced": False,
                }

        return best
