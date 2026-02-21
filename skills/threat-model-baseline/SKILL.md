---
name: threat-model-baseline
description: Build a lightweight STRIDE-like threat model with data flow, mitigations, and residual risk statement for Team Orchestrator Phase 2.
metadata:
  short-description: Lightweight threat model baseline
  tags:
    - security
    - architecture
    - risk
    - governance
---

# Threat Model Baseline

Use this skill in Phase 2 to produce an actionable, lightweight threat baseline.

## Role Scope

- Primary: Security Reviewer
- Co-author: Architect

## Method

Use a lightweight STRIDE-like pass over explicit trust boundaries and data flows.

## Inputs Required

- Architecture context and component boundaries
- Data flow path (ingress, processing, storage, egress)
- Auth and authorization model
- Sensitive data classification
- External dependencies and trust assumptions

## Workflow

1. Inventory assets and trust boundaries.
2. Map critical data flows.
3. Identify threats per STRIDE category for each boundary/flow.
4. Score each threat using likelihood and impact.
5. Define mitigations and detection controls.
6. State residual risk and acceptance needs.

## Risk Scoring

- Likelihood: 1 (unlikely) to 5 (probable)
- Impact: 1 (low) to 5 (severe)
- Risk Score: `Likelihood * Impact`

Risk classes:

- 1-4: Low
- 5-9: Medium
- 10-15: High
- 16-25: Critical

## Required Output

- System Boundaries:
- Data Flow Summary:
- Threat Register:
- Threat ID:
- Category:
- Boundary/Flow:
- Likelihood:
- Impact:
- Score:
- Mitigation:
- Detection:
- Owner:
- Residual Risk Statement:
- Approval Requirement:

## Gate Rules

- No Contract Freeze if critical threats are unresolved.
- High threats require mitigation plan and owner before freeze.
- Medium threats may proceed only with explicit residual risk note.

## Anti-Patterns

- Threat list without boundary context
- Mitigation without owner
- Implicit risk acceptance
- Missing auth abuse cases

## Integrations

- Pair with `contract-freeze-kit` for freeze verdict.
- Pair with `security-gate-runbook` for ongoing gating.
