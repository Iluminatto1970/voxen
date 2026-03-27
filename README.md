# Voxen

Voxen is a CLI orchestrator for autonomous software squads with:

- strategic triage and brainstorming,
- role/workflow routing,
- execution approvals and policy gates,
- QA checks and coverage gate,
- skill recommendations, bundles, pinning, and health,
- context/memory pipeline with command-based operation.

## Open Source Scope

Este repositorio publico contem o nucleo open-source do Voxen para orquestracao,
automacao de workflow, memoria/contexto e operacao via CLI.

Use `.env.example` como template para configuracoes locais. Nunca commite segredos.

## Quick start

```bash
python3 voxen.py
```

Direct command mode:

```bash
python3 voxen.py --cmd "/voxen"
python3 voxen.py --cmd "/voxen context;;/voxen status"
```

## Install via curl

Depois do push no GitHub, voce pode instalar com uma linha:

```bash
curl -fsSL https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh | bash
```

Modos de instalacao:

- Global (padrao): instala `voxen` e `voxen-init` em `~/.local/bin`
  ```bash
  curl -fsSL https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh | bash -s -- --global
  ```
  `--global` tambem prepara o projeto alvo para OpenCode (`./.voxen/bin/voxen`
  e `.opencode/commands/voxen.md`).
  A instalacao ativa auto-update do Voxen ao executar a CLI.
- Por projeto (diretorio atual ou caminho informado): cria `./.voxen/bin/voxen`
  ```bash
  curl -fsSL https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh | bash -s -- --project
  curl -fsSL https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh | bash -s -- --project /caminho/do/projeto
  ```
- Global + projeto atual (ou caminho informado)
  ```bash
  curl -fsSL https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh | bash -s -- --both
  curl -fsSL https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh | bash -s -- --both /caminho/do/projeto
  ```

Depois da instalacao global, qualquer novo projeto pode ser preparado com:

```bash
voxen-init /caminho/do/projeto
```

Tambem e possivel iniciar um projeto direto pela CLI do Voxen:

```bash
voxen --cmd "/voxen init /caminho/do/projeto"
```

Teste apos instalar:

```bash
voxen --cmd "/voxen"
```

Atualizacao manual imediata:

```bash
voxen-update
```

Controle de auto-update:

- Desativar: `export VOXEN_AUTO_UPDATE=0`
- Intervalo (segundos): `export VOXEN_AUTO_UPDATE_INTERVAL=21600`

## Integracao com OpenCode

Para o comando `/voxen` aparecer no menu de comandos do OpenCode, o projeto
precisa ter o arquivo `.opencode/commands/voxen.md`.

As opcoes abaixo ja criam esse arquivo automaticamente:

- `voxen-init /caminho/do/projeto`
- `voxen --cmd "/voxen init /caminho/do/projeto"`
- `install.sh --global`, `install.sh --project` e `install.sh --both`

Depois, reinicie o OpenCode dentro do diretorio do projeto e digite `/voxen`.

## Skills do antigravity-kit

O Voxen agora usa skills do `antigravity-kit` no projeto adaptado, com prioridade:

1. `.agent/skills` do projeto atual
2. `_references/antigravity-kit/.agent/skills` da instalacao Voxen
3. `_references/antigravity-awesome-skills/skills`

Na instalacao, o script sincroniza automaticamente o repositorio
`https://github.com/vudovn/antigravity-kit.git` para servir de fonte de skills.
