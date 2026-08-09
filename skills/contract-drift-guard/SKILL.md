---
name: contract-drift-guard
description: Compare a deliberately frozen shared API, persisted schema, or cross-writer interface against implementation and decide whether a re-freeze is needed. Use only when such a contract exists.
---

# Contract Drift Guard

## Workflow

1. Read the frozen contract and only the changed interface surfaces.
2. Classify each evidence-backed difference: `none`, `additive`, `major`, or `breaking`.
3. For `major` or `breaking`, stop the affected integration and request the smallest needed architect decision.
4. Record the disposition in the delivery ledger.

## Output Contract

```
Drift: none/additive/major/breaking
Evidence: <contract field or behaviour>
Consumer impact: <none or concrete>
Action: <continue / update contract / re-freeze>
```

## Gate Rules

- Do not run this check for private local refactors.
- An additive change still needs consumer awareness when multiple writers depend on it.
- A breaking change cannot be merged before an explicit contract decision.
