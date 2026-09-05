# Managed AWS MCP Server reference

Use this reference while configuring the managed AWS MCP Server. Before mutating configuration, verify the current commands against AWS's [setup guide](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/getting-started-aws-mcp-server.html). This reference was checked on 2026-09-04.

## Endpoint selection

| MCP endpoint Region | HTTPS endpoint |
| --- | --- |
| `us-east-1` | `https://aws-mcp.us-east-1.api.aws/mcp` |
| `eu-central-1` | `https://aws-mcp.eu-central-1.api.aws/mcp` |

The endpoint Region selects the managed server. It is separate from the default Region for AWS operations.

## OAuth route

For Codex, AWS documents this configuration:

```sh
codex mcp add aws-mcp --url https://aws-mcp.us-east-1.api.aws/mcp?oauth=initialize
codex mcp login aws-mcp
```

The second command opens an AWS Sign-In browser flow. The user must perform login, MFA, and consent themselves. AWS says OAuth access tokens are valid for one hour and are refreshed for up to twelve hours. OAuth does not support multi-profile switching in one session.

The IAM principal needs `signin:AuthorizeOAuth2Access` and `signin:CreateOAuth2Token`; AWS publishes the `AWSMCPSignInOAuthAccessPolicy` managed policy. Escalate a missing permission to the AWS administrator rather than attaching it by default.

## SigV4 route

Use this path for named profiles, cross-account work, or a defined operation Region. AWS documents this Codex command as an example:

```sh
codex mcp add aws-mcp uvx mcp-proxy-for-aws==1.6.4 https://aws-mcp.us-east-1.api.aws/mcp --metadata AWS_REGION=us-west-2
```

The documented proxy version is intentionally an example rather than a permanent pin. Check the current AWS guide before use. The proxy is installed through `uvx`; obtain user approval before a first-time download or `uv` installation.

AWS requires AWS CLI 2.32.0 or newer for the documented local-credential route. Prefer `aws login` for a human session or a configured SSO profile with `aws sso login --profile <name>`. Verify the chosen profile using `aws sts get-caller-identity` without copying its raw output into the conversation.

## Safe verification and rollback

Use `codex mcp list` to confirm the entry and a documentation/region-listing question to confirm tool discovery. Do not test with an AWS write operation.

To remove only this Codex MCP configuration:

```sh
codex mcp remove aws-mcp
```
