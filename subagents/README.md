# Subagent Definitions

This folder contains role-specific Codex subagent TOML definitions.

## Files

- `pm.toml`
- `architect.toml`
- `web-designer.toml`
- `app-designer.toml`
- `backend-engineer.toml`
- `frontend-engineer.toml`
- `efficiency-expert.toml`
- `quality-lead.toml`
- `quality-engineer.toml`
- `security-reviewer.toml`
- `tech-lead.toml`

## Usage in Codex config

Add role registry entries in your `.codex/config.toml` and point `config_file` to these files.
Example:

```toml
[agents.pm]
description = "Scope and acceptance-criteria specialist"
config_file = "subagents/pm.toml"

[agents.architect]
description = "Contract and architecture specialist"
config_file = "subagents/architect.toml"
```

Note: `config_file` path is resolved relative to the config file that declares the agent.
