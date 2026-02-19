# Sync Subagents To Codex

Installs subagent TOML definitions from this repository into Codex and updates `config.toml`.

## What it does

- Syncs files from `subagents/*.toml` to:
  - `$CODEX_HOME/agents` (if `CODEX_HOME` is set)
  - otherwise `~/.codex/agents`
- Updates `$CODEX_HOME/config.toml` (or `~/.codex/config.toml`)
- Ensures:
  - `[features]` contains `multi_agent = true`
  - a managed block with `[agents.<name>]` entries exists

## Script

- `sync-subagents-to-codex.sh`

## Usage

```bash
./scripts/sync-subagents-to-codex/sync-subagents-to-codex.sh
```

## Options

```bash
./scripts/sync-subagents-to-codex/sync-subagents-to-codex.sh --dry-run
./scripts/sync-subagents-to-codex/sync-subagents-to-codex.sh --force
./scripts/sync-subagents-to-codex/sync-subagents-to-codex.sh --copy
```

Notes:
- Default mode uses symlinks.
- `--force` replaces existing files in the destination `agents` directory.
