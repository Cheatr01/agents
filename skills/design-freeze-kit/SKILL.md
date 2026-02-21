---
name: design-freeze-kit
description: Define and validate design freeze deliverables including token schema, naming rules, component inventory, accessibility baseline, and migration/versioning notes.
metadata:
  short-description: Design freeze package for web/app
  tags:
    - design-system
    - frontend
    - accessibility
    - governance
---

# Design Freeze Kit

Use this skill in Phase 2.5 to formalize design-system contracts before visual implementation.

## Role Scope

- Primary: Web Designer, App Designer
- Implementation partner: Frontend Engineer

## Inputs Required

- UI scope for this delivery
- Existing token/system baseline
- Component usage inventory
- Accessibility requirements

## Required Deliverables

### Token Schema

Must include at least:

- Color tokens (semantic and state)
- Typography tokens
- Spacing/size tokens
- Radius/elevation tokens
- Motion tokens

### Naming Rules

- Stable token naming grammar
- Alias and deprecation policy
- Reserved naming prefixes

### Component Inventory

- Component name
- Variant list
- States
- Usage boundaries
- Owner role

### Accessibility Baseline

- Focus visibility policy
- Contrast targets
- Keyboard interaction expectations
- Semantic and ARIA expectations

### Versioning and Migration

- Design-system version tag
- Breaking token/component policy
- Migration note for changed contracts

## Workflow

1. Normalize token taxonomy.
2. Lock naming grammar.
3. Finalize component inventory and ownership.
4. Validate accessibility baseline for key surfaces.
5. Publish version + migration notes.
6. Issue freeze verdict.

## Output Contract

- Token Schema:
- Naming Rules:
- Component Inventory:
- Accessibility Baseline:
- Version:
- Migration Notes:
- Freeze Verdict: READY/CONDITIONAL/NOT_READY

## Gate Rules

- No FE visual implementation before `READY`.
- `CONDITIONAL` allowed only for non-breaking documentation gaps.
- Breaking token changes after freeze require version bump and migration note.

## Anti-Patterns

- Raw hex/hardcoded spacing in implementation path
- Ambiguous token naming
- Components without ownership
- Accessibility as deferred work

## Integrations

- Pair with `issue-branch-guard` so design changes stay tied to subtask branches.
