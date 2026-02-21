---
name: scope-to-acceptance
description: Convert problem statements into execution-ready scope, non-goals, acceptance criteria, assumptions, and dependency mapping.
metadata:
  short-description: PM scope and acceptance template
  tags:
    - pm
    - planning
    - requirements
    - governance
---

# Scope To Acceptance

Use this skill in Phase 1 to transform ambiguous requests into execution-ready scope.

## Role Scope

- Primary: PM
- Secondary reviewers: Tech Lead, Architect

## Use When

- Problem statement is broad or underspecified
- Multiple possible interpretations exist
- Teams need clear boundaries before issue decomposition

## Inputs Required

- User/business request
- Constraints (time, budget, platform, compliance)
- Known architecture constraints
- Existing pain points and success signal

## Output Quality Bar

Every acceptance criterion must be:

- Observable (someone can verify it)
- Binary (pass/fail)
- Testable (manual or automated)
- Scoped (ties to in-scope area)

## Workflow

1. Define the target outcome in one sentence.
2. Write explicit in-scope boundaries.
3. Write explicit non-goals.
4. Draft acceptance criteria with test signal.
5. Capture assumptions and unresolved questions.
6. Build dependency map with owners and risk.
7. Mark blockers that prevent issue breakdown.

## Dependency Classification

For each dependency, classify:

- Type: technical, product, legal, operational, external service
- Criticality: blocking, high, medium, low
- Owner: role or team
- Failure impact: delivery, quality, security, timeline

## Output Contract

- Outcome Statement:
- Scope (in):
- Non-goals (out):
- Acceptance Criteria:
- AC1:
- AC2:
- AC3:
- Assumptions:
- Open Questions:
- Dependencies:
- Blockers:
- Ready for Subtask Breakdown: yes/no

## Gate Rules

- No subtask issue creation before `Ready for Subtask Breakdown = yes`.
- If blockers exist, PM must route to Tech Lead with mitigation options.

## Anti-Patterns

- "Should work" style acceptance criteria
- Hidden non-goals
- Dependencies without owners
- Conflating assumptions with requirements

## Integrations

- Feed outputs into `gh-subtask-breakdown`.
- Use with `orchestration-scorekeeper` to anchor C/R/E evidence.
