---
name: design-freeze-kit
description: Define a minimal, stable design-system decision for reusable tokens or components that multiple UI changes depend on. Use before parallel visual implementation or a design-system breaking change; do not use for a local UI tweak.
---

# Design Freeze Kit

## Required Deliverables

- Affected token/component names and owner.
- States and accessibility expectation for the changed reusable surface.
- Compatibility or migration note if existing consumers change.

## Output Contract

```
Reusable surface: <tokens/components>
Accessibility: <focus, semantics, contrast as applicable>
Compatibility: <not applicable / migration>
Verdict: READY / CONDITIONAL / NOT_READY
```

## Gate Rules

- A local layout adjustment can proceed without this freeze.
- Do not require a version bump for a non-breaking internal addition.
- A breaking reusable token/component change needs a migration note before parallel adoption.
