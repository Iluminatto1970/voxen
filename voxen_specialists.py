from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


class VoxenSpecialists:
    """
    Especialistas para analise paralela de uma intencao.
    """

    def __init__(self, source_roots: list[str] | None = None) -> None:
        root = Path(__file__).resolve().parent
        self.source_roots = [
            Path(item)
            for item in (
                source_roots
                or [
                    str(Path.cwd() / ".agent" / "agents"),
                    str(root / "_references" / "antigravity-kit" / ".agent" / "agents"),
                ]
            )
        ]
        self.specialists = self._load_specialists()

    def _default_specialists(self) -> list[dict]:
        return [
            {
                "id": "api-designer",
                "focus": ["api", "rest", "graphql", "openapi", "schema", "endpoint"],
                "workflow": "create",
                "skills": ["api-patterns", "architecture"],
                "description": "Especialista em design de APIs, contratos e padroes de integracao.",
            },
            {
                "id": "frontend-specialist",
                "focus": ["frontend", "ui", "ux", "componente", "layout", "react", "next"],
                "workflow": "create",
                "skills": ["frontend-design", "nextjs-react-expert"],
                "description": "Especialista em interfaces, experiencia do usuario e implementacao frontend.",
            },
            {
                "id": "backend-specialist",
                "focus": ["backend", "api", "endpoint", "database", "auth", "server"],
                "workflow": "create",
                "skills": ["api-patterns", "database-design"],
                "description": "Especialista em APIs, modelagem de dados e arquitetura backend.",
            },
            {
                "id": "database-architect",
                "focus": ["database", "schema", "migration", "query", "index", "postgres"],
                "workflow": "create",
                "skills": ["database-design", "architecture"],
                "description": "Especialista em banco de dados, schema e performance de consultas.",
            },
            {
                "id": "qa-automation-engineer",
                "focus": ["teste", "coverage", "qa", "bug", "regressao"],
                "workflow": "test",
                "skills": ["testing-patterns", "webapp-testing"],
                "description": "Especialista em qualidade, testes automatizados e regressao.",
            },
            {
                "id": "test-engineer",
                "focus": ["teste", "unit", "integration", "e2e", "coverage", "tdd"],
                "workflow": "test",
                "skills": ["testing-patterns", "tdd-workflow"],
                "description": "Especialista em engenharia de testes, cobertura e estrategia de validacao.",
            },
            {
                "id": "debugger",
                "focus": ["debug", "erro", "bug", "falha", "stacktrace", "root-cause"],
                "workflow": "debug",
                "skills": ["systematic-debugging", "lint-and-validate"],
                "description": "Especialista em diagnostico sistematico e correcao de falhas.",
            },
            {
                "id": "security-auditor",
                "focus": ["security", "vulnerabilidade", "token", "secret", "auth"],
                "workflow": "debug",
                "skills": ["vulnerability-scanner", "red-team-tactics"],
                "description": "Especialista em seguranca, hardening e analise de vulnerabilidades.",
            },
            {
                "id": "penetration-tester",
                "focus": ["pentest", "penetration", "security", "exploit", "owasp"],
                "workflow": "debug",
                "skills": ["red-team-tactics", "vulnerability-scanner"],
                "description": "Especialista em testes ofensivos e identificacao de vetores de ataque.",
            },
            {
                "id": "devops-engineer",
                "focus": ["deploy", "infra", "docker", "pipeline", "release"],
                "workflow": "deploy",
                "skills": ["deployment-procedures", "server-management"],
                "description": "Especialista em deploy, infraestrutura e pipelines de entrega.",
            },
            {
                "id": "performance-optimizer",
                "focus": ["performance", "profiling", "latency", "throughput", "optimize"],
                "workflow": "enhance",
                "skills": ["performance-profiling", "lint-and-validate"],
                "description": "Especialista em diagnostico de gargalos e otimizacao de performance.",
            },
            {
                "id": "project-planner",
                "focus": ["plan", "roadmap", "scope", "milestone", "sprint", "timeline"],
                "workflow": "plan",
                "skills": ["plan-writing", "architecture"],
                "description": "Especialista em planejamento, decomposicao de tarefas e milestones.",
            },
            {
                "id": "product-manager",
                "focus": ["produto", "prioridade", "mvp", "valor", "roadmap", "metricas"],
                "workflow": "plan",
                "skills": ["behavioral-modes", "plan-writing"],
                "description": "Especialista em estrategia de produto e priorizacao orientada a valor.",
            },
            {
                "id": "product-owner",
                "focus": ["backlog", "historia", "aceite", "negocio", "stakeholder"],
                "workflow": "plan",
                "skills": ["plan-writing", "documentation-templates"],
                "description": "Especialista em backlog, requisitos e criterios de aceite.",
            },
            {
                "id": "orchestrator",
                "focus": ["orchestrate", "multi-agent", "coordination", "squad", "parallel"],
                "workflow": "orchestrate",
                "skills": ["parallel-agents", "architecture"],
                "description": "Especialista em coordenacao de multiplos agentes e fluxos complexos.",
            },
            {
                "id": "explorer-agent",
                "focus": ["explore", "map", "discover", "codebase", "dependencies"],
                "workflow": "plan",
                "skills": ["clean-code", "documentation-templates"],
                "description": "Especialista em exploracao da base de codigo e descoberta de contexto.",
            },
            {
                "id": "code-archaeologist",
                "focus": ["legacy", "historic", "arquiv", "refactor", "technical-debt"],
                "workflow": "enhance",
                "skills": ["clean-code", "architecture"],
                "description": "Especialista em codigo legado, arqueologia de decisoes e refatoracao guiada.",
            },
            {
                "id": "documentation-writer",
                "focus": ["docs", "readme", "documentacao", "guia", "manual"],
                "workflow": "enhance",
                "skills": ["documentation-templates", "clean-code"],
                "description": "Especialista em documentacao tecnica, guias e padroes de escrita.",
            },
            {
                "id": "seo-specialist",
                "focus": ["seo", "meta", "indexacao", "ranking", "search", "analytics"],
                "workflow": "create",
                "skills": ["seo-fundamentals", "web-design-guidelines"],
                "description": "Especialista em SEO tecnico, conteudo indexavel e performance de busca.",
            },
            {
                "id": "mobile-developer",
                "focus": ["mobile", "react-native", "flutter", "ios", "android", "expo"],
                "workflow": "create",
                "skills": ["mobile-design", "clean-code"],
                "description": "Especialista em desenvolvimento mobile e experiencia em dispositivos moveis.",
            },
            {
                "id": "game-developer",
                "focus": ["game", "unity", "godot", "unreal", "phaser", "gameplay"],
                "workflow": "create",
                "skills": ["game-development", "performance-profiling"],
                "description": "Especialista em desenvolvimento de jogos e sistemas interativos.",
            },
        ]

    def _infer_workflow(self, specialist_id: str, description: str) -> str:
        text = f"{specialist_id} {description}".lower()
        if any(token in text for token in ["deploy", "devops", "infra", "release"]):
            return "deploy"
        if any(token in text for token in ["test", "qa", "debug", "security", "penetration"]):
            return "test"
        if any(token in text for token in ["plan", "planner", "manager", "orchestrator"]):
            return "plan"
        return "create"

    def _infer_skills(self, specialist_id: str, skills_meta: list[str]) -> list[str]:
        if skills_meta:
            return skills_meta
        sid = specialist_id.lower()
        if "frontend" in sid:
            return ["frontend-design", "nextjs-react-expert"]
        if "backend" in sid or "api" in sid:
            return ["api-patterns", "database-design"]
        if "security" in sid or "penetration" in sid:
            return ["vulnerability-scanner", "red-team-tactics"]
        if "test" in sid or "qa" in sid or "debug" in sid:
            return ["testing-patterns", "systematic-debugging"]
        if "devops" in sid:
            return ["deployment-procedures", "server-management"]
        if "seo" in sid:
            return ["seo-fundamentals", "documentation-templates"]
        return ["clean-code"]

    def _infer_focus(self, specialist_id: str, description: str) -> list[str]:
        tokens = re.findall(r"[a-z0-9_-]+", f"{specialist_id} {description}".lower())
        base = []
        for token in tokens:
            if token in {"specialist", "engineer", "agent", "developer", "and", "with", "for", "the"}:
                continue
            if len(token) < 3:
                continue
            if token not in base:
                base.append(token)
        return base[:20]

    def _parse_frontmatter(self, content: str) -> dict:
        if not content.startswith("---\n"):
            return {}
        end = content.find("\n---\n", 4)
        if end == -1:
            return {}
        block = content[4:end]
        data: dict[str, str] = {}
        for line in block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip().lower()] = value.strip()
        return data

    def _agent_files(self) -> list[Path]:
        files = []
        seen = set()
        for root in self.source_roots:
            if not root.exists():
                continue
            for file in sorted(root.glob("*.md")):
                if file.name in seen:
                    continue
                seen.add(file.name)
                files.append(file)
        return files

    def _load_specialists(self) -> list[dict]:
        discovered = []
        for file in self._agent_files():
            try:
                content = file.read_text(encoding="utf-8")
            except Exception:
                continue
            meta = self._parse_frontmatter(content)
            specialist_id = meta.get("name") or file.stem
            description = meta.get("description", "Especialista tecnico.")
            skills_meta = [item.strip() for item in meta.get("skills", "").split(",") if item.strip()]
            discovered.append(
                {
                    "id": specialist_id,
                    "focus": self._infer_focus(specialist_id, description),
                    "workflow": self._infer_workflow(specialist_id, description),
                    "skills": self._infer_skills(specialist_id, skills_meta),
                    "description": description,
                }
            )

        if discovered:
            discovered.sort(key=lambda item: item["id"])
            return discovered
        return self._default_specialists()

    def _score_specialist(self, specialist: dict, intent: str) -> dict:
        text = intent.lower()
        score = sum(1 for token in specialist["focus"] if token in text)
        return {
            "id": specialist["id"],
            "workflow": specialist["workflow"],
            "skills": specialist["skills"],
            "score": score,
        }

    def parallel_scout(self, intent: str, top_n: int = 3) -> list[dict]:
        with ThreadPoolExecutor(max_workers=min(5, len(self.specialists))) as executor:
            futures = [executor.submit(self._score_specialist, specialist, intent) for specialist in self.specialists]
            results = [future.result() for future in futures]

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_n]

    def list_specialists(self) -> list[dict]:
        return [
            {
                "id": specialist["id"],
                "workflow": specialist["workflow"],
                "skills": specialist["skills"],
                "focus": specialist.get("focus", []),
                "description": specialist.get("description", ""),
            }
            for specialist in self.specialists
        ]
