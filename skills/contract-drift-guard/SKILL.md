---
name: contract-drift-guard
description: Detect and manage API contract drift between frontend and backend, including re-freeze triggers and required escalation flow for breaking changes.
metadata:
  short-description: FE/BE contract drift detection and re-freeze rules
  tags:
    - backend
    - frontend
    - api
    - governance
---

# Contract Drift Guard

Use this skill in Phase 3 to detect and control drift between frozen contract and implementation.

## Role Scope

- Primary: Backend Engineer, Frontend Engineer
- Gate owner: Tech Lead

## Drift Sources

- API path/method mismatch
- Schema mismatch (field added, removed, type changed)
- Error semantics changed
- Auth requirement changed
- Versioning rule violated

## Detection Inputs

- Frozen contract reference
- Current BE implementation behavior
- Current FE integration assumptions
- Failing integration or contract tests

## Drift Classification

- `NONE`: no contract-impacting difference
- `MINOR`: non-breaking additive drift
- `MAJOR`: potentially breaking drift
- `BREAKING`: confirmed consumer-impacting drift

## Workflow

1. Compare frozen contract against current BE and FE behavior.
2. Record every detected drift item with evidence.
3. Classify drift severity.
4. For `MAJOR` and `BREAKING`, notify Tech Lead and Architect.
5. For `BREAKING`, trigger mandatory re-freeze flow.

## Re-Freeze Trigger Rules

Trigger re-freeze if any is true:

- Existing consumers would fail with no code changes
- Error handling contract changed materially
- Auth behavior changed (required scopes/roles)
- Versioning constraints violated

## Output Contract

- Drift Detected: yes/no
- Drift Register:
- ID:
- Type:
- Evidence:
- Severity:
- Consumer Impact:
- Re-Freeze Required: yes/no
- Escalation Targets:
- Immediate Actions:

## Gate Rules

- No merge for `BREAKING` drift before re-freeze approval.
- `MAJOR` drift requires explicit Tech Lead disposition.
- Every drift entry must link to issue/branch context.

## Anti-Patterns

- Treating runtime "works on my machine" as contract compliance
- Silent schema evolution
- Ignoring FE workaround patches as drift signal

## Integrations

- Pair with `contract-freeze-kit` for re-freeze review.
- Pair with `orchestration-scorekeeper` to update risk tier.
