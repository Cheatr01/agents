---
name: contract-freeze-kit
description: Prepare and validate API contract freeze readiness with a strict checklist covering error model, versioning, auth model, payload examples, and approval verdict.
metadata:
  short-description: Contract freeze checklist and verdict
  tags:
    - architecture
    - security
    - api
    - governance
---

# Contract Freeze Kit

Use this skill immediately before Contract Freeze in Phase 2.

## Role Scope

- Primary: Architect, Security Reviewer
- Mandatory approvers: Architect + Security Reviewer

## Use When

- New or changed API/data contract exists
- Multiple teams depend on interface stability
- FE/BE parallel implementation is about to start

## Required Inputs

- Contract draft (endpoints/events/schemas)
- Authn/authz model
- Error model and code taxonomy
- Versioning and compatibility policy
- Example payloads for success and failure cases

## Freeze Checklist

### Contract Structure

- Endpoint/event ownership is explicit
- Request/response schemas are complete
- Field-level constraints are documented

### Error Model

- Error codes are stable and deterministic
- Error payload shape is uniform
- Recoverable vs non-recoverable errors are clear

### Versioning

- Version strategy is explicit
- Breaking-change rule is defined
- Deprecation timeline is documented

### Auth Model

- Authentication scheme defined
- Authorization boundaries defined
- Failure semantics for auth errors are defined

### Payload Examples

- Happy path examples included
- Validation failure examples included
- Auth failure examples included

### Consumer Readiness

- Migration notes for impacted consumers
- Rollout sequencing notes
- Backward compatibility risks documented

## Decision Matrix

- `READY`: all checklist items pass
- `CONDITIONAL`: only low-risk documentation gaps remain with owners/due dates
- `NOT_READY`: any structural, auth, versioning, or error-model gap

## Output Contract

- Contract Summary:
- Checklist Results:
- Structure: pass/fail
- Error Model: pass/fail
- Versioning: pass/fail
- Auth Model: pass/fail
- Payload Examples: pass/fail
- Consumer Readiness: pass/fail
- Open Gaps:
- Verdict: READY/CONDITIONAL/NOT_READY
- Required Actions Before Freeze:

## Gate Rules

- No Contract Freeze on `NOT_READY`.
- `CONDITIONAL` requires explicit owner and due date per gap.
- Post-freeze breaking changes require re-freeze procedure.

## Integrations

- Pair with `threat-model-baseline` to validate security assumptions.
- Pair with `contract-drift-guard` for post-freeze enforcement.
