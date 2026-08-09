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
  - prefer a single skill-suite YAML per tested skill (`*.eval.yaml`) that contains required `eval_type`, `skill_path`, optional `gate_requirements`, required `grader`, required `rate`, optional `max_concurrency`, and eval cases together
  - prefer runners that discover `tests/src/skills/*` and execute isolated per-skill test flows
  - `tests/results/` for generated test outputs
- Keep global eval runtime defaults in `eval-config.toml` at repository root; suite YAML values override global config.

## Notes

- Add new rules under `subagents/rules/`.
- Keep pre-orchestration discovery and ideation skills under `skills/` and design them to hand off business briefs, not technical implementation plans.
- Keep this file updated when structure or conventions change.
