---
name: quality-gate-matrix
description: Select the smallest sufficient automated and manual validation set for a changed software increment and record a release decision. Use when regression risk is non-obvious or a release needs explicit evidence; do not use to rerun every suite after every edit.
---

# Quality Gate Matrix

## Workflow

1. Map each changed behaviour to one acceptance criterion and one validation signal.
2. Select focused unit, integration, negative-path, regression, build/package, and manual checks only where applicable.
3. Let each worker run its focused check once after its final code change.
4. After integration, run the full suite once; re-run only affected checks after later fixes.
5. Save verbose output outside context and report command, status, duration, and failure count only.

## Output Contract

| Behaviour | Required evidence | Owner | Status | Gap / rationale |
| --- | --- | --- | --- | --- |
| <AC> | <focused/full/manual> | <role> | pass/fail/not run | <one line> |

`Gate Decision: PASS / FAIL / BLOCKED`

## Gate Rules

- Do not run an equivalent green suite twice without a code or integration change.
- A manual or hardware requirement remains `not run` until someone performs it.
- A failing critical-path check blocks release; state any accepted gap and owner.
