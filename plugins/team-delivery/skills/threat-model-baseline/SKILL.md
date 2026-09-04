---
name: threat-model-baseline
description: Create a compact threat model for a changed trust boundary involving authentication, permissions, secrets, sensitive data, external execution, or network input. Use before implementing that boundary; do not use for unrelated local changes.
---

# Threat Model Baseline

## Workflow

1. Name the changed asset, entry point, trust boundary, and data exit.
2. Identify only plausible threats and their concrete mitigation or detection.
3. Stop on an unresolved critical threat; assign an owner for high risk.

## Required Output

| Boundary / asset | Threat | Risk | Mitigation / detection | Owner | Residual |
| --- | --- | --- | --- | --- | --- |
| <item> | <concrete threat> | low/medium/high/critical | <control> | <role> | <statement> |

## Gate Rules

- Do not use generic STRIDE filler without a changed boundary.
- No security or contract approval with an unresolved critical threat.
- Record accepted residual risk explicitly; never imply it from silence.
