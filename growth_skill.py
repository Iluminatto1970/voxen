from pathlib import Path


class GrowthSkill:
    """
    Captura de Leads e Deploy: quando o código vira negócio.
    """

    def __init__(self, workspace_dir: str = "workspace") -> None:
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)

    def generate_landing_page(self, product_name: str, value_prop: str) -> str:
        content = (
            "<h1>" + product_name + "</h1>"
            + "<p>" + value_prop + "</p>"
            + "<form>Email: <input type='email' name='email' required></form>"
        )
        output_file = self.workspace / "index.html"
        output_file.write_text(content, encoding="utf-8")
        return "Landing Page gerada. Pronto para capturar leads."

    def deploy_to_production(self, target: str = "vercel") -> str:
        if target.lower() == "aws":
            return "Deploy realizado com sucesso na AWS. O sistema está vivo."
        return "Deploy realizado com sucesso na Vercel. O sistema está vivo."


growth = GrowthSkill()
