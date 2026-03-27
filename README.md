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

Private billing work should live in the local/private branch `billing-private`.

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
- Por projeto (diretorio atual): cria `./.voxen/bin/voxen`
  ```bash
  curl -fsSL https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh | bash -s -- --project
  ```
- Global + projeto atual
  ```bash
  curl -fsSL https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh | bash -s -- --both
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
