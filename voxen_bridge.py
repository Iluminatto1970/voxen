from core_agent import OpenCodeExecutor
from growth_skill import GrowthSkill
from qa_skill import QASkill
from voxen_brainstorm import BrainstormAgent
from pathlib import Path
import re
from skills_catalog import SkillsCatalog
from skill_factory import SkillFactory
from voxen_evaluator import VoxenEvaluator
from voxen_policies import VoxenPolicyEngine
from voxen_context import VoxenContextEngine
from voxen_router import VoxenIntentRouter
from voxen_specialists import VoxenSpecialists
from voxen_manager import AgentRole, VoxenManager


class VoxenBridge:
    """
    Interface entre a IA OpenCode e o Squad local.
    Transforma intenção em execução bash com checkpoints explícitos do dev.
    """

    def __init__(
        self,
        workspace_dir: str = "workspace",
        state_file: str = "voxen_state.json",
        auto_install_skills: bool = True,
        auto_install_top_n: int = 3,
        interactive: bool = True,
        strict_pin_enforcement: bool = True,
    ) -> None:
        root = Path(__file__).resolve().parent
        self.workspace_dir = workspace_dir
        self.executor = OpenCodeExecutor(workspace_dir=workspace_dir)
        self.manager = VoxenManager(state_file=state_file)
        self.qa = QASkill(workspace_dir=workspace_dir)
        self.factory = SkillFactory()
        self.growth = GrowthSkill(workspace_dir=workspace_dir)
        self.context = VoxenContextEngine(workspace_dir=workspace_dir)
        self.specialists = VoxenSpecialists(
            source_roots=[
                str(Path.cwd() / ".agent" / "agents"),
                str(root / "_references" / "antigravity-kit" / ".agent" / "agents"),
            ]
        )
        self.router = VoxenIntentRouter(specialists=self.specialists.list_specialists())
        self.catalog = SkillsCatalog(
            source_root=str(root / "_references" / "antigravity-awesome-skills" / "skills"),
            source_roots=[
                str(Path.cwd() / ".agent" / "skills"),
                str(root / "_references" / "antigravity-kit" / ".agent" / "skills"),
                str(root / "_references" / "antigravity-awesome-skills" / "skills"),
            ],
            target_root="skills",
        )
        self.policies = VoxenPolicyEngine()
        self.evaluator = VoxenEvaluator(metrics_file=f"{workspace_dir}/_memory/evals.jsonl")
        self.auto_install_skills = auto_install_skills
        self.auto_install_top_n = auto_install_top_n
        self.interactive = interactive
        self.strict_pin_enforcement = strict_pin_enforcement

    def _ask(self, prompt: str, default: str = "") -> str:
        if not self.interactive:
            return default
        label = f"{prompt}"
        if default:
            label += f" [{default}]"
        label += ": "
        value = input(label).strip()
        return value if value else default

    def _ask_yes_no(self, prompt: str, default_yes: bool = True) -> bool:
        default = "s" if default_yes else "n"
        answer = self._ask(f"{prompt} (s/n)", default=default).lower()
        return answer in {"s", "sim", "y", "yes"}

    def _looks_like_shell_command(self, value: str) -> bool:
        text = value.strip()
        if not text:
            return False

        shell_tokens = {"./", "../", "/", "git ", "python ", "pytest", "npm ", "pnpm ", "yarn ", "make ", "docker ", "bash ", "sh "}
        if any(text.startswith(token) for token in shell_tokens):
            return True

        shell_operators = ["&&", "||", "|", ";", "$()", "`"]
        return any(operator in text for operator in shell_operators)

    def _request_approval(self, task_id: int, stage: str, summary: str, default_yes: bool = True) -> bool:
        approval = self.manager.create_approval(task_id=task_id, stage=stage, summary=summary)
        approved = True if not self.interactive else self._ask_yes_no(
            f"Aprovar etapa '{stage}'? {summary}",
            default_yes=default_yes,
        )
        self.manager.update_approval(approval["id"], "approved" if approved else "rejected")
        return approved

    def _extract_mission_context(self, instruction: str) -> str:
        marker = "Contexto da missao:"
        if marker in instruction:
            return instruction.split(marker, 1)[1].strip()
        return instruction.strip()

    def _build_textual_deliverable(self, agent_role: AgentRole, instruction: str) -> str:
        context = self._extract_mission_context(instruction) or "missao nao informada"
        if agent_role == AgentRole.MANAGER:
            return (
                f"# Plano de Produto\n\n"
                f"## Contexto\n- {context}\n\n"
                "## Objetivo\n"
                "- Definir um MVP validavel em ate 4 semanas.\n\n"
                "## Riscos Principais\n"
                "- Escopo amplo para o primeiro ciclo.\n"
                "- Dependencias externas sem SLA definido.\n"
                "- Falta de criterio claro de sucesso no lancamento.\n\n"
                "## Entregavel\n"
                "- Documento de escopo do MVP com prioridades e metricas de sucesso.\n"
            )
        if agent_role == AgentRole.DEVELOPER:
            return (
                f"# Plano Tecnico\n\n"
                f"## Contexto\n- {context}\n\n"
                "## Etapas\n"
                "1. Modelar entidades e regras de negocio centrais.\n"
                "2. Implementar API principal e autenticacao basica.\n"
                "3. Construir interface inicial com fluxo completo.\n"
                "4. Adicionar observabilidade minima e logs essenciais.\n"
                "5. Preparar ambiente de homologacao com dados de teste.\n\n"
                "## Criterio tecnico\n"
                "- Entrega incrementavel com rollback simples por modulo.\n"
            )
        return (
            f"# Estrategia de QA\n\n"
            f"## Contexto\n- {context}\n\n"
            "## Criterios de Aceite\n"
            "- Fluxo principal concluido sem erro em ambiente de homologacao.\n"
            "- Validacao de entradas obrigatorias e mensagens de erro claras.\n"
            "- Logs de falha disponiveis para diagnostico rapido.\n\n"
            "## Suite Minima\n"
            "- Testes unitarios para regras de negocio criticas.\n"
            "- Testes de integracao para API principal.\n"
            "- Smoke test de ponta a ponta do fluxo central.\n"
        )

    def _persist_textual_deliverable(self, task_id: int, agent_role: AgentRole, instruction: str) -> str:
        deliverables_dir = Path(self.workspace_dir) / "_deliverables"
        deliverables_dir.mkdir(parents=True, exist_ok=True)
        filename = f"task_{task_id}_{agent_role.value.lower()}.md"
        target = deliverables_dir / filename
        content = self._build_textual_deliverable(agent_role, instruction)
        target.write_text(content, encoding="utf-8")
        return str(target)

    def _run_brainstorm_deliverable(self, instruction: str) -> tuple[str, str]:
        context = self._extract_mission_context(instruction)
        project_name = f"{self._mode_name()}_project"
        agent = BrainstormAgent(project_name=project_name, workspace_dir=self.workspace_dir)
        agent.define_mission(user_intent=context, mode="BRUTAL")
        report_path = str(Path(self.workspace_dir) / "BRAINSTORM.md")
        return report_path, f"Brainstorm estruturado gerado em: {report_path}"

    def _extract_external_workflow_name(self, instruction: str) -> str:
        match = re.search(r"workflow externo '([^']+)'", instruction, flags=re.IGNORECASE)
        return (match.group(1).strip().lower() if match else "")

    def _slugify(self, text: str, max_len: int = 30) -> str:
        normalized = re.sub(r"[^a-z0-9\s-]", "", text.lower())
        words = [item for item in re.split(r"[\s_-]+", normalized) if item]
        if not words:
            return "plano"
        slug = "-".join(words[:3])
        if len(slug) > max_len:
            slug = slug[:max_len].rstrip("-")
        return slug or "plano"

    def _append_or_create(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.write_text(path.read_text(encoding="utf-8") + "\n\n" + content, encoding="utf-8")
        else:
            path.write_text(content, encoding="utf-8")

    def _run_external_workflow_deliverable(
        self,
        workflow_name: str,
        instruction: str,
        agent_role: AgentRole,
        task_id: int,
    ) -> tuple[str, str]:
        context = self._extract_mission_context(instruction) or "missao nao informada"

        if workflow_name == "brainstorm":
            return self._run_brainstorm_deliverable(instruction)

        if workflow_name == "plan":
            slug = self._slugify(context)
            plan_file = Path(self.workspace_dir) / "docs" / f"PLAN-{slug}.md"
            if agent_role == AgentRole.MANAGER:
                content = (
                    f"# PLAN {slug}\n\n"
                    f"## Overview\n- Request: {context}\n\n"
                    "## Success Criteria\n"
                    "- MVP definido com escopo e metricas objetivas.\n"
                    "- Entregas faseadas com risco controlado.\n"
                )
                plan_file.parent.mkdir(parents=True, exist_ok=True)
                plan_file.write_text(content, encoding="utf-8")
            elif agent_role == AgentRole.DEVELOPER:
                content = (
                    "## Task Breakdown\n"
                    "1. Fundacao de dados e autenticacao.\n"
                    "2. API principal e fluxos core.\n"
                    "3. Interface inicial e observabilidade minima.\n"
                )
                self._append_or_create(plan_file, content)
            else:
                content = (
                    "## Verification Checklist\n"
                    "- [ ] Fluxo principal validado em homologacao.\n"
                    "- [ ] Casos de erro e limites cobertos.\n"
                    "- [ ] Criticos sem regressao.\n"
                )
                self._append_or_create(plan_file, content)
            path = str(plan_file)
            return path, f"Workflow plan aplicado. Entregavel salvo em: {path}"

        report_dir = Path(self.workspace_dir) / "_deliverables" / "workflows"
        report_file = report_dir / f"{workflow_name}-task-{task_id}-{agent_role.value.lower()}.md"
        role_label = {
            AgentRole.MANAGER: "Manager",
            AgentRole.DEVELOPER: "Developer",
            AgentRole.QA: "QA",
            AgentRole.GROWTH: "Growth",
        }.get(agent_role, agent_role.value)
        content = (
            f"# Workflow {workflow_name}\n\n"
            f"- Role: {role_label}\n"
            f"- Contexto: {context}\n\n"
            "## Resultado\n"
            "- Compatibilidade antigravity aplicada para este workflow.\n"
            "- Proximo passo pronto para execucao incremental.\n"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(content, encoding="utf-8")
        path = str(report_file)
        return path, f"Workflow {workflow_name} aplicado. Entregavel salvo em: {path}"

    def route_intent(self, intent: str) -> dict:
        return self.router.route(intent)

    def _mode_name(self) -> str:
        mode = Path(self.workspace_dir).name
        if mode in {"micro_saas", "dev_tool_cli", "support_agent", "mvp_generic"}:
            return mode
        return "mvp_generic"

    def _auto_install_skills(self, intent: str, route: dict) -> list[str]:
        if not self.auto_install_skills:
            return []

        mode_name = self._mode_name()
        recommendations = self.catalog.recommend(mode_name=mode_name, intent=intent, limit=8)
        installed = []
        for skill in recommendations[: self.auto_install_top_n]:
            ok, _ = self.catalog.install(skill)
            if ok:
                installed.append(skill)

        if installed:
            labels = self.catalog.format_skill_labels(installed)
            print(f"[SKILLS] auto-instaladas: {', '.join(labels)}")
        return installed

    def _auto_remediate_skills(self) -> dict:
        report = self.catalog.validate_installed()
        if report.get("ok", False):
            return {"status": "ok", "healed": []}
        healed = self.catalog.heal_skills()
        healed_labels = self.catalog.format_skill_labels(healed.get("healed", []))
        if healed_labels:
            print(f"[SKILLS] auto-remediacao aplicada: {', '.join(healed_labels)}")
        return healed

    def _enforce_pins(self) -> tuple[bool, str]:
        report = self.catalog.enforce_pins()
        if report.get("ok", False):
            return True, "Pins de skills estao consistentes."

        if not self.strict_pin_enforcement:
            return True, "Pins inconsistentes, mas enforcement estrito desativado."

        sync = self.catalog.sync_pins()
        report_after = self.catalog.enforce_pins()
        if report_after.get("ok", False):
            repaired = ", ".join(sync.get("repaired", [])) or "nenhuma"
            return True, f"Pins ajustados automaticamente ({repaired})."

        issues = "; ".join(report_after.get("issues", []))
        return False, f"Falha na consistencia de pins: {issues}"

    def context_snapshot(self) -> dict:
        return self.context.analyze()

    def sync_squad_intent(self, agent_role: AgentRole, ai_instruction: str) -> dict:
        started = self.evaluator.timer()
        print(f"[{agent_role.value}] Intenção recebida: {ai_instruction}")

        pins_ok, pins_msg = self._enforce_pins()
        print(f"[PIN-ENFORCEMENT] {pins_msg}")
        if not pins_ok:
            self.evaluator.record(
                kind="task_execution",
                status="blocked",
                payload={"reason": pins_msg, "role": agent_role.value},
                started_at=started,
            )
            return {
                "status": "blocked",
                "msg": pins_msg,
            }

        mvi = self.context.mvi_context_for(ai_instruction)
        route = self.router.route(ai_instruction)
        self._auto_install_skills(ai_instruction, route)
        self._auto_remediate_skills()
        if route.get("score", 0) > 0:
            print(
                f"[AUTO-ROUTER] sugestao role={route['role'].value} "
                f"workflow={route['workflow']} skill={route['skill']} specialist={route.get('specialist','') }"
            )
        if mvi.get("selected_files"):
            print(f"[MVI] arquivos relevantes: {', '.join(mvi['selected_files'][:5])}")

        task = self.manager.add_task(ai_instruction, agent_role)
        self.manager.add_checkpoint(task["id"], "execucao_terminal", required_by="dev")
        self.manager.add_checkpoint(task["id"], "qa_validado", required_by="dev")
        self.manager.add_checkpoint(task["id"], "deploy_autorizado", required_by="dev")
        self.manager.update_task_status(task["id"], "in_progress", "Execução iniciada.")

        if not self._request_approval(
            task["id"],
            stage="proposal",
            summary=f"Executar task com role {agent_role.value} e instrucao fornecida.",
            default_yes=True,
        ):
            self.manager.update_task_status(task["id"], "paused", "Proposta rejeitada pelo dev.")
            return {
                "status": "paused",
                "msg": "Execucao pausada na etapa de proposta.",
                "task_id": task["id"],
            }

        available_skills = ", ".join(self.factory.skills.keys())
        skill_name = self._ask(
            f"Escolha o contexto de skill ({available_skills})",
            default=route.get("skill", "automation_cli"),
        )
        print("\nContexto aplicado:")
        print(self.factory.get_skill_context(skill_name))

        command = self._ask("Comando final a executar", default=ai_instruction)
        allowed, policy_msg = self.policies.pre_execution(command)
        print(f"[POLICY] {policy_msg}")
        if not allowed:
            self.manager.update_task_status(task["id"], "blocked", policy_msg)
            self.evaluator.record(
                kind="task_execution",
                status="blocked",
                payload={"task_id": task["id"], "reason": policy_msg},
                started_at=started,
            )
            return {
                "status": "blocked",
                "msg": policy_msg,
                "task_id": task["id"],
            }

        if not self._request_approval(
            task["id"],
            stage="execution",
            summary=f"Executar comando: {command}",
            default_yes=True,
        ):
            self.manager.update_task_status(task["id"], "paused", "Execução negada pelo dev.")
            return {
                "status": "paused",
                "msg": "Execução pausada por decisão do dev.",
                "task_id": task["id"],
            }
        self.manager.approve_checkpoint(task["id"], "execucao_terminal", approver="dev")

        if self.interactive or self._looks_like_shell_command(command):
            result = self.executor.execute_command(command)
        else:
            workflow_name = self._extract_external_workflow_name(ai_instruction)
            if workflow_name:
                deliverable_path, message = self._run_external_workflow_deliverable(
                    workflow_name=workflow_name,
                    instruction=ai_instruction,
                    agent_role=agent_role,
                    task_id=task["id"],
                )
            else:
                deliverable_path = self._persist_textual_deliverable(task["id"], agent_role, ai_instruction)
                message = (
                    "Instrucao textual processada sem execucao de shell "
                    f"(role={agent_role.value}). Entregavel salvo em: {deliverable_path}"
                )
            result = {
                "status": "success",
                "stdout": message,
                "stderr": "",
                "return_code": 0,
                "deliverable_file": deliverable_path,
            }
        status = "completed" if result["status"] == "success" else "failed"

        qa_logs = []

        if self.interactive and self._ask_yes_no("Rodar checagem de segurança agora", default_yes=True):
            file_to_scan = self._ask("Arquivo para varredura de segurança", default="")
            if file_to_scan:
                ok, message = self.qa.run_security_check(file_to_scan)
                qa_logs.append(message)
                if not ok:
                    status = "failed"

        if self.interactive and self._ask_yes_no("Rodar testes automatizados agora", default_yes=True):
            suggested_cmd = self.factory.get_test_command(skill_name)
            test_cmd = self._ask("Comando de testes", default=suggested_cmd)
            if test_cmd:
                ok, message, test_output = self.qa.run_unit_tests_verbose(test_cmd)
                qa_logs.append(message)
                if not ok:
                    status = "failed"
                else:
                    cov_ok, cov_msg = self.qa.check_coverage_threshold(test_output, minimum_percent=80.0)
                    qa_logs.append(cov_msg)
                    if not cov_ok:
                        status = "failed"

        if status == "completed":
            self.manager.approve_checkpoint(task["id"], "qa_validado", approver="dev")
            self._request_approval(
                task["id"],
                stage="qa_gate",
                summary="Qualidade aprovada para possivel deploy.",
                default_yes=True,
            )

        if status == "completed" and self._ask_yes_no("Ativar etapa de Growth", default_yes=False):
            product_name = self._ask("Nome do produto", default="OpenCode Squad")
            value_prop = self._ask("Proposta de valor", default="Automação ponta a ponta com IA")
            qa_logs.append(self.growth.generate_landing_page(product_name, value_prop))

            if self._ask_yes_no("Executar deploy simulado", default_yes=False):
                target = self._ask("Alvo do deploy (vercel/aws)", default="vercel")
                if self._request_approval(
                    task["id"],
                    stage="deploy_gate",
                    summary=f"Deploy para {target}",
                    default_yes=True,
                ):
                    can_deploy, deploy_msg = self.policies.pre_deploy(
                        qa_approved=(status == "completed"),
                        target=target,
                    )
                    if can_deploy:
                        qa_logs.append(self.growth.deploy_to_production(target))
                        self.manager.approve_checkpoint(task["id"], "deploy_autorizado", approver="dev")
                    else:
                        qa_logs.append(deploy_msg)
                        status = "failed"

        combined_log = str(result)
        if qa_logs:
            combined_log += "\n" + "\n".join(qa_logs)

        self.manager.update_task_status(task["id"], status, combined_log)
        self.evaluator.record(
            kind="task_execution",
            status=status,
            payload={"task_id": task["id"], "role": agent_role.value},
            started_at=started,
        )
        result["task_id"] = task["id"]
        result["final_status"] = status
        result["checkpoints"] = qa_logs
        return result


bridge = VoxenBridge()
