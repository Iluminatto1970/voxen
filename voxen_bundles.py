from skills_catalog import SkillsCatalog


class VoxenBundles:
    """
    Bundles de skills por modo de operacao.
    """

    def __init__(self, catalog: SkillsCatalog) -> None:
        self.catalog = catalog
        self.bundles = {
            "micro_saas": [
                "react-nextjs-development",
                "stripe-integration",
                "frontend-design",
                "api-design-principles",
                "seo-content-writer",
            ],
            "dev_tool_cli": [
                "python-patterns",
                "rust-pro",
                "lint-and-validate",
                "systematic-debugging",
                "vulnerability-scanner",
            ],
            "support_agent": [
                "api-patterns",
                "workflow-automation",
                "knowledge-base-constructor",
                "rag-agent-implementation",
                "integration-testing",
            ],
        }

    def list_bundle(self, mode_name: str) -> list[str]:
        return list(self.bundles.get(mode_name, []))

    def install_bundle(self, mode_name: str, top_n: int = 5) -> dict:
        wanted = self.list_bundle(mode_name)[:top_n]
        installed = []
        missing = []

        for skill in wanted:
            ok, _ = self.catalog.install(skill)
            if ok:
                installed.append(skill)
            else:
                missing.append(skill)

        return {
            "mode": mode_name,
            "installed": installed,
            "missing": missing,
            "requested": wanted,
        }
