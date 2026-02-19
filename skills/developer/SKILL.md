---
name: developer
description: End-to-end delivery workflow for software tasks with explicit role stages: create a task-based branch first, perform tech lead planning and handoff, implement as developer, build and run unit and integration tests as automation tester, fix issues from technical review, fix issues from security review, and finish with final tech lead acceptance. Use when the user asks for complete delivery with planning, implementation, testing, reviews, and final quality sign-off.
---

# Developer Skill

Follow this sequence exactly. Do not skip stages unless the user explicitly asks to skip them.

## 1) Create Branch First

1. Resolve the work item identifier from the user request (`GitHub issue`, `Jira`, or equivalent).
2. Create the branch before analysis or code edits.
3. Use branch name format:
`codex/<task-id>-<short-kebab-summary>`
4. If no task identifier exists, create one in the requested tracker first.
5. Report the created branch name.

## 2) Tech Lead Stage: Plan and Handoff

Produce an implementation plan that is ready for execution by another agent.

Required output:
1. Problem statement and scope boundaries.
2. Assumptions and open questions.
3. Architecture and design decisions.
4. PR-level execution plan:
- Split work into pull-request-sized steps.
- Keep each step independently reviewable and testable.
5. Risks and mitigations.
6. Definition of done:
- Functional criteria.
- Test criteria.
- Documentation criteria.

Handoff package format:
1. `Context`
2. `Plan (PR-sized)`
3. `Acceptance Criteria`
4. `Risks`
5. `Execution Notes`

## 3) Developer Stage: Implement

Implement the solution according to the approved plan.

Execution rules:
1. Read repository instructions first (`AGENTS.md` and module-specific guidelines).
2. Keep changes minimal and focused on the task scope.
3. Update code, configuration, and docs affected by the change.
4. Add or update tests together with code changes.
5. Document key tradeoffs in commit/PR notes.

Implementation checklist:
1. Feature behavior matches acceptance criteria.
2. Error handling is explicit and deterministic.
3. Backward compatibility impact is assessed.
4. Observability impact is assessed (logs/metrics/traces if relevant).

## 4) Automation Tester Stage: Unit + Integration Coverage

Prepare and execute a complete automated test set for changed behavior.

Required coverage:
1. Unit tests for core logic and edge cases.
2. Integration tests for cross-component behavior.
3. Negative-path tests for validation and failure handling.
4. Regression tests for previously fixed behavior in touched areas.

Required test report:
1. Tests added/updated.
2. Commands executed.
3. Pass/fail summary.
4. Remaining gaps and rationale.

## 5) Technical Reviewer Stage

Perform a technical review with defect-finding priority.

Review focus:
1. Correctness and behavioral regressions.
2. Code quality and maintainability.
3. Test completeness and reliability.
4. Performance and scalability implications.

Actions:
1. Log findings with severity and file references.
2. Fix confirmed issues.
3. Re-run relevant tests after fixes.
4. Update notes with what changed.

## 6) Security Reviewer Stage

Perform a focused security review and remediate findings.

Review focus:
1. Input validation and unsafe parsing.
2. Authentication/authorization paths.
3. Secret handling and sensitive data exposure.
4. Injection vectors and dependency risks.
5. Logging of sensitive data.

Actions:
1. Record findings with severity and exploitability context.
2. Fix confirmed security issues.
3. Re-run security-relevant tests and affected automated tests.
4. Document residual risk if any risk remains.

## 7) Tech Lead Final Acceptance

Verify final delivery quality against the original plan.

Final gate checklist:
1. All planned PR-sized deliverables are complete or explicitly re-scoped.
2. Acceptance criteria are satisfied.
3. Unit and integration tests pass for the implemented scope.
4. Technical and security review findings are resolved or explicitly accepted with rationale.
5. Documentation is updated for behavior/architecture changes.

Final handoff summary format:
1. `Delivered`
2. `Validated`
3. `Findings Resolved`
4. `Residual Risks`
5. `Ready for PR / Ready for Merge`
