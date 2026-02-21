---
name: worktree-isolation
description: Run parallel subagent execution safely by assigning each subtask branch to its own git worktree, preventing branch/context collisions.
metadata:
  short-description: Parallel subtask isolation with git worktrees
  tags:
    - git
    - worktree
    - parallelism
    - orchestration
---

# Worktree Isolation

Use this skill when multiple subagents run in parallel on different subtasks.

## Objective

Ensure each subtask has an isolated working directory bound to one branch.

## Inputs Required

- Repository root path
- Integration branch:
  - `codex/<parent-issue>-<task-slug>`
- Subtask branches list:
  - `codex/<parent-issue>-<task-slug>/<sub-issue>-<subtask-slug>`

## Workflow

1. Keep integration branch in main workspace root.
2. Create one worktree per subtask branch under a deterministic folder:
   - `.worktrees/<sub-issue>-<subtask-slug>`
3. Assign exactly one subagent per worktree.
4. Require each subagent to run all writes and checks inside its assigned worktree.
5. Merge subtask branches back to integration branch only after role gates pass.

## Guardrails

- Never use one worktree for multiple active subtask branches.
- Never commit subtask work on integration branch.
- If worktree branch diverges from assigned issue, pause and rebind.

## Output Format

- Worktree map table:
  - sub-issue id
  - branch
  - worktree path
  - assigned role/subagent
- Isolation status:
  - `ready`, `blocked`, or `rebind required`
