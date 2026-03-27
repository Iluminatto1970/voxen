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
            "constraints": [],
            "mode": "BRUTAL",
            "timebox_minutes": 10,
            "deadline": (datetime.now() + timedelta(minutes=10)).isoformat(),
            "execution_plan": {
                "brainstorm_minutes": 10,
                "prototype_minutes": 60,
                "qa_minutes": 20,
                "feedback_loop": "imediato",
            },
            "options": [],
            "recommendation": {},
            "brainstorm_report": "",
        }

    def _infer_domain(self, user_intent: str) -> str:
        text = user_intent.lower()
        if any(word in text for word in ["venda", "checkout", "assinatura", "saas", "stripe"]):
            return "saas"
        if any(word in text for word in ["ferramenta", "cli", "terminal", "devtool"]):
            return "cli"
        if any(word in text for word in ["atendimento", "suporte", "whatsapp", "chatbot", "rag"]):
            return "support"
        return "generic"

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

    def _extract_constraints(self, user_intent: str) -> list[str]:
        text = user_intent.lower()
        constraints = []
        if any(word in text for word in ["rapido", "urgente", "hoje", "amanha", "prazo"]):
            constraints.append("Prazo curto para entregar valor inicial.")
        if any(word in text for word in ["barato", "baixo custo", "economico", "mvp"]):
            constraints.append("Controle de custo e escopo no primeiro ciclo.")
        if any(word in text for word in ["escala", "mil", "alto trafego", "performance"]):
            constraints.append("Preocupacao com escalabilidade e performance.")
        if any(word in text for word in ["lgpd", "compliance", "seguranca", "dados"]):
            constraints.append("Atencao com seguranca e conformidade de dados.")
        return constraints

    def _build_options(self, domain: str) -> list[dict]:
        options_by_domain = {
            "saas": [
                {
                    "name": "MVP monolitico com foco em conversao",
                    "description": "Monolito web com onboarding, checkout e telemetria basica para validar receita.",
                    "pros": [
                        "Entrega rapida de ponta a ponta",
                        "Menor custo inicial de operacao",
                        "Facil de iterar por feedback comercial",
                    ],
                    "cons": [
                        "Escalabilidade limitada no medio prazo",
                        "Divida tecnica se crescer sem modularizar",
                    ],
                    "effort": "Low",
                },
                {
                    "name": "Arquitetura modular por dominios",
                    "description": "Separar autenticacao, billing e produto em modulos independentes desde o inicio.",
                    "pros": [
                        "Melhor manutencao e crescimento",
                        "Evolucao de times e ownership mais clara",
                    ],
                    "cons": [
                        "Maior complexidade inicial",
                        "Tempo de setup maior antes de validar receita",
                    ],
                    "effort": "Medium",
                },
                {
                    "name": "Go-to-market com servicos gerenciados",
                    "description": "Maximizar uso de terceiros para auth, billing e analytics com camada fina de produto.",
                    "pros": [
                        "Time-to-market muito rapido",
                        "Menos sobrecarga operacional",
                    ],
                    "cons": [
                        "Dependencia de vendors externos",
                        "Margem pode cair com crescimento",
                    ],
                    "effort": "Low",
                },
            ],
            "cli": [
                {
                    "name": "CLI enxuta com comandos essenciais",
                    "description": "Focar no fluxo principal com UX terminal clara e tratamento de erro robusto.",
                    "pros": [
                        "Entrega rapida para usuarios tecnicos",
                        "Facil validar adocao com early adopters",
                    ],
                    "cons": [
                        "Cobertura funcional inicial menor",
                    ],
                    "effort": "Low",
                },
                {
                    "name": "CLI pluginavel",
                    "description": "Core minimo com sistema de plugins para extensao por modulo.",
                    "pros": [
                        "Alta flexibilidade de evolucao",
                        "Permite ecossistema comunitario",
                    ],
                    "cons": [
                        "Exige desenho de API interna estavel",
                        "Debug e suporte mais complexos",
                    ],
                    "effort": "High",
                },
                {
                    "name": "CLI + daemon local",
                    "description": "Comandos leves no terminal com servico local para tarefas pesadas e cache.",
                    "pros": [
                        "Performance superior em operacoes repetidas",
                        "Melhor base para recursos avancados",
                    ],
                    "cons": [
                        "Complexidade de runtime e observabilidade",
                        "Maior custo de manutencao",
                    ],
                    "effort": "Medium",
                },
            ],
            "support": [
                {
                    "name": "RAG baseline com FAQ prioritaria",
                    "description": "Pipeline simples de busca semantica para reduzir tickets repetitivos rapidamente.",
                    "pros": [
                        "Impacto rapido em tempo de resposta",
                        "Implementacao controlada para MVP",
                    ],
                    "cons": [
                        "Cobertura limitada a base existente",
                    ],
                    "effort": "Low",
                },
                {
                    "name": "Orquestracao multiagente por intent",
                    "description": "Roteamento de intents por agentes especialistas com politicas por canal.",
                    "pros": [
                        "Maior qualidade por especializacao",
                        "Escala melhor para casos complexos",
                    ],
                    "cons": [
                        "Mais pontos de falha e monitoramento",
                        "Custo de inferencia potencialmente maior",
                    ],
                    "effort": "High",
                },
                {
                    "name": "Assistente hibrido com handoff humano",
                    "description": "IA resolve primeiro nivel e transfere com contexto para operadores em casos sensiveis.",
                    "pros": [
                        "Balanceia automacao e qualidade",
                        "Reduz risco de respostas inadequadas",
                    ],
                    "cons": [
                        "Depende de operacao humana estruturada",
                        "Requer trilha de auditoria forte",
                    ],
                    "effort": "Medium",
                },
            ],
            "generic": [
                {
                    "name": "MVP funcional de escopo minimo",
                    "description": "Recorte pequeno com medicao de valor desde o primeiro deploy.",
                    "pros": [
                        "Aprendizado rapido com usuarios reais",
                        "Menor risco de investir no produto errado",
                    ],
                    "cons": [
                        "Pode parecer incompleto para alguns usuarios",
                    ],
                    "effort": "Low",
                },
                {
                    "name": "Core robusto antes de abrir funcionalidades",
                    "description": "Priorizar fundacao tecnica e padroes para reduzir retrabalho depois.",
                    "pros": [
                        "Base mais sustentavel no medio prazo",
                        "Menos regressao em expansao futura",
                    ],
                    "cons": [
                        "Adia validacao de mercado",
                        "Retorno mais lento no inicio",
                    ],
                    "effort": "Medium",
                },
                {
                    "name": "Piloto assistido com operacao manual",
                    "description": "Automacao parcial com processos manuais para validar demanda antes de escalar arquitetura.",
                    "pros": [
                        "Baixo custo de entrada",
                        "Flexibilidade para ajustar proposta de valor",
                    ],
                    "cons": [
                        "Escala limitada enquanto manual",
                        "Dependencia de processo operacional",
                    ],
                    "effort": "Low",
                },
            ],
        }
        return options_by_domain.get(domain, options_by_domain["generic"])

    def _recommend_option(self, options: list[dict], constraints: list[str]) -> tuple[int, str]:
        if not options:
            return 0, "Sem opcoes disponiveis."

        prefer_speed = any("Prazo curto" in item for item in constraints)
        prefer_cost = any("Controle de custo" in item for item in constraints)

        scores = []
        for index, option in enumerate(options, start=1):
            effort = option.get("effort", "Medium")
            score = 0
            if effort == "Low":
                score += 3
            elif effort == "Medium":
                score += 2
            else:
                score += 1

            if prefer_speed and effort == "Low":
                score += 2
            if prefer_cost and effort in {"Low", "Medium"}:
                score += 1
            scores.append((score, index, option))

        scores.sort(key=lambda item: (-item[0], item[1]))
        _, winner_index, winner = scores[0]
        reason = (
            f"equilibra velocidade, risco e viabilidade para o contexto atual "
            f"com esforco {winner.get('effort', 'Medium')}"
        )
        return winner_index, reason

    def _format_brainstorm_report(self) -> str:
        topic = self.blueprint.get("core_problem", "Tema")
        context_parts = [
            f"Problema: {topic}",
            f"Usuario foco: {self.blueprint.get('target_user') or 'nao definido'}",
            f"Monetizacao inicial: {self.blueprint.get('monetization')}",
            f"Stack sugerida: {self.blueprint.get('stack_decision')}",
        ]
        constraints = self.blueprint.get("constraints", [])
        if constraints:
            context_parts.append(f"Restricoes: {'; '.join(constraints)}")

        lines = [
            f"## 🧠 Brainstorm: {topic}",
            "",
            "### Context",
            " ".join(context_parts),
            "",
            "---",
            "",
        ]

        for idx, option in enumerate(self.blueprint.get("options", []), start=1):
            label = chr(ord("A") + idx - 1)
            lines.extend(
                [
                    f"### Option {label}: {option['name']}",
                    option["description"],
                    "",
                    "✅ **Pros:**",
                ]
            )
            for item in option.get("pros", []):
                lines.append(f"- {item}")
            lines.append("")
            lines.append("❌ **Cons:**")
            for item in option.get("cons", []):
                lines.append(f"- {item}")
            lines.extend(["", f"📊 **Effort:** {option.get('effort', 'Medium')}", "", "---", ""])

        recommendation = self.blueprint.get("recommendation", {})
        recommended_name = recommendation.get("name", "Option A")
        recommended_reason = recommendation.get("reason", "melhor alinhamento com objetivo")
        lines.extend(
            [
                "## 💡 Recommendation",
                "",
                f"**{recommended_name}** because {recommended_reason}.",
                "",
                "What direction would you like to explore?",
            ]
        )
        return "\n".join(lines)

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
        domain = self._infer_domain(user_intent)

        self.blueprint["core_problem"] = user_intent
        self.blueprint["stack_decision"] = stack
        self.blueprint["monetization"] = monetization
        self.blueprint["risk_factors"] = self._extract_risks(user_intent)
        self.blueprint["constraints"] = self._extract_constraints(user_intent)

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

        options = self._build_options(domain)
        recommended_index, recommended_reason = self._recommend_option(options, self.blueprint["constraints"])
        self.blueprint["options"] = options
        recommended_option = options[recommended_index - 1] if options else {"name": "Opcao A"}
        self.blueprint["recommendation"] = {
            "option": recommended_index,
            "name": f"Option {chr(ord('A') + recommended_index - 1)}",
            "reason": recommended_reason,
        }
        self.blueprint["brainstorm_report"] = self._format_brainstorm_report()

        self.save_blueprint()
        self.save_brainstorm_report()
        return self.blueprint

    def save_blueprint(self) -> Path:
        output_file = self.workspace / "BLUEPRINT.json"
        output_file.write_text(
            json.dumps(self.blueprint, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[SQUAD] Blueprint de engenharia gerado em {output_file}.")
        return output_file

    def save_brainstorm_report(self) -> Path:
        output_file = self.workspace / "BRAINSTORM.md"
        output_file.write_text(self.blueprint.get("brainstorm_report", ""), encoding="utf-8")
        print(f"[SQUAD] Relatorio de brainstorm gerado em {output_file}.")
        return output_file
