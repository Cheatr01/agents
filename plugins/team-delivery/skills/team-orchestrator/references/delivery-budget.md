# Delivery budget

Use this only after the engineering brief passes preflight and before any delegation.

| Class | Estimated token ceiling | Writers | Reviewers | Full checks |
| --- | --- | --- | --- | --- |
| Small | 12k | 0–1 | 1 | 0–1 |
| Medium | 30k | 0–2 | 1 | 1 |
| Large | 60k | 0–2 | 1 | 1 |

If the platform reports actual usage, record it in the delivery ledger. Otherwise record `estimated` and enforce these measurable proxies:

- subagent brief: at most 600 words;
- tool result admitted to context: at most 1,500 tokens;
- one successful focused-check label per worker; and
- one successful full-check label per integration state.

For every code-changing increment, reserve one independent code reviewer even when the delivery shape is otherwise small. Allocate an implementation reserve and a review reserve within the total ceiling; the review reserve must be no greater than the implementation reserve. Across all review rounds, reviewer consumption must be no greater than implementation consumption for the same increment. When usage is estimated, record that this comparison is estimated. `independent-code-review` limits the review loop to five complete rounds.

Use `run-compact.sh --history <path>` to warn on an identical successful check. A warning requires a reason (`code changed`, `integration changed`, or `investigating failure`) before repeating it.
