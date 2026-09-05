#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Sync subagent TOML definitions from this repository into Codex config.

Usage:
  sync-subagents-to-codex.sh [--symlink|--copy] [--force] [--dry-run]

Options:
  --symlink   Create per-file symlinks in Codex agents dir (default)
  --copy      Copy TOML files instead of symlinking
  --force     Replace existing destination files/symlinks
  --dry-run   Print actions without writing changes
  -h, --help  Show this help

Environment:
  CODEX_HOME  If set, target paths are under $CODEX_HOME
              Otherwise target paths are under ~/.codex
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
SOURCE_DIR="$REPO_ROOT/subagents"
CODEX_ROOT="${CODEX_HOME:-$HOME/.codex}"
DEST_AGENTS_DIR="$CODEX_ROOT/agents"
CONFIG_FILE="$CODEX_ROOT/config.toml"

MANAGED_BEGIN="# BEGIN MANAGED SUBAGENTS (team-orchestrator)"
MANAGED_END="# END MANAGED SUBAGENTS (team-orchestrator)"

ROLE_FILES=(
  "pm.toml"
  "architect.toml"
  "web-designer.toml"
  "app-designer.toml"
  "backend-engineer.toml"
  "frontend-engineer.toml"
  "bugfix-evidence-collector.toml"
  "bugfix-investigator.toml"
  "efficiency-expert.toml"
  "quality-lead.toml"
  "quality-engineer.toml"
  "security-reviewer.toml"
  "tech-lead.toml"
)

section_from_file() {
  local f="$1"
  echo "${f%.toml}"
}

description_from_section() {
  local s="$1"
  case "$s" in
    pm) echo "Product scope and acceptance criteria owner." ;;
    architect) echo "Architecture and API contract specialist." ;;
    web-designer) echo "Web design system and tokens specialist." ;;
    app-designer) echo "App/mobile design system and tokens specialist." ;;
    backend-engineer) echo "Backend implementation specialist." ;;
    frontend-engineer) echo "Frontend implementation specialist." ;;
    bugfix-evidence-collector) echo "Read-only bug evidence collection specialist." ;;
    bugfix-investigator) echo "Evidence-backed root-cause investigation specialist." ;;
    efficiency-expert) echo "Performance and efficiency specialist." ;;
    quality-lead) echo "Quality strategy and gate owner." ;;
    quality-engineer) echo "Automated testing and defect reproduction specialist." ;;
    security-reviewer) echo "Security risk reviewer and remediation advisor." ;;
    tech-lead) echo "Technical governance and final acceptance owner." ;;
    *) echo "Specialized agent role." ;;
  esac
}

ensure_dir() {
  local d="$1"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] mkdir -p \"$d\""
  else
    mkdir -p "$d"
  fi
}

remove_path() {
  local p="$1"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] rm -rf \"$p\""
  else
    rm -rf "$p"
  fi
}

link_or_copy() {
  local src="$1"
  local dst="$2"
  if [[ "$MODE" == "symlink" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
      echo "[dry-run] ln -s \"$src\" \"$dst\""
    else
      ln -s "$src" "$dst"
    fi
  else
    if [[ "$DRY_RUN" == "true" ]]; then
      echo "[dry-run] cp \"$src\" \"$dst\""
    else
      cp "$src" "$dst"
    fi
  fi
}

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

ensure_dir "$DEST_AGENTS_DIR"

linked=0
skipped=0
replaced=0

for rf in "${ROLE_FILES[@]}"; do
  src="$SOURCE_DIR/$rf"
  dst="$DEST_AGENTS_DIR/$rf"

  if [[ ! -f "$src" ]]; then
    echo "WARN   missing source file: $src"
    ((skipped += 1))
    continue
  fi

  if [[ -L "$dst" && "$MODE" == "symlink" ]]; then
    current="$(readlink "$dst" || true)"
    if [[ "$current" == "$src" ]]; then
      echo "SKIP   $rf (already linked)"
      ((skipped += 1))
      continue
    fi
  fi

  if [[ -e "$dst" || -L "$dst" ]]; then
    if [[ "$FORCE" == "true" ]]; then
      remove_path "$dst"
      ((replaced += 1))
    else
      echo "SKIP   $rf (destination exists: $dst, use --force to replace)"
      ((skipped += 1))
      continue
    fi
  fi

  link_or_copy "$src" "$dst"
  if [[ "$MODE" == "symlink" ]]; then
    echo "LINK   $rf -> $src"
  else
    echo "COPY   $rf -> $dst"
  fi
  ((linked += 1))
done

tmp_cfg="$(mktemp)"
tmp_no_managed="$(mktemp)"
trap 'rm -f "$tmp_cfg" "$tmp_no_managed"' EXIT

if [[ -f "$CONFIG_FILE" ]]; then
  cp "$CONFIG_FILE" "$tmp_cfg"
else
  : > "$tmp_cfg"
fi

# Remove previously managed block.
awk -v begin="$MANAGED_BEGIN" -v end="$MANAGED_END" '
  $0 == begin { in_block=1; next }
  $0 == end { in_block=0; next }
  !in_block { print }
' "$tmp_cfg" > "$tmp_no_managed"

# Ensure [features] multi_agent = true
tmp_features="$(mktemp)"
trap 'rm -f "$tmp_cfg" "$tmp_no_managed" "$tmp_features"' EXIT

awk '
  BEGIN { in_features=0; saw_features=0; saw_multi=0 }
  /^\[[^]]+\][[:space:]]*$/ {
    if (in_features && !saw_multi) {
      print "multi_agent = true"
      saw_multi=1
    }
    in_features = ($0 == "[features]")
    if (in_features) {
      saw_features=1
      saw_multi=0
    }
    print
    next
  }
  {
    if (in_features && $0 ~ /^[[:space:]]*multi_agent[[:space:]]*=/) {
      print "multi_agent = true"
      saw_multi=1
      next
    }
    print
  }
  END {
    if (in_features && !saw_multi) {
      print "multi_agent = true"
    } else if (!saw_features) {
      print ""
      print "[features]"
      print "multi_agent = true"
    }
  }
' "$tmp_no_managed" > "$tmp_features"

tmp_final="$(mktemp)"
trap 'rm -f "$tmp_cfg" "$tmp_no_managed" "$tmp_features" "$tmp_final"' EXIT
cp "$tmp_features" "$tmp_final"

{
  echo ""
  echo "$MANAGED_BEGIN"
  for rf in "${ROLE_FILES[@]}"; do
    src="$SOURCE_DIR/$rf"
    [[ -f "$src" ]] || continue
    section="$(section_from_file "$rf")"
    config_rel="agents/$rf"
    desc="$(description_from_section "$section")"

    if grep -Eq "^[[:space:]]*\\[agents\\.${section}\\][[:space:]]*$" "$tmp_features"; then
      echo "# skipped agents.$section (already defined outside managed block)"
      continue
    fi

    echo "[agents.${section}]"
    echo "description = \"$desc\""
    echo "config_file = \"$config_rel\""
    echo ""
  done
  echo "$MANAGED_END"
} >> "$tmp_final"

if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "[dry-run] would update: $CONFIG_FILE"
  echo "----- managed config preview -----"
  sed -n '/^# BEGIN MANAGED SUBAGENTS (team-orchestrator)$/,/^# END MANAGED SUBAGENTS (team-orchestrator)$/p' "$tmp_final"
else
  ensure_dir "$CODEX_ROOT"
  cp "$tmp_final" "$CONFIG_FILE"
  echo ""
  echo "UPDATED $CONFIG_FILE"
fi

echo ""
echo "Done."
echo "Source:      $SOURCE_DIR"
echo "Agents dir:  $DEST_AGENTS_DIR"
echo "Config:      $CONFIG_FILE"
echo "Mode:        $MODE"
echo "Linked/Copied: $linked"
echo "Replaced:      $replaced"
echo "Skipped:       $skipped"
