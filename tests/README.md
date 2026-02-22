# Tests

This folder contains targeted skill evals inspired by OpenAI's recommendation to use a small, focused prompt set to catch regressions early.

Reference:
- https://developers.openai.com/blog/eval-skills#4-use-a-small-targeted-prompt-set-to-catch-regressions-early

## Structure

- `test_fixtures/` shared fixtures only (cross-skill fixtures, common expectations)
- `src/` test code and per-skill tests (mirrors `skills/`)
- `src/skills/<skill-name>/` is the primary home for that skill's tests, prompts, sample responses, and gate requirements
- `results/` generated test outputs

## Quick Start

Run isolated test flow for all skill test folders under `tests/src/skills`:

```bash
python3 tests/src/run_all.py
```

Run isolated test flow for selected skills only:

```bash
python3 tests/src/run_all.py --skills scope-to-acceptance orchestration-scorekeeper
```

Run one skill suite directly:

```bash
python3 tests/src/common/run_skill_suite.py \
  --skill scope-to-acceptance \
  --out-dir tests/results/skills/scope-to-acceptance
```

## Notes

- Repository mode discovers `tests/src/skills/*` and runs a separate isolated flow per skill.
- Each skill flow can run:
  - gate lint (`gate_requirements.json`) if present
  - one or more evals (`eval_config.json` or `*.eval_config.json`) if present
- Outputs are isolated per skill under `tests/results/skills/<skill>/`.
- Repo summary is written to `tests/results/repo-suite-summary.json`.
- The targeted prompt set validates response contracts and negative controls.
- The gate lint discovers `gate_requirements.json` files inside each skill test folder and validates required sections/snippets in `skills/<skill>/SKILL.md`.
- Replace sample responses with real model outputs to track regressions across revisions.
