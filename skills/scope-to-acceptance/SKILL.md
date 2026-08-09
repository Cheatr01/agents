---
name: scope-to-acceptance
description: Independently convert an ambiguous product or software request into a compact, testable scope and acceptance record. Use before engineering handoff when the request lacks a clear outcome, boundary, or success signal; this is not part of team-orchestrator execution.
---

# Scope To Acceptance

Use this before engineering orchestration, not inside it. Do not invoke it for a typo, a fully specified technical task, or to restate a product brief that already answers these questions.

## Workflow

1. Write the one-sentence user outcome.
2. Set the smallest in-scope boundary and explicit non-goals.
3. Define up to five observable acceptance criteria, each with its validation signal.
4. List only assumptions or dependencies that can block the increment.
5. Mark whether the task is ready to implement or needs a user decision.

## Output Contract

```
Outcome Statement: <one sentence>
Scope (in): <bounded list>
Non-goals (out): <bounded list>
Acceptance Criteria:
- AC1: <pass/fail signal>
- AC2: <pass/fail signal>
- AC3: <pass/fail signal, when applicable>
Assumptions: <only material assumptions>
Open Questions: <only blockers>
Dependencies: <owner + impact, if any>
Blockers: <none or decision needed>
Ready for Subtask Breakdown: yes/no
```

## Gate Rules

- Do not create a plan or subtask solely to answer an unresolved product decision.
- Keep acceptance criteria binary and tied to the current increment.
- If a prerequisite is unavailable, stop at the blocker instead of expanding scope.
