---
name: gh-subtask-breakdown
description: Split a parent task into architecture-driven subtasks and create linked GitHub issues with ownership, dependencies, acceptance criteria, and deterministic branch naming.
metadata:
  short-description: Architect subtask decomposition with GitHub issue creation
  tags:
    - github
    - architecture
    - planning
    - orchestration
---

# GitHub Subtask Breakdown

Use this skill when an Architect must decompose a parent task into executable subtasks and create GitHub issues.

## Inputs Required

- Parent task title and scope
- Parent issue id (or explicit instruction to create one)
- Initial role assignment per subtask
- Target repository (`owner/repo`)

## Workflow

1. Produce a subtask list.
   - Each subtask must contain:
     - title
     - owner role
     - acceptance criteria
     - dependencies
     - risk notes
2. Create one GitHub issue per subtask.
3. Link subtasks to the parent issue.
   - Prefer native parent/sub-issue linking.
   - If unavailable, add explicit references in issue body.
4. Generate deterministic branch names for each subtask:
   - `codex/<parent-issue>-<task-slug>/<sub-issue>-<subtask-slug>`
5. Return a compact issue register.

## Output Format

- Parent issue id/url
- Subtask table:
  - subtask title
  - issue id/url
  - owner role
  - dependencies
  - branch name
- Escalation notes for blocked or ambiguous subtasks

## Guardrails

- Do not create vague subtasks (must be independently testable/reviewable).
- Do not leave acceptance criteria empty.
- Do not assign multiple primary owner roles to one subtask.
- If issue creation fails, stop and report exact failure before proceeding.
