# Tests

This folder contains targeted skill evals inspired by OpenAI's recommendation to use a small, focused prompt set to catch regressions early.

Reference:
- https://developers.openai.com/blog/eval-skills#4-use-a-small-targeted-prompt-set-to-catch-regressions-early

## Structure

- `test_fixtures/` shared fixtures only (cross-skill fixtures, common expectations)
- `src/` test code and per-skill tests (mirrors `skills/`)
- `src/skills/<skill-name>/` is the primary home for that skill's tests
  - preferred format: single-file YAML suite (`*.eval.yaml` / `*.eval.yml`)
  - every suite YAML is validated against [skill-suite.schema.yaml](/Users/jiri/agents/tests/src/common/skill-suite.schema.yaml)
- `results/` generated test outputs
- `../eval-config.toml` global eval runtime defaults; suite YAML can override any runtime field

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
  - schema lint (`schema:<eval>`) for every suite YAML before any eval execution
  - gate lint from embedded `gate_requirements` in the suite YAML, or legacy `gate_requirements.json`
  - one or more evals (`eval_config.json`, `*.eval_config.json`, `eval.yaml`, `*.eval.yaml`) if present
- CLI output prints aligned per-step status, runtime, and effective eval runtime config for each eval.
- Outputs are isolated per skill under `tests/results/skills/<skill>/`.
- Repo summary is written to `tests/results/repo-suite-summary.json`.
- The targeted prompt set validates response contracts and negative controls.
- The preferred suite YAML contains required `eval_type`, `skill`, `skill_path`, optional `gate_requirements`, required `grader`, required `rate`, and required `cases`.
- The gate lint validates `gate_requirements.required_snippets` against the file in `skill_path`.
- Eval runner executes each case live via `codex exec` and then grades marker expectations on the captured response.
- For YAML eval suites, keep each case self-contained (`prompt` + `expected`) with no pre-generated response fixtures.
- `eval_name` is optional for YAML suites; if omitted, it is derived from the config file name.
- `cases` is required by schema and may be an empty array.
- Optional per-eval runtime knobs: `max_concurrency`, `codex_timeout_seconds`, `codex_sandbox`, `codex_model`, `codex_reasoning_effort`, `codex_extra_args`, `codex_isolation`, `codex_home_base_dir`.
- Runtime precedence is `env > suite YAML > /Users/jiri/agents/eval-config.toml > built-in defaults`.
- `EVAL_CODEX_HOME_BASE_DIR` overrides the configured base directory for isolated `CODEX_HOME` temp homes.
- For `eval_type: skill` with `codex_isolation: true`, the runner creates a fresh suite-local `CODEX_HOME`, copies minimal auth/state files, and symlinks the tested skill into that isolated home.
- Default `max_concurrency` is `3`, configurable globally in `/Users/jiri/agents/eval-config.toml` and overridable per suite YAML.
- Duration metadata is written into schema, gate, eval, suite, and repo-level result JSON files.
