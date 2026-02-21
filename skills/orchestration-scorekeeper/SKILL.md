---
name: orchestration-scorekeeper
description: Compute and maintain consistent C/R/E delivery scoring, escalation thresholds, and escalation reason logs for Team Orchestrator runs.
metadata:
  short-description: C/R/E scoring and escalation log
  tags:
    - orchestration
    - governance
    - risk
    - planning
---

# Orchestration Scorekeeper

Use this skill when Tech Lead or PM needs consistent delivery scoring in Phase 0 and at any escalation point.

This skill is the canonical scoring source for Team Orchestrator. If another skill proposes a conflicting score, this skill wins.

## Role Scope

- Primary: Tech Lead, PM
- Secondary consumers: Architect, Security Reviewer, Quality Lead

## Use When

- Starting a new orchestration run (Phase 0)
- Scope expands or shrinks
- Contract/design freeze is violated or reopened
- New security/performance risk is discovered
- Before final governance gate (Phase 5)

## Inputs Required

- Task statement and intended outcome
- Current scope boundaries and non-goals
- Known architecture/contract constraints
- Data sensitivity and exposure context
- Current findings (quality, security, performance)

## Canonical Rubric

### Complexity (C)

1. Trivial edit, single file, no behavioral change
2. Small change, single component, clear boundary
3. Medium feature, 1-2 modules, moderate integration
4. Cross-module behavior and integration impact
5. Architectural shift, platform-wide implications

### Risk (R)

1. Safe internal change, easy rollback
2. Regression possible, moderate blast radius
3. Production impact likely if wrong
4. Security-sensitive or high reliability exposure
5. Compliance/critical system exposure

### Exposure (E)

1. Internal-only, non-customer-facing
2. Limited users/low business criticality
3. User-facing core workflow
4. Public API or external integration dependency
5. Public plus sensitive data path

## Tier Mapping

`Delivery Score = C * R * E`

- 1-10: Minimal Team Mode
- 11-30: Standard Team
- 31-60: Extended Team
- 61+: Full Governance Mode

## Required Execution

1. Score C, R, E using evidence from current scope.
2. Compute Delivery Score and map tier.
3. Compare against configured escalation threshold.
4. If tier crossed, produce mandatory escalation package:
- what changed
- why score changed
- which roles must be added
- which gates must be re-run
5. Append log entry to threshold history.

## Escalation Reason Taxonomy

Use one or more reason codes:

- `SCOPE_GROWTH`
- `CONTRACT_CHANGE`
- `DESIGN_CHANGE`
- `SECURITY_FINDING`
- `PERF_REGRESSION`
- `DATA_SENSITIVITY_CHANGE`
- `DEPENDENCY_RISK`

## Output Contract

Return exactly this block in every run:

- Task:
- C: <value> (<evidence>)
- R: <value> (<evidence>)
- E: <value> (<evidence>)
- Delivery Score:
- Tier:
- Escalation Threshold:
- Escalation Triggered: yes/no
- Reason Codes:
- Required Role Changes:
- Gates to Re-run:
- Score Log Entry:

## Score Log Format

`<timestamp> | C=<n> R=<n> E=<n> Score=<n> Tier=<name> Triggered=<yes/no> Reasons=<codes>`

## Gate Rules

- No implementation track starts without an initial score.
- No phase transition on tier change without an updated score log.
- No final acceptance without score revalidation.

## Anti-Patterns

- Scoring by intuition without evidence
- Keeping old score after scope shift
- Hiding escalation to preserve timeline
- Using inconsistent rubrics between runs

## Integrations

- Pair with `scope-to-acceptance` for better C/E calibration.
- Pair with `contract-drift-guard` to auto-trigger re-scoring.
- Pair with `security-gate-runbook` and `performance-regression-lab` for R updates.
