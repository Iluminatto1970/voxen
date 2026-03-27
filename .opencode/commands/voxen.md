---
description: Executa comandos do Voxen CLI
---
Voce esta operando o comando `/voxen` no projeto.

Regras de execucao:

1) Para fluxos estilo antigravity (interacao conversacional), quando `$ARGUMENTS`
comecar com um destes subcomandos:

- `brainstorm`
- `plan`
- `create`
- `debug`
- `enhance`
- `preview`
- `orchestrate`
- `test`
- `deploy`
- `workflow`

Comporte-se como workflow guiado: converse com o usuario, faca perguntas curtas
de contexto quando faltarem dados, apresente opcoes com tradeoffs e recomende
proximo passo. Nao gerar codigo na primeira resposta desse fluxo.

Formato esperado:

```markdown
## 🧠 Brainstorm: [Topico]

### Context
[Resumo curto do problema]

---

### Option A: [Nome]
[Descricao]

✅ **Pros:**
- ...

❌ **Cons:**
- ...

📊 **Effort:** Low | Medium | High

---

### Option B: [Nome]
...

### Option C: [Nome]
...

## 💡 Recommendation

**Option [X]** because [reasoning].

What direction would you like to explore?
```

2) Para subcomandos operacionais (status, skills, list, context, route etc),
- Execute o Voxen CLI com `/voxen $ARGUMENTS`.
- Resuma o resultado de forma objetiva.

!`./.voxen/bin/voxen --cmd "/voxen $ARGUMENTS"`
