---
name: performance-regression-lab
description: Investigate performance regressions with baseline methodology, before/after measurements, and stop-go limits for deployment safety.
metadata:
  short-description: Perf baseline and regression decisioning
  tags:
    - performance
    - efficiency
    - benchmarking
    - governance
---

# Performance Regression Lab

Use this skill when the performance track is active or a regression is detected.

## Role Scope

- Primary: Efficiency Expert
- Consumers: Tech Lead, Backend Engineer, Frontend Engineer

## Inputs Required

- Baseline metrics and measurement method
- Current implementation metrics
- Performance target/SLO
- Representative workload profile

## Measurement Hygiene

- Use comparable environment and workload
- Warm-up before collecting measurements
- Run enough samples to reduce noise
- Record tool versions and parameters

## Core Metrics

Track at least:

- Latency (p50, p95, p99)
- Throughput
- Error rate under load
- Resource usage (CPU/memory/io)

## Workflow

1. Validate baseline quality and comparability.
2. Measure current behavior with same profile.
3. Compute before/after deltas.
4. Identify bottlenecks and probable root causes.
5. Propose and test remediations.
6. Issue stop/go decision using explicit limits.

## Stop/Go Policy

- `GO`: all key metrics within agreed tolerance
- `CONDITIONAL`: one non-critical metric outside tolerance with mitigation plan
- `STOP`: critical metric violates tolerance or result quality is inconclusive

## Output Contract

- Baseline Method:
- Workload Profile:
- Before Metrics:
- After Metrics:
- Delta Summary:
- Bottleneck Analysis:
- Stop/Go Limits:
- Decision: GO/CONDITIONAL/STOP
- Follow-up Actions:

## Gate Rules

- No go decision on non-comparable measurements.
- Critical-path regression requires escalation and re-scoring.

## Integrations

- Pair with `orchestration-scorekeeper` when performance risk changes.
- Pair with `integration-merge-governor` for final release readiness.
