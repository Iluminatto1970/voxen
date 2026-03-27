import json
from datetime import datetime, timedelta
from pathlib import Path


class BrainstormAgent:
    """
    O Arquiteto de Conceitos: transforma intencao em blueprint tecnico.
    """

    def __init__(
        self,
        project_name: str,
        workspace_dir: str = "workspace",
        force_mode: str = "",
    ) -> None:
        self.project_name = project_name
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.force_mode = force_mode.upper() if force_mode else ""
        self.blueprint = {
            "project": project_name,
            "created_at": datetime.now().isoformat(),
            "core_problem": "",
            "target_user": "",
            "monetization": "",
            "stack_decision": "",
            "risk_factors": [],
            "mode": "BRUTAL",
            "timebox_minutes": 10,
            "deadline": (datetime.now() + timedelta(minutes=10)).isoformat(),
            "execution_plan": {
                "brainstorm_minutes": 10,
                "prototype_minutes": 60,
                "qa_minutes": 20,
                "feedback_loop": "imediato",
            },
        }

    def _extract_stack_and_monetization(self, user_intent: str) -> tuple[str, str]:
        text = user_intent.lower()
        if any(word in text for word in ["venda", "checkout", "assinatura", "saas", "stripe"]):
            return "Next.js + Stripe + Supabase", "Recorrencia/SaaS"
        if any(word in text for word in ["ferramenta", "cli", "terminal", "devtool"]):
            return "Python + Typer + Rich (ou Rust)", "Open Source + Licenciamento"
        if any(word in text for word in ["atendimento", "suporte", "whatsapp", "chatbot", "rag"]):
            return "Python + FastAPI + VectorDB + Canal de Mensagens", "Servico recorrente B2B"
        return "Python + FastAPI + Postgres", "Validacao de mercado/MVP"

    def _extract_risks(self, user_intent: str) -> list[str]:
        text = user_intent.lower()
        risks = [
            "Escopo excessivo sem milestone de deploy.",
            "Falta de testes automatizados no fluxo critico.",
        ]
        if "pagamento" in text or "stripe" in text:
            risks.append("Falha em fluxo de cobranca e webhooks de pagamento.")
        if "api" in text or "integr" in text:
            risks.append("Rate limit e indisponibilidade de APIs externas.")
        if "dados" in text or "lgpd" in text:
            risks.append("Risco de conformidade e vazamento de dados sensiveis.")
        return risks

    def _guided_questions(self) -> tuple[str, str, str]:
        problem = input("[GUIADO] Qual problema central vamos resolver? ").strip()
        user = input("[GUIADO] Quem e o usuario pagante/principal? ").strip()
        revenue = input("[GUIADO] Como isso monetiza no primeiro deploy? ").strip()
        return problem, user, revenue

    def define_mission(self, user_intent: str, mode: str = "BRUTAL") -> dict:
        mode_normalized = self.force_mode or mode.strip().upper()
        self.blueprint["mode"] = mode_normalized

        print(f"[BRAINSTORM] Analisando intencao: '{user_intent}'")
        stack, monetization = self._extract_stack_and_monetization(user_intent)

        self.blueprint["core_problem"] = user_intent
        self.blueprint["stack_decision"] = stack
        self.blueprint["monetization"] = monetization
        self.blueprint["risk_factors"] = self._extract_risks(user_intent)

        if mode_normalized == "GUIADO":
            problem, target_user, revenue = self._guided_questions()
            if problem:
                self.blueprint["core_problem"] = problem
            if target_user:
                self.blueprint["target_user"] = target_user
            if revenue:
                self.blueprint["monetization"] = revenue

        if mode_normalized == "AUDITOR":
            repo_status = input("[AUDITOR] Qual o principal sintoma do sistema atual? ").strip()
            if repo_status:
                self.blueprint["risk_factors"].insert(0, f"Problema atual reportado: {repo_status}")

        self.save_blueprint()
        return self.blueprint

    def save_blueprint(self) -> Path:
        output_file = self.workspace / "BLUEPRINT.json"
        output_file.write_text(
            json.dumps(self.blueprint, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[SQUAD] Blueprint de engenharia gerado em {output_file}.")
        return output_file
