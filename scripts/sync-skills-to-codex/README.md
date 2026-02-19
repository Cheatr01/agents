# Sync Skills To Codex

Synchronizes all skill directories from this repository's `skills/` folder into Codex skills.

## Script

- `sync-to-codex-skills.sh`

## Usage

```bash
./scripts/sync-skills-to-codex/sync-to-codex-skills.sh
```

Default mode creates one symlink per skill in:

- `$CODEX_HOME/skills` (if `CODEX_HOME` is set)
- otherwise `~/.codex/skills`

## Options

```bash
./scripts/sync-skills-to-codex/sync-to-codex-skills.sh --copy
./scripts/sync-skills-to-codex/sync-to-codex-skills.sh --force
./scripts/sync-skills-to-codex/sync-to-codex-skills.sh --dry-run
```
