# Repositorios de Referencia (Exemplo)

Este arquivo lista repositorios citados durante a configuracao e uso do Voxen.

## Principais

- `https://github.com/Iluminatto1970/voxen`
  - Repositorio principal do projeto Voxen (CLI, orquestracao e integracoes).

- `https://github.com/vudovn/antigravity-kit`
  - Base de referencia para workflows, agentes e estrutura `.agent`.

- `https://github.com/vudovn/antigravity-awesome-skills`
  - Fonte complementar de skills usadas pelo catalogo do Voxen.

## URLs adicionais citadas no projeto

- `https://github.com/vudovn/antigravity-kit.git`
  - URL usada como referencia de sincronizacao no README e no instalador.

- `https://raw.githubusercontent.com/Iluminatto1970/voxen/main/install.sh`
  - Endpoint de instalacao por curl do Voxen.

## Como usar no projeto

- Workflows e especialistas podem ser carregados de:
  - `.agent/workflows`
  - `.agent/agents`

- Skills podem ser priorizadas a partir de:
  - `.agent/skills` (projeto atual)
  - `_references/antigravity-kit/.agent/skills`
  - `_references/antigravity-awesome-skills/skills`

## Observacao

Se quiser manter paridade completa com o Antigravity-kit, mantenha estes repositorios sincronizados e valide com os comandos de checklist/verify antes de deploy.
