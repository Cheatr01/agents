---
name: performance-regression-lab
description: Measure and decide on a specific observed performance regression or explicit performance target using comparable before/after evidence. Use only when a metric, workload, or regression exists; do not use for speculative tuning.
---

# Performance Regression Lab

## Workflow

1. State the target or suspected regression and representative workload.
2. Measure baseline and current behaviour with the same method.
3. Run the smallest remediation experiment that can disprove the hypothesis.
4. Report the one or two decision metrics, not raw benchmark logs.

## Output Contract

```
Workload / method: <one line>
Baseline: <metric>
Current: <metric>
Delta: <value>
Decision: GO / CONDITIONAL / STOP
Next action: <none or owner>
```

## Gate Rules

- Do not claim a regression from non-comparable measurements.
- Escalate only a measured critical-path regression or a remediation that changes architecture.
- Store long profiles and traces outside the active context.
