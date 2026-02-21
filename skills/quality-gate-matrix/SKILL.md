---
name: quality-gate-matrix
description: Define and execute a quality gate matrix across unit, integration, negative-path, and regression testing with explicit thresholds and gate decisions.
metadata:
  short-description: Quality matrix and release gate decision
  tags:
    - qa
    - testing
    - governance
    - release
---

# Quality Gate Matrix

Use this skill in Phase 4 and Phase 5 to produce a defensible quality gate decision.

## Role Scope

- Primary: Quality Lead
- Execution: Quality Engineer

## Inputs Required

- Changed areas and risk tier
- Acceptance criteria
- Existing test suites and coverage
- Known defect history in touched modules

## Matrix Axes

- Unit tests
- Integration tests
- Negative-path tests
- Regression tests

## Threshold Policy

Set thresholds by risk tier:

- Minimal tier: critical path coverage + smoke regression
- Standard tier: moderate path and error coverage
- Extended/full governance tiers: full critical path, negative-path, and regression coverage with explicit gap rationale

## Workflow

1. Build matrix by changed area and risk.
2. Define required tests and thresholds per axis.
3. Execute tests and collect results.
4. Triage failures by severity and user impact.
5. Publish gate decision: pass/fail/blocked.

## Output Contract

- Test Matrix:
- Area:
- Unit:
- Integration:
- Negative-path:
- Regression:
- Threshold:
- Result:
- Failures:
- Coverage Gaps:
- Risk Statement:
- Gate Decision: PASS/FAIL/BLOCKED
- Required Follow-ups:

## Gate Rules

- No `PASS` with unresolved high-impact failures.
- Any accepted gap must include owner and due date.
- Re-run impacted suites after every fix to gate-blocking defects.

## Anti-Patterns

- Coverage percentage without scenario quality
- Skipping negative paths for user-facing changes
- Releasing with untriaged flaky failures

## Integrations

- Pair with `integration-merge-governor` for final readiness.
- Pair with `orchestration-scorekeeper` if failures increase risk tier.
