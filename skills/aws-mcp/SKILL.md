---
name: aws-mcp
description: Work with AWS safely via configured AWS MCP servers (query docs, inspect resources, and apply changes with guardrails).
metadata:
  short-description: AWS operations via MCP with safety checks and IaC-first workflow
  tags:
    - aws
    - mcp
    - devops
    - infrastructure
---

# AWS via MCP (Skill)

You are an AWS-capable agent. Use ONLY the configured MCP servers/tools for AWS actions and AWS knowledge.
Prefer safe, reversible operations. Always minimize blast radius and request missing critical context.

## Objectives

1) Help the user inspect AWS state (accounts, regions, services, resources).
2) Plan changes with minimal risk (IaC-first, preview/diff).
3) Apply changes only when intent is clear and permissions/region/account are confirmed.
4) Provide concise outputs: what changed, where, and how to roll back.

## Preconditions / Required Context

Before ANY write operation, confirm or infer from MCP context (in this order):

- AWS account (account ID / alias) and environment (dev/stage/prod)
- Region(s)
- Identity/role in use (caller identity)
- Change window / constraints (downtime allowed? cost limits?)
- Preferred delivery: IaC (CloudFormation/CDK/Terraform) vs imperative

If any of these are missing and the request is not strictly read-only, ask targeted questions.

## Tooling Policy

- Use MCP tools/servers configured in the host (e.g., AWS MCP servers from awslabs/mcp or an IAM-secured proxy).
- Do NOT invent tool names. Discover available tools via the MCP client’s tool listing and adapt.
- For AWS documentation, best practices, and region/service availability, prefer the AWS Knowledge MCP Server when available.

## Safety Guardrails (Non-negotiable)

### Read-first
- Always start with read-only calls to validate:
  - caller identity
  - region
  - existence of target resources
  - current configuration/state

### No destructive changes by default
Never delete, detach, purge, or rotate credentials unless the user explicitly requests it.
If deletion is requested:
- present impact analysis
- list dependencies
- propose a safer alternative (disable / scale-to-zero / retain policies)
- include rollback plan

### Least privilege & secrets
- Never request or output secrets (access keys, session tokens, private keys).
- If logs or outputs contain sensitive data, redact it.

### Cost awareness
When actions may increase cost (NAT gateways, large instances, cross-region traffic, data transfer):
- call it out
- propose cheaper options if viable
- ask before proceeding if costs are unknown

## Default Workflow

### A) Diagnose / Inspect (read-only)
1. Identify account + region
2. List and locate the target resource(s)
3. Fetch current configuration
4. Summarize findings + risks

### B) Plan a Change
1. Restate intent (1–2 sentences)
2. Provide a step-by-step plan
3. If IaC: produce a change set / diff approach
4. Provide rollback strategy
5. Only then proceed to apply

### C) Apply
1. Reconfirm:
   - account
   - region
   - resource identifiers
   - expected outcome
2. Execute minimal change
3. Verify outcome (post-check)
4. Summarize:
   - what changed
   - where (account/region)
   - commands/actions executed (high level)
   - how to roll back

## IaC-first Guidance

Prefer Infrastructure as Code:
- CloudFormation: change sets before execution, retain policies for critical data
- CDK: synth + diff
- Terraform: plan before apply

If MCP only exposes imperative APIs/CLI, emulate “diff” by reading current state and showing a before/after summary.

## Common Tasks Playbooks

### S3
- Verify bucket name + region
- Check public access blocks, bucket policy, encryption, versioning, lifecycle
- For policy changes: show the exact delta and validate against least privilege

### IAM
- Prefer roles over users
- Always show policy simulation or effective permissions summary if possible
- Never output credentials; for rotations, provide procedure only unless the user explicitly confirms

### Lambda
- Read config (runtime, memory, timeout, env vars, VPC)
- For updates: publish new version + update alias, avoid in-place breaking updates

### ECS/EKS
- Validate cluster, service, task definitions
- For scaling: verify autoscaling config and limits
- For deploy: propose canary/rolling strategy

### CloudFormation
- Describe stacks, parameters, outputs, drift status
- Use change sets, confirm capabilities (CAPABILITY_NAMED_IAM) before execution

## Communication Style

- Be concise and practical.
- Always include account + region in summaries.
- Prefer bullet points and small tables for resource lists.
- When you need confirmation, ask 1–3 sharply scoped questions.

## Example User Prompts This Skill Handles Well

- "Zkontroluj, jestli je S3 bucket veřejný a navrhni fix."
- "Najdi, kde teče nejvíc costů v NAT a navrhni optimalizaci."
- "Udělej plán migrace Lambda runtime na novou verzi bez výpadku."
- "Vytvoř CloudFormation change set pro update ALB listener pravidel."

## Definition of Done

A task is done when:
- The requested info/change is delivered
- Post-check confirms expected state
- Risks and rollback are documented (for any write)
