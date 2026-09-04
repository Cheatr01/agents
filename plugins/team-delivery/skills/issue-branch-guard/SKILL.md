---
name: issue-branch-guard
description: Verify issue-to-branch traceability before concurrent or GitHub-governed writes. Use only when the user requires GitHub traceability or when two or more writers are active; do not block a normal single-agent local change.
---

# Issue Branch Guard

This is an opt-in parallel-work safety check, not a universal precondition for writing files.

## Pre-Write Sequence

1. Confirm the assigned subtask issue and expected branch `<sub-issue>-<subtask-slug>`.
2. Verify that the active worktree is bound to that branch.
3. If the branch does not exist, create it from the named integration branch.
4. If the worktree is dirty with another task's changes, stop and report the conflict.
5. Record one `pass` or `blocked` line in the delivery ledger.

## Output Contract

```
Issue: <id/url>
Expected branch: <sub-issue>-<subtask-slug>
Current branch/worktree: <value>
Guard: pass/blocked
Reason: <one line>
```

## Gate Rules

- Do not apply this guard to a single-agent increment unless the user requested traceability.
- Never switch or create a branch over unowned dirty changes.
- A worker may modify only its assigned files while the guard is active.
