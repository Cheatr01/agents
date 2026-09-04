#!/usr/bin/env bash
set -u -o pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: run-compact.sh <label> [--history <path>] -- <command> [args ...]" >&2
  exit 64
fi

label="$1"
shift
history_file=""

if [[ $# -ge 2 && "$1" == "--history" ]]; then
  history_file="$2"
  shift 2
fi

if [[ $# -lt 2 || "$1" != "--" ]]; then
  echo "usage: run-compact.sh <label> [--history <path>] -- <command> [args ...]" >&2
  exit 64
fi

shift
safe_label="${label//[^A-Za-z0-9._-]/-}"
log_file="${TMPDIR:-/tmp}/codex-${safe_label}-$$.log"

if [[ -n "$history_file" ]]; then
  history_dir="$(dirname "$history_file")"
  if [[ ! -d "$history_dir" ]]; then
    echo "FAIL label=${safe_label} status=64 history-directory-missing=${history_dir}" >&2
    exit 64
  fi
  touch "$history_file"
  if grep -Fq "${safe_label}|pass|" "$history_file"; then
    printf 'WARN label=%s repeated-success reason=required\n' "$safe_label" >&2
  fi
fi

"$@" >"$log_file" 2>&1
status=$?

if [[ $status -eq 0 ]]; then
  printf 'PASS label=%s status=0 log=%s\n' "$safe_label" "$log_file"
  if [[ -n "$history_file" ]]; then
    printf '%s|pass|%s\n' "$safe_label" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$history_file"
  fi
else
  printf 'FAIL label=%s status=%s log=%s\n' "$safe_label" "$status" "$log_file" >&2
  if [[ -n "$history_file" ]]; then
    printf '%s|fail|%s\n' "$safe_label" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$history_file"
  fi
fi

exit "$status"
