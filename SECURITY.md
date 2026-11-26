# Security Policy

## Supported Versions

TERMGPT v0.8.4 is an experimental beta release.

## Reporting Vulnerabilities

Report vulnerabilities privately through GitHub Security.
Do not include credentials or tokens in public issues.

## Security Model

- TERMGPT is not a security sandbox.
- Shell commands execute with current user permissions.
- Full Access enables inspection outside the workspace.
- Automatic approval may execute actions without confirmation.
- File contents and command outputs may be sent to ChatGPT.
- Conversation history is stored locally without encryption.
- Authentication credentials use Windows DPAPI.
- Never run TERMGPT as administrator.

Use Manual Mode and Workspace Access for untrusted projects.

## Dependencies

The OpenAI SDK source revision is pinned.
Dependencies are checked using npm audit during installation.
This does not guarantee the absence of vulnerabilities.
