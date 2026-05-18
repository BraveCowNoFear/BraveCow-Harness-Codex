# BraveCow Harness Codex

BraveCow Harness Codex is a Windows-first starter harness for Codex Desktop. It installs a small, auditable control plane for skills, memory files, agent profiles, and harness reports without copying private local runtime state.

For Chinese instructions, see [README.zh-CN.md](README.zh-CN.md).

## What It Installs

- `~/.codex/harness`: portable audit and inventory scripts.
- `~/.agents/skills/agent-harness-introspect`: a skill for inspecting the local Codex harness.
- `~/.codex/skills/agent-harness-introspect`: a junction to the shared skill when possible, otherwise a copy.
- `~/.codex/memories`: five starter memory files.
- `~/.codex/agents`: starter `default`, `explorer`, and `worker` profiles.
- `AGENTS.md` snippets for the global Codex directory and, by default, the current workspace.

It does not install API keys, browser sessions, vault entries, personal profiles, automations, marketplace caches, or vendored third-party code.

## Quick Start

Open PowerShell in this repository and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Then ask Codex:

```text
Use the agent-harness-introspect skill and audit my local Codex harness.
```

## Useful Options

```powershell
# Install without editing the current workspace AGENTS.md
powershell -ExecutionPolicy Bypass -File .\install.ps1 -NoWorkspaceAgents

# Re-copy templates and scripts over existing files
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Force

# Avoid junction creation and copy the skill into ~/.codex/skills instead
powershell -ExecutionPolicy Bypass -File .\install.ps1 -NoJunctions
```

## Repository Safety Model

This repository is intentionally small. It captures the harness architecture, not a user's private machine state. The installer creates local reports after installation so each user can review their own setup.

Run the package validation check before publishing changes:

```powershell
python .\tests\validate_package.py
```

