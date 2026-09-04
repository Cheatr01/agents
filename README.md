# Agent Assets Repository

This repository stores assets for my agents, primarily for Codex.

## Structure

- `skills/` - skill packages and related files
- `subagents/` - subagent-specific assets
- `subagents/rules/` - rules for subagents
- `plugins/` - self-contained Codex Marketplace plugin packages
- `.agents/plugins/marketplace.json` - repo-local Marketplace catalog

## Marketplace

The local Marketplace exposes `team-delivery`, `product-discovery`, and the
standalone `aws-mcp` skill. `hello-world` remains an internal invocation/eval
fixture and is intentionally not listed.
