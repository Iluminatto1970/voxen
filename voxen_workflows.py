from __future__ import annotations

from voxen_manager import AgentRole


class VoxenWorkflows:
    """
    Workflows estilo antigravity-kit para execucao padronizada.
    """

    def __init__(self) -> None:
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

    def names(self) -> list[str]:
        return sorted(self._workflows.keys())

    def build_steps(self, workflow: str, intent: str) -> list[dict]:
        base = self._workflows.get(workflow, self._workflows["create"])
        steps = []
        for role, instruction in base:
            steps.append(
                {
                    "role": role.value,
                    "instruction": f"{instruction} Contexto da missao: {intent}",
                }
            )
        return steps
