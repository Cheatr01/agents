---
name: issue-branch-guard
description: Enforce pre-write discipline by requiring an assigned GitHub subtask issue and matching branch checkout before any file modifications.
metadata:
  short-description: Issue-to-branch pre-write guard
  tags:
    - git
    - github
    - governance
    - workflow
---

# Issue Branch Guard

Use this skill for any role that will write to disk.

## Rule

No write is allowed before:

1. Assigned subtask issue is known.
2. Matching branch is checked out:
   - `codex/<parent-issue>-<task-slug>/<sub-issue>-<subtask-slug>`

## Pre-Write Sequence

1. Confirm assigned parent issue and sub-issue id.
2. Compute expected branch name from issues + slugs.
3. Check current branch.
4. If branch is missing:
   - create it from integration branch.
5. If current branch is different:
   - stop and switch to expected branch.
6. Only then modify files.

## Validation Checks

- Branch contains assigned sub-issue id.
- Branch path starts with parent issue + task slug.
- Commit scope matches the assigned subtask boundaries.

## Failure Handling

- Missing issue id: stop and escalate to Architect/Tech Lead.
- Naming collision: stop and request normalized slug.
- Wrong branch with pending changes: stop and escalate (do not continue writing).

## Output

- Assigned issue id(s)
- Current branch and expected branch
- Guard status: `pass` or `blocked`
- Reason and escalation target if blocked
