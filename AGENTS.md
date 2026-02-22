# AGENTS

## Purpose

This repository stores reusable assets for local agent workflows.

## Conventions

- Keep files organized by domain (`skills/`, `subagents/`, `subagents/rules/`).
- Prefer small, focused markdown docs and simple text-based configs.
- Use clear naming so assets are easy to find and reuse.
- Keep automated eval assets under `tests/`:
  - `tests/test_fixtures/` for shared fixtures only
  - `tests/src/` for test code, mirroring root skill layout (`tests/src/skills/<skill-name>/`)
  - keep skill-specific prompts, sample responses, and gate requirements inside each skill test folder
  - prefer runners that discover `tests/src/skills/*` and execute isolated per-skill test flows
  - `tests/results/` for generated test outputs

## Notes

- Add new rules under `subagents/rules/`.
- Keep this file updated when structure or conventions change.
