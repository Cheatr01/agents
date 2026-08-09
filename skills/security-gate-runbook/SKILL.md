---
name: security-gate-runbook
description: Triage material security findings and produce a compact security decision for a security-sensitive increment or release. Use when auth, permissions, secrets, sensitive data, execution, or a concrete finding is in scope; do not run a full audit by default.
---

# Security Gate Runbook

## Workflow

1. Review only the changed boundary and its direct data/control flow.
2. Classify evidence-backed findings: `critical`, `high`, `medium`, or `low`.
3. Fix blockers, or obtain explicit time-bounded risk acceptance where policy allows it.
4. Check tool output and logs for secrets without printing environment values. Test presence only (for example, `GH_TOKEN=set`), never the value.

## Output Contract

```
Findings: <none or id:severity:one-line impact>
Blockers: <none or ids>
Remediation / acceptance: <owner + expiry when needed>
Decision: APPROVE / CONDITIONAL / REJECT
Residual risk: <one line>
```

## Gate Rules

- No approval with open critical findings.
- Do not downgrade a finding merely to avoid a delivery delay.
- Never expose secret values in commands, logs, diffs, or summaries.
