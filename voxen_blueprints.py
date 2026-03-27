def get_blueprints() -> dict[str, list[dict]]:
    return {
        "micro_saas": [
            {
                "role": "Manager",
                "instruction": "Definir user story de checkout e metricas de conversao.",
            },
            {
                "role": "Dev",
                "instruction": "Implementar autenticacao e estrutura inicial da API de assinatura.",
            },
            {
                "role": "Tester",
                "instruction": "Executar testes de fluxo de pagamento e validar erros de transacao.",
            },
            {
                "role": "Growth",
                "instruction": "Gerar landing page focada em captura de leads com CTA claro.",
            },
        ],
        "dev_tool_cli": [
            {
                "role": "Manager",
                "instruction": "Definir escopo da CLI e criterios de performance/seguranca.",
            },
            {
                "role": "Dev",
                "instruction": "Construir comandos base, parser de argumentos e tratamento de erro robusto.",
            },
            {
                "role": "Tester",
                "instruction": "Rodar testes de regressao, seguranca e validacao de saida da CLI.",
            },
            {
                "role": "Growth",
                "instruction": "Preparar copy tecnica e plano de lancamento para comunidade dev.",
            },
        ],
        "support_agent": [
            {
                "role": "Manager",
                "instruction": "Mapear intents principais e politicas de atendimento seguras.",
            },
            {
                "role": "Dev",
                "instruction": "Implementar pipeline RAG e integracao inicial com canal de mensagens.",
            },
            {
                "role": "Tester",
                "instruction": "Validar alucinacao, conformidade e fallback humano.",
            },
            {
                "role": "Growth",
                "instruction": "Configurar playbook de retencao e coleta de feedback dos usuarios.",
            },
        ],
    }
