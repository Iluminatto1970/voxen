from __future__ import annotations

from pathlib import Path

from voxen_manager import AgentRole


class VoxenWorkflows:
    """
    Workflows estilo antigravity-kit para execucao padronizada.
    """

    def __init__(self, source_roots: list[str] | None = None) -> None:
        root = Path(__file__).resolve().parent
        self.source_roots = [
            Path(item)
            for item in (
                source_roots
                or [
                    str(Path.cwd() / ".agent" / "workflows"),
                    str(root / "_references" / "antigravity-kit" / ".agent" / "workflows"),
                ]
            )
        ]
        self._workflows = {
            "plan": [
                (AgentRole.MANAGER, "Definir objetivo, riscos e entregavel da tarefa."),
                (AgentRole.DEVELOPER, "Gerar plano tecnico de implementacao em etapas."),
                (AgentRole.QA, "Definir estrategia de testes e criterios de aceite."),
            ],
            "debug": [
                (AgentRole.QA, "Reproduzir erro e capturar evidencias do problema."),
                (AgentRole.DEVELOPER, "Aplicar correcao minima e segura."),
                (AgentRole.QA, "Executar regressao para validar fix."),
            ],
            "test": [
                (AgentRole.QA, "Executar testes automatizados e revisar cobertura."),
                (AgentRole.DEVELOPER, "Corrigir falhas de testes encontradas."),
                (AgentRole.QA, "Revalidar suite final e publicar resultado."),
            ],
            "deploy": [
                (AgentRole.MANAGER, "Revisar readiness de release e rollback plan."),
                (AgentRole.QA, "Aprovar qualidade final pre-deploy."),
                (AgentRole.GROWTH, "Executar deploy e monitorar sinais iniciais."),
            ],
            "status": [
                (AgentRole.MANAGER, "Consolidar status das tasks e bloqueios ativos."),
            ],
            "create": [
                (AgentRole.MANAGER, "Definir escopo funcional minimo da entrega."),
                (AgentRole.DEVELOPER, "Implementar a funcionalidade proposta."),
                (AgentRole.QA, "Validar funcionalidade com testes."),
            ],
            "enhance": [
                (AgentRole.MANAGER, "Mapear impacto da melhoria sem quebrar funcionalidades existentes."),
                (AgentRole.DEVELOPER, "Aplicar enhancement incremental com foco em compatibilidade."),
                (AgentRole.QA, "Executar regressao e validar ganho da melhoria."),
            ],
            "preview": [
                (AgentRole.DEVELOPER, "Preparar build de preview para validacao rapida."),
                (AgentRole.QA, "Validar preview em cenarios criticos de uso."),
                (AgentRole.MANAGER, "Registrar feedback e decisao de follow-up."),
            ],
            "orchestrate": [
                (AgentRole.MANAGER, "Quebrar missao em subtarefas coordenadas."),
                (AgentRole.DEVELOPER, "Executar nucleo tecnico da missao."),
                (AgentRole.GROWTH, "Preparar impacto de negocio e comunicacao da entrega."),
            ],
        }
        self._external_workflows = {
            "brainstorm": "Structured idea exploration before implementation.",
            "ui-ux-pro-max": "Workflow focado em design e experiencia de interface.",
        }
        self._external_workflows.update(self._load_external_workflows())

    def _load_external_workflows(self) -> dict[str, str]:
        workflows: dict[str, str] = {}
        seen = set()
        for root in self.source_roots:
            if not root.exists():
                continue
            for file in sorted(root.glob("*.md")):
                name = file.stem.strip().lower()
                if not name or name in seen:
                    continue
                seen.add(name)
                try:
                    content = file.read_text(encoding="utf-8")
                except Exception:
                    content = ""
                description = ""
                if content.startswith("---\n"):
                    end = content.find("\n---\n", 4)
                    if end != -1:
                        block = content[4:end]
                        for line in block.splitlines():
                            if line.strip().lower().startswith("description:"):
                                description = line.split(":", 1)[1].strip()
                                break
                workflows[name] = description or "Workflow externo carregado do antigravity-kit."
        return workflows

    def names(self) -> list[str]:
        return sorted(set(self._workflows.keys()) | set(self._external_workflows.keys()))

    def build_steps(self, workflow: str, intent: str) -> list[dict]:
        normalized = workflow.strip().lower()
        if normalized in self._external_workflows:
            description = self._external_workflows[normalized]
            base = [
                (AgentRole.MANAGER, f"Aplicar workflow externo '{normalized}' com foco no objetivo informado. {description}"),
                (AgentRole.DEVELOPER, f"Consolidar plano tecnico do workflow externo '{normalized}' com passos acionaveis."),
                (AgentRole.QA, f"Definir validacao e criterios de aceite para o workflow externo '{normalized}'."),
            ]
        elif normalized in self._workflows:
            base = self._workflows[normalized]
        else:
            base = self._workflows["create"]
        steps = []
        for role, instruction in base:
            steps.append(
                {
                    "role": role.value,
                    "instruction": f"{instruction} Contexto da missao: {intent}",
                }
            )
        return steps
