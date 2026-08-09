---
name: orchestration-scorekeeper
description: Calculate and revalidate a compact C/R/E delivery score for a bounded software increment when a coordination, escalation, or release decision needs evidence. Do not use for trivial edits or as a reason to automatically add agents.
---

# Orchestration Scorekeeper

Use the score to choose validation and coordination intensity, not to manufacture process.

## Rubric

- **C (complexity):** 1 trivial/single-file; 2 bounded component; 3 one or two integrations; 4 cross-module; 5 architectural/platform change.
- **R (risk):** 1 easy rollback; 2 regression possible; 3 production workflow; 4 security/reliability sensitive; 5 compliance/critical.
- **E (exposure):** 1 internal; 2 limited users; 3 user-facing; 4 public integration; 5 public and sensitive data.

`Delivery Score = C × R × E`

| Score | Guidance |
| --- | --- |
| 1–10 | One agent; focused check; no formal governance by default |
| 11–30 | Add one targeted review or gate only when its trigger is present |
| 31–60 | Use a short plan; consider bounded parallelism after an interface is stable |
| 61+ | Require explicit architecture/security/release planning before writes |

## Required Execution

1. State one evidence phrase for each factor.
2. Choose only the required role or gate, if any.
3. Re-score only on material scope, interface, data-sensitivity, security, or measured-performance change.
4. Append one short line to the external delivery ledger; do not replay prior score reports.

## Output Contract

```
Task: <bounded increment>
C: <n> (<evidence>)
R: <n> (<evidence>)
E: <n> (<evidence>)
Delivery Score: <n> — <tier>
Change since last score: <none or reason>
Required addition: <none or one role/gate>
Score Log Entry: <timestamp> C=<n> R=<n> E=<n> score=<n> reason=<none|code>
```

## Gate Rules

- Do not score a typo-only or clearly bounded mechanical edit.
- A tier increase does not itself require a larger team; name the concrete trigger.
- Re-score before accepting a high-risk release decision.
