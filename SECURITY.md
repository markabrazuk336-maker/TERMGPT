# Security Policy

## Supported Versions

TERMGPT is currently in beta.

## Reporting a Vulnerability

Please report security vulnerabilities privately.
Do not publish credentials, tokens or exploit details in public issues.

## Security Limitations

- TERMGPT does not provide a complete security sandbox.
- Automatic approval can execute commands with user permissions.
- Full Access can inspect files outside the workspace.
- File contents and command output may be sent to ChatGPT.
- Local conversation history is not encrypted.
- Do not run TERMGPT as administrator.

## Authentication

TERMGPT uses the OpenAI Sign in with ChatGPT DevKit.
Local credential encryption uses Windows DPAPI.
