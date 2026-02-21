---
name: security-gate-runbook
description: Run continuous and final security gating with severity rubric, approval criteria, and explicit risk acceptance workflow.
metadata:
  short-description: Security gate criteria and risk acceptance
  tags:
    - security
    - governance
    - compliance
    - review
---

# Security Gate Runbook

Use this skill continuously and at Phase 5 for formal security gate decisions.

## Role Scope

- Primary: Security Reviewer
- Approvers for risk acceptance: Tech Lead plus designated risk owner

## Severity Rubric

- `CRITICAL`: practical exploit with severe impact
- `HIGH`: strong exploitability or major impact
- `MEDIUM`: material risk with constrained exploitability
- `LOW`: minor risk with limited impact

## Approval Criteria

- No open critical findings
- No open high findings unless explicitly approved by exception policy
- Medium findings require either remediation or documented time-bound risk acceptance
- Low findings must be tracked with owner

## Workflow

1. Aggregate findings from code, config, dependencies, and runtime behavior.
2. Score and classify each finding.
3. Mark blockers vs non-blockers.
4. Execute or request remediation where needed.
5. If accepting risk, create explicit acceptance record.
6. Publish gate decision.

## Risk Acceptance Record

Must include:

- Finding ID
- Scope impacted
- Approver
- Owner
- Expiry date
- Monitoring/detection controls
- Exit criteria

## Output Contract

- Findings by Severity:
- Blocking Findings:
- Remediation Status:
- Risk Acceptance Records:
- Security Gate Decision: APPROVE/REJECT/CONDITIONAL
- Conditions (if conditional):

## Gate Rules

- No implicit risk acceptance.
- Conditional approvals must have expiry and owner.
- Expired risk acceptance automatically reopens gate.

## Anti-Patterns

- Marking unresolved high-risk findings as low priority
- Accepting risk without monitoring controls
- One-time audit mindset instead of continuous gating

## Integrations

- Pair with `threat-model-baseline` in Phase 2.
- Pair with `integration-merge-governor` for final merge policy.
