# Delivery controls

Use this only after the engineering brief passes preflight and before any delegation.

| Class | Writers | Reviewers | Full checks |
| --- | --- | --- | --- |
| Small | 0–1 | 1 | 0–1 |
| Medium | 0–2 | 1 | 1 |
| Large | 0–2 | 1 | 1 |

Keep context and validation focused:

- subagent brief: at most 600 words;
- one successful focused-check label per worker; and
- one successful full-check label per integration state.

For every code-changing increment, use one independent code reviewer even when the delivery shape is otherwise small. `independent-code-review` limits the review loop to five complete rounds.

Use `run-compact.sh --history <path>` to warn on an identical successful check. A warning requires a reason (`code changed`, `integration changed`, or `investigating failure`) before repeating it.
