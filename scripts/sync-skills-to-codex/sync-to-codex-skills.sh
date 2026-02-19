#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Sync all local skills from this repository into Codex skills directory.

Usage:
  sync-to-codex-skills.sh [--symlink|--copy] [--force] [--dry-run]

Options:
  --symlink   Create per-skill symlinks in Codex skills dir (default)
  --copy      Copy skill folders instead of symlinking
  --force     Replace existing destinations
  --dry-run   Print planned actions without changing filesystem
  -h, --help  Show this help

Environment:
  CODEX_HOME  If set, destination is $CODEX_HOME/skills
              Otherwise destination is ~/.codex/skills
EOF
}

MODE="symlink"
FORCE="false"
DRY_RUN="false"

while (($# > 0)); do
  case "$1" in
    --symlink)
      MODE="symlink"
      ;;
    --copy)
      MODE="copy"
      ;;
    --force)
      FORCE="true"
      ;;
    --dry-run)
      DRY_RUN="true"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"
SOURCE_DIR="$REPO_ROOT/skills"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}"
DEST_DIR="$DEST_ROOT/skills"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Source directory does not exist: $SOURCE_DIR" >&2
  exit 1
fi

mkdir_cmd() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] mkdir -p \"$DEST_DIR\""
  else
    mkdir -p "$DEST_DIR"
  fi
}

remove_existing() {
  local target="$1"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] rm -rf \"$target\""
  else
    rm -rf "$target"
  fi
}

create_link() {
  local src="$1"
  local dst="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] ln -s \"$src\" \"$dst\""
  else
    ln -s "$src" "$dst"
  fi
}

copy_dir() {
  local src="$1"
  local dst="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] cp -R \"$src\" \"$dst\""
  else
    cp -R "$src" "$dst"
  fi
}

mkdir_cmd

installed=0
skipped=0
replaced=0

shopt -s nullglob
for skill_path in "$SOURCE_DIR"/*; do
  [[ -d "$skill_path" ]] || continue
  skill_name="$(basename "$skill_path")"
  dest_path="$DEST_DIR/$skill_name"

  if [[ -L "$dest_path" ]]; then
    current_target="$(readlink "$dest_path" || true)"
    if [[ "$MODE" == "symlink" && "$current_target" == "$skill_path" ]]; then
      echo "SKIP   $skill_name (already linked)"
      ((skipped += 1))
      continue
    fi
  fi

  if [[ -e "$dest_path" || -L "$dest_path" ]]; then
    if [[ "$FORCE" == "true" ]]; then
      remove_existing "$dest_path"
      ((replaced += 1))
    else
      echo "SKIP   $skill_name (destination exists: $dest_path)"
      ((skipped += 1))
      continue
    fi
  fi

  if [[ "$MODE" == "symlink" ]]; then
    create_link "$skill_path" "$dest_path"
    echo "LINK   $skill_name -> $skill_path"
  else
    copy_dir "$skill_path" "$dest_path"
    echo "COPY   $skill_name -> $dest_path"
  fi
  ((installed += 1))
done

echo
echo "Done."
echo "Source:      $SOURCE_DIR"
echo "Destination: $DEST_DIR"
echo "Mode:        $MODE"
echo "Installed:   $installed"
echo "Replaced:    $replaced"
echo "Skipped:     $skipped"
