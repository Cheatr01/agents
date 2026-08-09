---
name: contract-freeze-kit
description: Make a short readiness decision for a changed shared API, event, persisted schema, or interface used by parallel writers. Use before parallel implementation or a public contract change; do not use for private implementation details.
---

# Contract Freeze Kit

## Freeze Checklist

- Owner and consumers are named.
- Input/output or schema constraints are explicit.
- Error and authorization semantics are explicit when applicable.
- Compatibility or migration rule is explicit when existing consumers exist.
- One success and one relevant failure example exist.

## Output Contract

```
Contract: <name and owner>
Consumers: <list>
Checklist gaps: <none or compact list>
Compatibility: <not applicable / rule>
Verdict: READY / CONDITIONAL / NOT_READY
Required action: <none or owner + decision>
```

## Gate Rules

- Do not freeze a private function merely to satisfy process.
- `CONDITIONAL` is only for a non-breaking documentation gap with an owner.
- A breaking post-freeze change requires an explicit updated decision.
