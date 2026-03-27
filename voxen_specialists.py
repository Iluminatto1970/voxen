from concurrent.futures import ThreadPoolExecutor


class VoxenSpecialists:
    """
    Especialistas para analise paralela de uma intencao.
    """

    def __init__(self) -> None:
        self.specialists = [
            {
                "id": "frontend-specialist",
                "focus": ["frontend", "ui", "ux", "componente", "layout", "react", "next"],
                "workflow": "create",
                "skills": ["frontend-design", "react-nextjs-development"],
            },
            {
                "id": "backend-specialist",
                "focus": ["backend", "api", "endpoint", "database", "auth", "server"],
                "workflow": "create",
                "skills": ["api-patterns", "database-design"],
            },
            {
                "id": "qa-automation-engineer",
                "focus": ["teste", "coverage", "qa", "bug", "regressao"],
                "workflow": "test",
                "skills": ["testing-patterns", "webapp-testing"],
            },
            {
                "id": "security-auditor",
                "focus": ["security", "vulnerabilidade", "token", "secret", "auth"],
                "workflow": "debug",
                "skills": ["vulnerability-scanner", "red-team-tactics"],
            },
            {
                "id": "devops-engineer",
                "focus": ["deploy", "infra", "docker", "pipeline", "release"],
                "workflow": "deploy",
                "skills": ["deployment-procedures", "server-management"],
            },
        ]

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
