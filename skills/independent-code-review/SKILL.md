---
name: independent-code-review
description: Independently review every complete code diff or pull request in bounded, batched rounds, checking task fit and material business-flow effects before fixes or reports are made.
---

# Independent Batched Code Review

Run this as the mandatory review gate for every increment that changes code, including a pull request review. It is not a substitute for tests or other applicable quality, security, or architecture gates. Do not use it for a no-code change.

## Independence and reviewer choice

- The reviewer must be a different agent from every agent that authored, edited, or directed the implementation under review. Never self-review.
- Give the reviewer a clean, bounded brief: the original task and acceptance criteria, non-goals, review range/base, and access to the final diff and relevant repository context. Do not give it an author's findings or proposed fixes before it reaches its own conclusion.
- Use Terra at `xhigh` reasoning by default; `high` is acceptable when the review budget requires it. For a large or cross-cutting review, use Sol at `high` when it fits the review cap. “Large” means the diff spans multiple modules, public interfaces, or a business-critical flow—not merely many generated lines.
- The reviewer only reviews. It must not edit code, suggest a partial fix while still inspecting, or turn a review assignment into an implementation assignment.

## Review scope

Review the complete final change set, not just the last fix or files named by the author. Establish the appropriate base for the task or PR, inspect every changed file in the `git diff`, and read unchanged call paths, tests, contracts, and configuration where needed to understand the effect.

Check at least:

- the complete diff against the task, acceptance criteria, stated scope, and non-goals;
- correctness, regressions, error and boundary paths, interfaces, tests, and relevant quality or security constraints; and
- important business flows affected by the change.

For a material business flow, compare the implementation with both the task's stated business intent and the prior behavior:

- If it contradicts the stated business intent, report a material finding.
- If the task implicitly entails a material business-flow change, emit a **business-flow notice**, clearly marked as informational rather than a finding. It asks the user to confirm that the intended flow is the one that changed. Do not fix it or treat it as a defect unless the user designates it as a finding.

## Batch protocol

An iteration is one complete inspection of the entire current diff. The initial review is iteration 1.

1. Inspect the whole review range before publishing, returning, or acting on any individual item. Accumulate all findings privately during the inspection.
2. After coverage is complete, emit one review bundle. Each actionable finding needs a priority, precise location, evidence/impact, and a concrete correction direction. Include the task-fit result, coverage/range, and any business-flow notices separately from findings.
3. Do not make fixes during review. Do not ask an implementation agent to fix the first finding before the remaining diff has been reviewed.
4. If the user explicitly asked to write findings directly to the pull request, the reviewer posts the complete bundle only after the review is complete: inline comments where a precise line exists and a final summary for cross-cutting findings and business-flow notices.
5. Otherwise, return the complete bundle to the orchestrator. The orchestrator records it in the task/delivery record and shows it to the user; it does not post to the pull request by default.
6. If the user explicitly asks to fix findings directly without recording them in the pull request, the orchestrator sends the complete batch to one or more non-reviewer implementation agents. They fix the batch together, then a reviewer re-runs this skill over the full updated diff. The reviewer never fixes its own findings.

Use this bundle shape; list `None` explicitly when a section is empty:

```text
Review round: <n>/5
Range and coverage: <base...head; all changed files reviewed>
Task fit: <meets / does not meet; short evidence>
Findings:
- [P0–P3] <title> — <file:line or cross-cutting scope>
  Evidence/impact: <why this is a real problem>
  Correction direction: <what must change>
Business-flow notices:
- <affected flow; observed change; user confirmation needed>
Decision: <clear / complete batch to fix / user decision required>
Review budget: <measured or estimated; spent; remaining>
```

Prioritize real, actionable defects. Do not pad the batch with style preferences, duplicate items, or speculative concerns.

## Iteration and token limits

- At most five complete review iterations may be run for one change set. After each repair batch, the next iteration reviews the full diff from its base again; it does not merely verify previously reported lines.
- If the fifth round is clear, the review gate passes. If it contains findings that need repair, or any further review would be needed, stop immediately and alert the user that the five-round limit was reached. Do not dispatch a sixth review or another repair batch without their direction.
- Before dispatching the first reviewer, set a review-token cap. Across all review rounds, measured reviewer consumption must not exceed the measured implementation consumption for the same increment. When measured consumption is unavailable, mark the cap `estimated`, set it no higher than the explicit implementation reserve, and keep both reserves within the total delivery budget. Use the smallest reviewer/model configuration that can still cover the whole diff.
- Track the cap after every round. If completing another full round would exceed it, stop and alert the user rather than silently spending more. The user may approve a new cap or take over.

The orchestrator may report a clean review, a batch of findings, or a required user decision only after the reviewer has completed coverage of that round.
