---
name: team-orchestrator
description: Plan and run a bounded engineering implementation increment when the user explicitly asks for multi-agent coding coordination, role assignment, or delivery governance. Require an engineering-ready brief; do not perform product discovery, requirements analysis, or roadmap planning.
---

# Lean Engineering Delivery Orchestrator

Deliver one bounded engineering increment: one implementation milestone or at most three tightly coupled coding issues. Do not turn a whole roadmap into one thread.

## Engineering-Brief Preflight

Accept work only when the request supplies all of these:

- technical outcome or defect to change;
- scoped components, files, or interface boundary;
- explicit non-goal or boundary;
- observable validation signal; and
- applicable constraints (platform, compatibility, security, performance).

Do not infer product intent, decide user outcomes, or turn an ambiguous feature request into a technical plan. If a requirement is missing, stop with:

```
Engineering brief required
Missing: <items>
Needed next: <one concise technical decision or an authoritative brief>
```

Product/discovery skills may prepare that brief separately, but are not a phase or dependency of this orchestrator.

## Default Operating Mode

- Use one lead agent and one branch unless parallel work has a clear dependency boundary.
- Use Terra for routine implementation, inspection, Git operations, and test coordination. Reserve Sol for an architecture decision, a security decision, or a large independent code review.
- Create an independent reviewer for every increment that changes code. The reviewer is mandatory even for a small diff, must not have authored, edited, or directed the implementation, and follows `independent-code-review`. In the current Codex environment, respect the platform's delegation rules.
- When subagents are authorized, use at most two writers and one independent reviewer. Give every subagent `fork_turns: none` and only: objective, owned files, relevant interfaces, constraints, and one validation command. For the reviewer also provide the original task, non-goals, complete diff range, and review-token cap—never the implementer's conclusions or proposed fixes.
- Keep a short external delivery ledger in the repository or task artifact. Use `references/delivery-ledger.md` when creating one; do not reconstruct state from long thread history.

## Triage and Budget

Score only when coordination or a gate decision is needed. Use `C × R × E` from `orchestration-scorekeeper`, but treat the result as validation intensity—not a mandatory team size.

Set a token budget before delegating. Use the platform's actual token counter when it is available; otherwise label it `estimated` and enforce the proxy limits in `references/delivery-budget.md`. Never claim an estimate is measured usage.

| Condition | Default delivery shape |
| --- | --- |
| C/R/E all low; one bounded change | One agent, focused validation, independent code review |
| One real interface, UI, or regression risk | Lead plus an independent reviewer and, if needed, one targeted specialist |
| Independent file areas with a frozen interface | Up to two writers in isolated worktrees |
| Auth, sensitive data, public API, migration, or architectural change | Add the relevant architecture/security gate before implementation |

State the following compact plan before writing:

```
Increment: <one milestone or 1–3 linked issues>
Scope / non-goal: <one line each>
Risk: C=<n> R=<n> E=<n>, only if scored
Token budget: <measured or estimated> <limit>; spent=<value or unavailable>
Agents: <names and bounded ownership, or none>
Gates: <only gates triggered by this change>
Validation budget: worker=<focused>; integration=<once>; manual=<needed/not needed>
Stop condition: <what requires user input or ends the increment>
```

Do not repeat the full plan after every step. Update it only when scope, ownership, or risk changes.

## Gate Selection

Load exactly the needed supporting skill; do not load every governance skill.

- `contract-freeze-kit` and `contract-drift-guard`: a shared/public API, persisted schema, or multi-writer interface changes.
- `design-freeze-kit`: reusable design tokens/components change; not for a local UI adjustment.
- `threat-model-baseline` and `security-gate-runbook`: auth, secrets, permissions, sensitive data, external execution, or a material security finding is involved.
- `quality-gate-matrix`: the changed behaviour has non-obvious regression risk or a release decision needs evidence.
- `performance-regression-lab`: an SLO, benchmark, or observed regression exists.
- `independent-code-review`: mandatory after every code diff. It is a separate, batch-only review loop with its own five-round and token limits; do not replace it with lead self-review.
- `gh-subtask-breakdown`, `issue-branch-guard`, `worktree-isolation`, and `integration-merge-governor`: only for user-requested GitHub traceability or two or more concurrent writers.

## Execution and Validation Budget

1. Implement the smallest vertical slice that proves the user outcome.
2. Each writer runs one focused check after its last code change.
3. After integration, run the full suite once and packaging/build once when relevant. Do not repeat equivalent green runs.
4. Run `independent-code-review` against the complete diff. It reports all findings as one batch; fixes, if requested, are also one batch and require a new full-diff review round.
5. When the project has a required UI, hardware, permission, or external-system check, run that project's manual smoke gate immediately after the vertical slice.
6. Mark every capability `automated`, `packaged`, `manual`, or `not tested`. Never infer manual success from unit tests.

Use `scripts/run-compact.sh <label> [--history <path>] -- <command ...>` for verbose checks. It writes the full log to a private temporary file and returns only a status summary. With `--history`, it warns before repeating an identical successful label. Never print environment values or unredacted logs.

## Escalation and Stop Rules

Re-score and add only the missing expertise when a new auth/data boundary, breaking interface, material defect, or measured regression appears. Do not re-run discovery or all freezes merely because any file changed. After a code-review repair batch, re-run the mandatory independent review over the complete diff as specified by `independent-code-review`; stop at its five-round or review-token limit and alert the user.

Stop and ask the user when a decision changes product scope, external cost, production state, or risk acceptance. Stop at a required manual hardware gate until the user can perform it.

## Completion Record

Return a compact handoff:

```
Outcome: <done / blocked>
Changed: <files or components>
Evidence: <focused/full/build/manual/review-round status>
Residual risk: <none or explicit>
Next increment: <one bounded next step, if any>
```
