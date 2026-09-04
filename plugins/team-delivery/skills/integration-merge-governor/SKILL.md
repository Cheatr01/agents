---
name: integration-merge-governor
description: Integrate and verify two or more completed parallel branches with a minimal merge order and final evidence record. Use only after multi-branch work; do not add a governance phase for a single-branch increment.
---

# Integration Merge Governor

## Merge Ordering Strategy

1. Merge the branch that supplies a dependency first.
2. Then merge lower-conflict branches.
3. After a conflict changes behaviour, run only the affected focused check.
4. Run the full suite once after all intended branches are integrated.

## Output Contract

```
Merge order: <branch list>
Per-branch evidence: <issue, focused check, review status>
Integration evidence: <full suite/build once>
Conflicts: <none or short disposition>
Readiness: ready/not ready
```

## Gate Rules

- Do not merge a branch without its stated acceptance evidence.
- Do not repeat green full-suite runs without a new integration change.
- Escalate only a material conflict, security finding, or interface change.
