---
name: gh-subtask-breakdown
description: Decompose a bounded, user-approved multi-writer delivery increment into independently testable GitHub subtasks with ownership and dependencies. Use only when GitHub issues or parallel writers are explicitly required; do not use for a single-agent change.
---

# GitHub Subtask Breakdown

Create no more issues than can run independently. Prefer one issue and one branch for a bounded increment.

## Workflow

1. Confirm the parent issue or explicit user authorization to create one.
2. Create a subtask only when it has separate ownership, acceptance criteria, and a dependency boundary.
3. Keep a maximum of three active subtasks unless the user approves more.
4. Generate deterministic branch names: `<sub-issue>-<subtask-slug>`.
5. Return only the compact register; do not copy the full product brief into every issue.

## Output Contract

| Subtask | Owner | Acceptance | Depends on | Issue | Branch |
| --- | --- | --- | --- | --- | --- |
| <bounded task> | <one owner> | <test signal> | <none/id> | <id/url> | `<sub-issue>-<subtask-slug>` |

## Gate Rules

- Do not create vague review-only or speculative issues.
- Do not use GitHub as a prerequisite for a single-agent local change.
- Stop if the task cannot be independently tested or its boundary is unclear.
