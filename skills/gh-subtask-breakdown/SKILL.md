---
name: gh-subtask-breakdown
description: Create or reorganize a bounded GitHub issue hierarchy with epics, native sub-issues, milestones, labels, dependencies, and traceable branches. Use when the user asks to create, break down, or maintain GitHub tasks, epics, subtasks, or milestone work; do not use for a single-agent local change.
---

# GitHub Epic and Sub-issue Breakdown

Use GitHub's native parent/sub-issue relationships. Do not emulate a hierarchy
with body checklists, cross-links, or title prefixes.

## Workflow

1. Confirm user authorization, the GitHub repository, and the intended milestone.
   Verify `gh auth status` before every GitHub write. If a sandboxed check appears
   unauthenticated, retry it with escalated access before asking the user to log in.
2. Inspect the repository's existing milestones and labels. If the work belongs
   to a milestone, resolve that milestone first; create it only when the user has
   asked for it or clearly authorized its creation.
3. Classify the work:
   - Use one normal issue for a bounded change with no independently deliverable children.
   - Use one top-level **epic** when the work has two or more independently
     testable child tasks. Label that issue `EPIC`.
   - Create a child issue only when it has separate scope, acceptance criteria,
     and a meaningful dependency or ownership boundary. Do not create review-only
     or speculative child issues.
4. Apply the shared milestone to the epic and every child issue. Milestone
   membership is not inferred from the parent relationship, so set it explicitly
   on every issue.
5. Create the epic and child issues, then attach every child using a native
   relationship, for example `gh issue edit <child> --parent <epic> --repo <repo>`.
   For a pre-existing hierarchy, use `--add-sub-issue`, `--remove-sub-issue`,
   `--parent`, or `--remove-parent` as appropriate. Never use an issue-body
   checklist or sibling links as a substitute for this relationship.
6. Represent execution order with GitHub blocking relationships (`--add-blocked-by`
   or `--add-blocking`), not prose-only dependencies. Mark `paralizable` only
   when a task can genuinely proceed alongside the main development path after
   its declared prerequisite is available.
7. Verify the resulting hierarchy, labels, milestone, and dependencies with
   `gh issue view --json parent,subIssues,milestone,labels` (or an equivalent
   GitHub API read) before reporting completion.

## Titles and issue bodies

- Write outcome-oriented titles. Do not put milestone names/numbers, epic
  prefixes, issue numbers, or hierarchy markers in titles.
- Keep each body compact: purpose, in-scope work, explicit exclusions where
  useful, observable acceptance criteria, and material dependencies.
- Do not copy the entire product brief into every issue.
- Generate a suggested branch name as `codex/<issue-number>-<slug>`; create a
  branch only if the user asks to begin implementation.

## Labels

Read the repository's label catalogue before writes and use the exact existing
label spelling. In this repository, use the literal `EPIC` label (uppercase),
never a lowercase `epic` variant. Apply only labels justified by the issue:

| Situation | Label |
| --- | --- |
| Top-level hierarchy issue | `EPIC` |
| New user-visible capability | `feature` |
| Extension or improvement of an existing capability | `enhancement` |
| Independently executable alongside the main path | `paralizable` |
| Defect, documentation-only work, duplicate, or abandoned work | `bug`, `documentation`, `duplicate`, or `won't fix` |

Do not silently create a new label. If the available labels do not describe an
important recurring classification, propose the label, its definition, and the
issues it would affect to the user first.

## Output contract

Return a compact register, without repeating issue bodies:

| Hierarchy | Type and labels | Milestone | Depends on | Issue | Suggested branch |
| --- | --- | --- | --- | --- |
| Epic or parent → child | `EPIC`, `feature`, ... | <milestone> | <none/id> | <id/url> | `codex/<issue>-<slug>` |

## Gate Rules

- Do not make an epic solely to group a single issue.
- Do not add a milestone name to an issue title to imply membership.
- Do not create labels, milestones, branches, or issue hierarchy changes beyond
  the user-authorized scope.
- Stop if the issue boundary cannot be independently tested or the milestone
  association is unclear.
