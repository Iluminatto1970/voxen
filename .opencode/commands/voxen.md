---
description: Executa comandos do Voxen CLI
---
Voce esta operando `/voxen` neste projeto.

Objetivo:
- Para comandos de planejamento/ideacao, agir de forma conversacional no estilo antigravity-kit.
- Para comandos operacionais, executar o Voxen CLI exatamente uma vez e resumir o resultado.

Regras obrigatorias:
1) Use exatamente os argumentos recebidos em `$ARGUMENTS`.
2) Nunca reutilize a saida de um comando como novo argumento.
3) Nunca encadeie automaticamente `route -> plan -> run`.
4) Nao invente comandos; somente os definidos em `/voxen help`.

Roteamento:
- Se `$ARGUMENTS` comecar com: `brainstorm`, `plan`, `create`, `debug`, `enhance`,
  `preview`, `orchestrate`, `test`, `deploy` ou `workflow`, nao rode CLI de imediato.
  Conduza conversa guiada, levante contexto essencial e ofereca opcoes com tradeoffs.

- Se `$ARGUMENTS` comecar com: `status`, `skills`, `list`, `context`, `route`,
  `workflows`, `specialists`, `bundle`, `eval`, `profiles`, execute:

`./.voxen/bin/voxen --cmd "/voxen $ARGUMENTS"`

e traga um resumo objetivo do resultado.

Importante:
- Se o usuario pediu `route`, responda somente o route.
- Nao transformar retorno de `route` em comando `plan` automaticamente.
