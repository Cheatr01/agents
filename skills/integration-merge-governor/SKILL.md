---
name: integration-merge-governor
description: Govern final integration in Phase 6 with merge order, required checks, conflict policy, and merge readiness checklist.
metadata:
  short-description: Final integration merge governance
  tags:
    - git
    - integration
    - release
    - governance
---

# Integration Merge Governor

Use this skill in Phase 6 to drive deterministic and auditable final integration.

## Role Scope

- Primary: Tech Lead
- Required signals: Security Reviewer and Quality Lead decisions

## Inputs Required

- Integration branch (`codex/<parent-issue>-<task-slug>`)
- Candidate subtask branches
- Dependency graph between subtasks
- Required CI checks and gate outcomes

## Merge Ordering Strategy

1. Build dependency-aware merge order (topological).
2. Within same dependency level, merge lower-risk branches first.
3. Merge branches with high conflict probability earlier.

## Required Checks Per Branch

- Linked subtask issue exists
- Branch naming policy compliance
- CI checks green
- Security gate status acceptable
- Quality gate status acceptable
- No unresolved high-risk findings

## Conflict Policy

- Resolve conflicts on subtask branch first.
- Re-run required checks after conflict resolution.
- If conflict changes behavior materially, request targeted review.

## Final Readiness Checklist

- All mandatory reviews approved
- Security gate: APPROVE or valid CONDITIONAL
- Quality gate: PASS
- Traceability check: PASS
- Score revalidation completed

## Output Contract

- Planned Merge Order:
- Branch Check Status:
- Conflict Notes:
- Gate Summary:
- Final Readiness: READY/NOT_READY
- Blockers:

## Gate Rules

- No direct merge to integration branch without full checks.
- Fail fast on traceability, security, or quality gate failure.

## Anti-Patterns

- Merge order based on convenience only
- Manual cherry-picking without audit trail
- Ignoring post-conflict verification

## Integrations

- Pair with `quality-gate-matrix` and `security-gate-runbook`.
- Pair with `issue-branch-guard` and `worktree-isolation` for branch hygiene.
