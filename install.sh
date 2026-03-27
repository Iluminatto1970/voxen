#!/usr/bin/env bash
set -euo pipefail

REPO="${VOXEN_REPO:-Iluminatto1970/voxen}"
BRANCH="${VOXEN_BRANCH:-main}"
INSTALL_DIR="${VOXEN_INSTALL_DIR:-$HOME/.voxen}"
BIN_DIR="${VOXEN_BIN_DIR:-$HOME/.local/bin}"
SRC_DIR="$INSTALL_DIR/src"
INSTALL_BIN_DIR="$INSTALL_DIR/bin"
PROJECT_DIR="${VOXEN_PROJECT_DIR:-$PWD}"

create_opencode_command_file() {
  local project_dir="$1"
  mkdir -p "$project_dir/.opencode/commands"
  cat > "$project_dir/.opencode/commands/voxen.md" <<'EOF'
---
description: Executa comandos do Voxen CLI
---
Execute o Voxen CLI no projeto e resuma o resultado de forma objetiva.
Use os argumentos passados para montar o comando '/voxen'.

!`./.voxen/bin/voxen --cmd "/voxen $ARGUMENTS"`
EOF
}

is_safe_bootstrap_target() {
  local project_dir="$1"
  local resolved
  resolved="$(cd "$project_dir" 2>/dev/null && pwd -P || printf "%s" "$project_dir")"
  [[ "$resolved" == "/" ]] && return 1
  return 0
}

MODE="global"
if [[ -n "${1:-}" ]]; then
  case "$1" in
    --project)
      MODE="project"
      shift
      ;;
    --both)
      MODE="both"
      shift
      ;;
    --global)
      MODE="global"
      shift
      ;;
  esac
fi

if [[ -n "${1:-}" ]]; then
  PROJECT_DIR="$1"
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[Voxen] Erro: python3 nao encontrado." >&2
  exit 1
fi

install_source() {
  echo "[Voxen] Instalando fonte $REPO ($BRANCH)"
  mkdir -p "$INSTALL_DIR"

  if command -v git >/dev/null 2>&1; then
    if [[ -d "$SRC_DIR/.git" ]]; then
      echo "[Voxen] Atualizando instalacao existente..."
      git -C "$SRC_DIR" fetch origin "$BRANCH"
      git -C "$SRC_DIR" checkout "$BRANCH"
      git -C "$SRC_DIR" pull --ff-only origin "$BRANCH"
    else
      rm -rf "$SRC_DIR"
      echo "[Voxen] Clonando repositorio..."
      git clone --branch "$BRANCH" --depth 1 "https://github.com/$REPO.git" "$SRC_DIR"
    fi
  else
    echo "[Voxen] Git nao encontrado. Usando download tar.gz..."
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    ARCHIVE_URL="https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH"
    curl -fsSL "$ARCHIVE_URL" -o "$TMP_DIR/voxen.tar.gz"
    rm -rf "$SRC_DIR"
    mkdir -p "$SRC_DIR"
    tar -xzf "$TMP_DIR/voxen.tar.gz" -C "$TMP_DIR"
    EXTRACTED_DIR="$TMP_DIR/$(basename "$REPO")-$BRANCH"
    cp -R "$EXTRACTED_DIR"/* "$SRC_DIR"
  fi
}

install_auto_update_helper() {
  mkdir -p "$INSTALL_BIN_DIR"
  cat > "$INSTALL_BIN_DIR/voxen_auto_update.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail

ENABLED="\${VOXEN_AUTO_UPDATE:-1}"
INTERVAL="\${VOXEN_AUTO_UPDATE_INTERVAL:-21600}"
STATE_FILE="$INSTALL_DIR/.last_auto_update"
SRC_DIR="$SRC_DIR"
BRANCH="$BRANCH"

if [[ "\$ENABLED" == "0" || "\$ENABLED" == "false" || "\$ENABLED" == "off" ]]; then
  exit 0
fi

if ! [[ "\$INTERVAL" =~ ^[0-9]+$ ]]; then
  INTERVAL=21600
fi

if ! command -v git >/dev/null 2>&1; then
  exit 0
fi

if [[ ! -d "\$SRC_DIR/.git" ]]; then
  exit 0
fi

NOW="\$(date +%s)"
LAST=0
if [[ -f "\$STATE_FILE" ]]; then
  LAST="\$(cat "\$STATE_FILE" 2>/dev/null || printf '0')"
fi

if [[ "\$LAST" =~ ^[0-9]+$ ]] && (( NOW - LAST < INTERVAL )); then
  exit 0
fi

LOCAL_HEAD="\$(git -C "\$SRC_DIR" rev-parse HEAD 2>/dev/null || printf '')"
git -C "\$SRC_DIR" fetch origin "\$BRANCH" >/dev/null 2>&1 || exit 0
REMOTE_HEAD="\$(git -C "\$SRC_DIR" rev-parse "origin/\$BRANCH" 2>/dev/null || printf '')"

if [[ -n "\$REMOTE_HEAD" && "\$LOCAL_HEAD" != "\$REMOTE_HEAD" ]]; then
  git -C "\$SRC_DIR" checkout "\$BRANCH" >/dev/null 2>&1 || exit 0
  git -C "\$SRC_DIR" pull --ff-only origin "\$BRANCH" >/dev/null 2>&1 || exit 0
  printf '[Voxen] Atualizado automaticamente para a ultima versao (%s).\n' "\$BRANCH"
fi

printf '%s' "\$NOW" > "\$STATE_FILE"
EOF
  chmod +x "$INSTALL_BIN_DIR/voxen_auto_update.sh"
}

install_global() {
  mkdir -p "$BIN_DIR"
  install_auto_update_helper

  cat > "$BIN_DIR/voxen" <<EOF
#!/usr/bin/env bash
if [[ -x "$INSTALL_BIN_DIR/voxen_auto_update.sh" ]]; then
  "$INSTALL_BIN_DIR/voxen_auto_update.sh" || true
fi
exec python3 "$SRC_DIR/voxen.py" "\$@"
EOF
  chmod +x "$BIN_DIR/voxen"

  cat > "$BIN_DIR/voxen-update" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ -x "$INSTALL_BIN_DIR/voxen_auto_update.sh" ]]; then
  VOXEN_AUTO_UPDATE_INTERVAL=0 "$INSTALL_BIN_DIR/voxen_auto_update.sh"
  exit 0
fi
echo "[Voxen] Atualizador nao encontrado em $INSTALL_BIN_DIR/voxen_auto_update.sh" >&2
exit 1
EOF
  chmod +x "$BIN_DIR/voxen-update"

cat > "$BIN_DIR/voxen-init" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="\${1:-\$PWD}"
VOXEN_INSTALL_DIR="\${VOXEN_INSTALL_DIR:-\$HOME/.voxen}"
SRC_DIR="\$VOXEN_INSTALL_DIR/src"
INSTALL_BIN_DIR="\$VOXEN_INSTALL_DIR/bin"
mkdir -p "\$PROJECT_DIR/.voxen/bin"
cat > "\$PROJECT_DIR/.voxen/bin/voxen" <<'EOV'
#!/usr/bin/env bash
set -euo pipefail
VOXEN_INSTALL_DIR="\${VOXEN_INSTALL_DIR:-\$HOME/.voxen}"
SRC_DIR="\$VOXEN_INSTALL_DIR/src"
INSTALL_BIN_DIR="\$VOXEN_INSTALL_DIR/bin"
if [[ -x "\$INSTALL_BIN_DIR/voxen_auto_update.sh" ]]; then
  "\$INSTALL_BIN_DIR/voxen_auto_update.sh" || true
fi
exec python3 "\$SRC_DIR/voxen.py" "\$@"
EOV
chmod +x "\$PROJECT_DIR/.voxen/bin/voxen"
mkdir -p "\$PROJECT_DIR/.opencode/commands"
cat > "\$PROJECT_DIR/.opencode/commands/voxen.md" <<'EOV'
---
description: Executa comandos do Voxen CLI
---
Execute o Voxen CLI no projeto e resuma o resultado de forma objetiva.
Use os argumentos passados para montar o comando '/voxen'.

!`./.voxen/bin/voxen --cmd "/voxen $ARGUMENTS"`
EOV
cat > "\$PROJECT_DIR/.voxen/README.md" <<'EOV'
# Voxen local do projeto

Use este launcher local:

```bash
./.voxen/bin/voxen
```
EOV
echo "[Voxen] Projeto inicializado em \$PROJECT_DIR/.voxen"
echo "[Voxen] Comando do OpenCode criado em \$PROJECT_DIR/.opencode/commands/voxen.md"
EOF
  chmod +x "$BIN_DIR/voxen-init"

  echo "[Voxen] Instalacao global concluida."
  echo "[Voxen] Comandos: $BIN_DIR/voxen, $BIN_DIR/voxen-init e $BIN_DIR/voxen-update"

  case ":$PATH:" in
    *":$BIN_DIR:"*)
      echo "[Voxen] PATH ja contem $BIN_DIR"
      ;;
    *)
      echo "[Voxen] Adicione ao PATH para usar 'voxen' direto:"
      echo "  export PATH=\"$BIN_DIR:\$PATH\""
      ;;
  esac
}

install_project() {
  local target_dir="$PROJECT_DIR/.voxen"
  mkdir -p "$target_dir/bin"

  cat > "$target_dir/bin/voxen" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ -x "$INSTALL_BIN_DIR/voxen_auto_update.sh" ]]; then
  "$INSTALL_BIN_DIR/voxen_auto_update.sh" || true
fi
exec python3 "$SRC_DIR/voxen.py" "\$@"
EOF
  chmod +x "$target_dir/bin/voxen"
  create_opencode_command_file "$PROJECT_DIR"

  cat > "$target_dir/README.md" <<'EOF'
# Voxen local do projeto

Comando local:

```bash
./.voxen/bin/voxen --cmd "/voxen"
```

Para instalar em outros projetos:

```bash
voxen-init /caminho/do/projeto
```
EOF

  echo "[Voxen] Instalacao por projeto concluida: $target_dir"
  echo "[Voxen] Use: ./.voxen/bin/voxen --cmd \"/voxen\""
  echo "[Voxen] Comando do OpenCode: $PROJECT_DIR/.opencode/commands/voxen.md"
}

install_source

if [[ "$MODE" == "global" ]]; then
  install_global
  if is_safe_bootstrap_target "$PROJECT_DIR"; then
    install_project
  else
    echo "[Voxen] Aviso: bootstrap local ignorado para diretorio nao seguro: '$PROJECT_DIR'"
  fi
elif [[ "$MODE" == "project" ]]; then
  if is_safe_bootstrap_target "$PROJECT_DIR"; then
    install_project
  else
    echo "[Voxen] Erro: diretorio de projeto invalido para bootstrap: '$PROJECT_DIR'" >&2
    exit 1
  fi
else
  install_global
  if is_safe_bootstrap_target "$PROJECT_DIR"; then
    install_project
  else
    echo "[Voxen] Aviso: bootstrap local ignorado para diretorio nao seguro: '$PROJECT_DIR'"
  fi
fi

echo "[Voxen] Teste rapido: voxen --cmd \"/voxen\""
