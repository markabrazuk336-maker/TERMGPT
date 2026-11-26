# TERMGPT

> Your personal AI coding agent, powered by ChatGPT.

![Version](https://img.shields.io/badge/version-0.8.3-2dd4bf)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.12-yellow)
![Status](https://img.shields.io/badge/status-Beta-orange)

## About

TERMGPT is an independent terminal-based AI coding assistant
built with Python and Node.js.

It uses the official Sign in with ChatGPT DevKit,
allowing eligible users to use their ChatGPT subscription
without purchasing a separate API key.

No Claude Code or Codex CLI installation required.

## Features

- ChatGPT OAuth authentication
- Windows DPAPI credential encryption
- AI model selection
- Autonomous coding agent
- PowerShell command execution
- Automatic approval mode
- Full filesystem inspection mode
- File attachments using @
- Persistent conversations and sessions
- Task manager
- Colored file diffs
- File backups and undo
- Streaming chat responses
- Read-only planning mode
- Fast response mode
- Disk usage inspection
- Global CLI command
- Gradient ASCII interface

## Requirements

- Windows 10 or 11
- Python 3.12+
- Node.js 22.12+
- Git
- An eligible ChatGPT account

## Installation

```powershell
git clone https://github.com/markabrazuk336-maker/TERMGPT.git
cd TERMGPT

py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

git clone https://github.com/openai/sign-in-with-chatgpt-devkit.git sdk

cd sdk
npm.cmd ci
npm.cmd run build -w @siwc/local
cd ..

.\.venv\Scripts\python.exe main.py
```

## Authentication

Run `/login` inside TERMGPT and sign in through your browser.

## Commands

| Command | Description |
|---------|-------------|
| /help | Show commands |
| /login | Sign in with ChatGPT |
| /logout | Disconnect account |
| /models | List available models |
| /model | Select model |
| /agent | Coding agent mode |
| /chat | Streaming chat mode |
| /plan | Read-only planning mode |
| /auto on | Enable automatic approval |
| /auto off | Disable automatic approval |
| /access full | Enable full disk inspection |
| /access workspace | Restrict filesystem access |
| /sessions | List saved sessions |
| /tasks | Show task progress |
| /undo | Undo last supported file change |
| /drives | List available drives |
| /fast on | Request concise responses |

## Security

TERMGPT is experimental software.

Automatic approval allows commands to execute with the
permissions of the current Windows user.

The application does not provide a complete security sandbox.
Do not run it as administrator.

File contents and command outputs may be sent to ChatGPT.
Conversation history is stored locally without encryption.

## Dependencies and licensing

TERMGPT uses the official OpenAI Sign in with ChatGPT DevKit.

https://github.com/openai/sign-in-with-chatgpt-devkit

The DevKit is distributed separately under its own
noncommercial license. OpenAI service terms also apply.

TERMGPT is an independent project and is not affiliated
with or endorsed by OpenAI.
