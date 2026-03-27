#!/usr/bin/env bash
set -euo pipefail

REPO="${VOXEN_REPO:-Iluminatto1970/voxen}"
BRANCH="${VOXEN_BRANCH:-main}"
INSTALL_DIR="${VOXEN_INSTALL_DIR:-$HOME/.voxen}"
BIN_DIR="${VOXEN_BIN_DIR:-$HOME/.local/bin}"
SRC_DIR="$INSTALL_DIR/src"
PROJECT_DIR="${VOXEN_PROJECT_DIR:-$PWD}"

MODE="global"
if [[ "${1:-}" == "--project" ]]; then
  MODE="project"
  shift
  if [[ -n "${1:-}" ]]; then
    PROJECT_DIR="$1"
  fi
elif [[ "${1:-}" == "--both" ]]; then
  MODE="both"
elif [[ "${1:-}" == "--global" || -z "${1:-}" ]]; then
  MODE="global"
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

install_global() {
  mkdir -p "$BIN_DIR"

  cat > "$BIN_DIR/voxen" <<EOF
#!/usr/bin/env bash
exec python3 "$SRC_DIR/voxen.py" "\$@"
EOF
  chmod +x "$BIN_DIR/voxen"

  cat > "$BIN_DIR/voxen-init" <<EOF
#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="\${1:-\$PWD}"
mkdir -p "\$PROJECT_DIR/.voxen/bin"
cat > "\$PROJECT_DIR/.voxen/bin/voxen" <<'EOV'
#!/usr/bin/env bash
set -euo pipefail
exec python3 "$SRC_DIR/voxen.py" "\$@"
EOV
chmod +x "\$PROJECT_DIR/.voxen/bin/voxen"
cat > "\$PROJECT_DIR/.voxen/README.md" <<'EOV'
# Voxen local do projeto

Use este launcher local:

```bash
./.voxen/bin/voxen
```
EOV
echo "[Voxen] Projeto inicializado em \$PROJECT_DIR/.voxen"
EOF
  chmod +x "$BIN_DIR/voxen-init"

  echo "[Voxen] Instalacao global concluida."
  echo "[Voxen] Comandos: $BIN_DIR/voxen e $BIN_DIR/voxen-init"

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
exec python3 "$SRC_DIR/voxen.py" "\$@"
EOF
  chmod +x "$target_dir/bin/voxen"

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
}

install_source

if [[ "$MODE" == "global" ]]; then
  install_global
elif [[ "$MODE" == "project" ]]; then
  install_project
else
  install_global
  install_project
fi

echo "[Voxen] Teste rapido: voxen --cmd \"/voxen\""
