---
name: worktree-isolation
description: Set up isolated git worktrees for two or more concurrently writing subagents with already-approved branches. Use only for active parallel writes; do not create worktrees for sequential or single-agent work.
---

# Worktree Isolation

Use worktrees only when isolation prevents a real branch collision. Keep the main workspace on the integration branch.

## Workflow

1. Confirm the small set of active writer tasks and their non-overlapping file ownership.
2. Create one worktree per approved branch at `.worktrees/<sub-issue>-<subtask-slug>`.
3. Bind exactly one writer to each worktree and one focused validation command.
4. Keep generated logs outside the repository.
5. Remove the worktree after the branch is integrated and the user no longer needs it.

## Output Contract

| Issue | Branch | Worktree | Owner | Validation |
| --- | --- | --- | --- | --- |
| <id> | `<sub-issue>-<subtask-slug>` | `.worktrees/<sub-issue>-<subtask-slug>` | <agent> | <focused command> |

## Gate Rules

- Do not share one worktree between active writers.
- Do not use this skill for review-only agents.
- Stop if ownership overlaps or the interface is not stable enough for parallel work.
