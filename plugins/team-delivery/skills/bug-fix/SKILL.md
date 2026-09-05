---
name: bug-fix
description: Investigate and repair a bounded software defect with adaptive evidence collection, an explicit root-cause gate, and a handoff into Team Delivery. Use for crashes, failing tests or CI jobs, regressions, and production defects; do not use for feature discovery or open-ended incident command.
---

# BugFix Orchestrator

Coordinate one defect from symptom to verified repair. Preserve the user's chosen coordinator model and reasoning effort; the model defaults below apply only to spawned subagents.

Honor the requested stopping point. A diagnosis-only request ends with the Root Cause Packet. A request to fix the defect continues through implementation and validation.

## Start With a Retrieval Decision

Before spawning anyone, inspect what the user already supplied and choose the cheapest path that can produce trustworthy evidence.

| Evidence shape | Retrieval owner | Model and effort |
| --- | --- | --- |
| One known, directly accessible artifact that the coordinator can inspect in one short operation, such as a GitHub Actions job URL, stack trace, or focused failing-test output | Coordinator directly; do not create a collector merely to open or summarize it | User-selected coordinator |
| Several routine sources, long logs, repository documentation, or artifacts that need collection and compression but little interpretation | `bugfix-evidence-collector` when registered; otherwise an `explorer` explicitly using `$bug-evidence-collector` | `gpt-5.6-luna`, `low` |
| Complex cloud navigation or queries, unfamiliar telemetry, cross-service/time-window correlation, or one incomplete Luna attempt | Same collector role with a stronger override | `gpt-5.6-terra`, `medium`; use `high` only when acquisition itself requires substantial reasoning |

Prefer direct retrieval when delegation overhead is greater than the retrieval. Prefer a collector when it can keep large, dispersed, or noisy evidence out of the coordinator's context. Do not make Luna guess at causality; upgrade acquisition to Terra when source selection or correlation requires real judgment. Do not repeat equivalent collection attempts.

Evidence collection is read-only. It may inspect logs, metrics, documentation, CI artifacts, and repository state, but it must not rerun jobs, change cloud configuration, edit code, or mutate production. Redact secrets and personal data; preserve source locations, timestamps, time zones, job or trace identifiers, and access gaps.

## Spawn the Evidence Collector

When a collector is justified, use `fork_turns: "none"` and give it only:

- the observed symptom and known time window;
- exact starting sources and allowed systems;
- the bounded retrieval question;
- redaction and no-mutation constraints; and
- this required output: the Evidence Packet defined by `$bug-evidence-collector`.

Set `task_name` to `bug_evidence`. Use `agent_type: "bugfix-evidence-collector"` when that configured role is available; otherwise use `agent_type: "explorer"`. Set the `model` and `reasoning_effort` fields from the selected retrieval row instead of inheriting the coordinator settings. The configured role defaults to Luna-low, so a complex acquisition must explicitly override it to Terra-medium/high.

Do not pass the whole conversation. Do not ask the collector to diagnose, propose a fix, edit files, or spawn more agents. While it runs, the coordinator may inspect a distinct local code path, but should not duplicate the same retrieval.

## Select the Investigator

Investigation begins only after the initial evidence is compact enough to hand off.

| Defect shape | Investigator | Model and effort |
| --- | --- | --- |
| Truly small and deterministic: one component, a focused reproducer, no concurrency, security, migration, or cross-service behavior, and a small evidence set | The current coordinator may investigate if it is already suitable, or spawn `bugfix-investigator` / `explorer` using `$bug-investigator` | `gpt-5.6-terra`, `xhigh` |
| Most defects with multiple plausible causes or non-trivial code paths | A separate investigator using `$bug-investigator` | `gpt-5.6-sol`, `medium` |
| Intermittent, concurrent, cross-service, stateful, production-only, security-sensitive, or repeatedly misdiagnosed defects | A separate investigator using `$bug-investigator` | `gpt-5.6-sol`, `high` |

For a spawned investigator, use `fork_turns: "none"`. Provide the original symptom, compact Evidence Packet, relevant repository paths or interfaces, constraints, and at most one safe reproduction command. Require a Root Cause Packet. Do not send the collector's speculation, the coordinator's preferred fix, or an unbounded raw log dump. The investigator must not implement the repair or spawn other agents.

Set `task_name` to `bug_investigation`. Use `agent_type: "bugfix-investigator"` when that configured role is available; otherwise use `agent_type: "explorer"`. Set `model` and `reasoning_effort` from the selected investigation row. The configured role deliberately defaults to Sol-high; override it to Sol-medium for an ordinary investigation or Terra-xhigh for the small deterministic case.

The investigator should be different from the evidence collector for non-trivial defects. The coordinator may combine retrieval and investigation only for the small deterministic case above.

## Root-Cause Gate

Do not launch implementation agents until the Root Cause Packet contains:

- a causal chain from trigger through faulty behavior to the observed symptom;
- source-linked evidence and a reproducible or otherwise discriminating signal;
- rejected alternatives that were genuinely plausible;
- confidence (`high`, `medium`, or `low`) and the remaining uncertainty;
- the smallest repair boundary and an explicit non-goal; and
- a validation plan that would fail before the repair and pass after it.

At `low` confidence, collect the named missing evidence or run one focused, safe experiment; do not start developers. At `medium` confidence, implementation may proceed only when its first step is a failing reproducer or another discriminating check that can invalidate the diagnosis. Do not turn an unexplained symptom into a speculative patch.

Stop for user input when progress needs production mutation, new external cost, access not already granted, risk acceptance, or a product decision.

## Repair Through Team Delivery

When the user requested a fix and the root-cause gate passes, convert the Root Cause Packet into the engineering brief expected by `$team-orchestrator`:

- technical outcome: remove the proven cause, not merely the visible symptom;
- scope: named components or files from the repair boundary;
- non-goal: behavior that must remain unchanged;
- validation: reproducer plus the smallest relevant regression checks; and
- constraints: compatibility, security, performance, rollout, or manual-system requirements.

Then follow `$team-orchestrator` for writer selection, ownership, implementation, validation, and mandatory independent code review. Reuse its delivery ledger for multi-turn or multi-agent work. Do not rerun product discovery, and do not reopen the diagnosis unless implementation evidence contradicts the Root Cause Packet.

If implementation contradicts the diagnosis, stop writers, preserve the new evidence, and return once to the investigator with the specific contradiction. Avoid a loop of speculative repair attempts.

## Compact Coordinator Record

Keep this state in the task or delivery ledger:

```text
Defect: <bounded symptom>
Retrieval: direct | Luna-low | Terra-medium/high — <reason>
Evidence: <packet status and source links>
Investigator: coordinator | Terra-xhigh | Sol-medium/high — <reason>
Root cause: <confidence and one-line causal statement, or pending>
Repair: <not authorized | blocked | Team Delivery status>
Contradiction budget: unused | used
```

Complete with the root cause, changed components, validation evidence, independent-review status when code changed, and explicit residual risk.
