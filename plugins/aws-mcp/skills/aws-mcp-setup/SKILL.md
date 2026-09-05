---
name: aws-mcp-setup
description: Set up and verify the managed AWS MCP Server for Codex, choosing OAuth for an interactive human sign-in or SigV4 for local AWS profiles. Use before configuring AWS MCP access; do not use for routine AWS operations.
---

# AWS MCP Setup

Configure the managed AWS MCP Server for a local Codex user. The default target is AWS's managed remote MCP service, not an older AWS Labs stdio server.

## Before Changing Anything

- Read the current AWS setup reference before composing commands; server endpoints and client syntax can change.
- Inspect the existing MCP configuration and available AWS CLI/profile names without reading or printing credential values.
- Confirm the target AWS partition, MCP endpoint Region, default operation Region, and whether the user needs multiple accounts in one session.
- Ask for explicit approval immediately before installing software, adding/removing an MCP configuration, or starting an interactive authentication flow.
- Never ask the user to paste, download, upload, or reveal an access key, secret key, session token, browser cookie, or OAuth token.

## Route

### OAuth — default for a human, one-account workflow

Use the managed HTTPS endpoint directly when the user is working interactively and does not need profile switching in one session.

1. Configure the Codex MCP entry using the current official endpoint with the OAuth initialization parameter.
2. Start `codex mcp login aws-mcp` (or the client's equivalent) only after approval.
3. The user completes AWS Sign-In and consent in the browser. Do not attempt to automate the sign-in, MFA, or consent page.
4. Confirm the connection with a read-only documentation query before any AWS API call.

OAuth does not download AWS access keys. If authorization fails, explain the missing IAM OAuth permission and ask the account administrator to grant it; do not attach policies or change IAM roles unless the user explicitly asks.

### SigV4 — named profiles, multi-account, or stricter local control

Use the AWS MCP Proxy only when the user needs profile switching, a specific default operation Region, read-only tool filtering, or cannot use OAuth.

1. Confirm that AWS CLI 2.32.0 or newer and `uv` are available; request approval before installing either.
2. Prefer an existing named profile. For a human session, use `aws login`; for an organization's IAM Identity Center setup, use `aws configure sso` once and `aws sso login --profile <name>` to refresh it.
3. Verify the selected profile with `aws sts get-caller-identity`, but summarize the result without exposing credential material.
4. Add the documented `uvx mcp-proxy-for-aws` configuration only after the identity check succeeds.
5. Restart Codex if needed and verify the installed tools with a harmless documentation or region-listing request.

Do not create, rotate, or retrieve IAM access keys as a setup shortcut. If the user already has a managed credential provider, role, or credential process, preserve it and use its named profile. Static keys are an exception owned by the user or their administrator and must be entered locally, never through chat or committed configuration.

## Configuration Safety

- Do not replace an existing `aws-mcp` entry or remove legacy AWS MCP entries without showing the conflict and obtaining approval.
- Keep AWS credentials out of MCP configuration files, environment dumps, shell history, repository files, and the final handoff.
- Treat the first tool call as potentially permissioned. Start with documentation or identity verification; do not perform a write as a connection test.
- If the desired account, Region, role, or allowed operation set is unclear, stop before authentication or configuration changes.
- To roll back a confirmed Codex configuration, use `codex mcp remove aws-mcp`; do not delete AWS credentials or alter IAM access as part of rollback.

## Troubleshooting

- Expired OAuth session: ask the user to run the client login flow again.
- Expired SSO session: run `aws sso login --profile <name>` after approval, then restart the MCP client.
- Missing credentials: guide the user to `aws login` or their organization's SSO configuration; never request keys in chat.
- OAuth 400: identify that the principal needs the AWS MCP OAuth permissions and route the policy change to the AWS administrator.
- SigV4 failure: verify the selected profile, operation Region, AWS partition, and system clock before changing configuration.

## Output Contract

```
Target: managed AWS MCP Server
Authentication: OAuth / SigV4
MCP endpoint Region: <region>
Operation Region: <region or profile default>
Credential source: <AWS Sign-In / named SSO profile / existing provider>
Changed: <Codex MCP config, local prerequisite, or none>
Verification: <read-only result>
Secrets handled: none
Next user action: <browser sign-in / administrator permission / none>
Rollback: <codex mcp remove aws-mcp / none>
```
