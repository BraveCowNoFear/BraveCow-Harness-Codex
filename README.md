# BraveCow Harness Codex

Current release: `0.5.0`.

BraveCow Harness Codex is a Windows-first control plane for Codex Desktop. It installs auditable skill inventory, provenance locks, safe update boundaries, local Markdown/FTS5 memory retrieval, agent profiles, and harness reports without copying private runtime state.

For Chinese instructions, see [README.zh-CN.md](README.zh-CN.md).

## What It Installs

- `~/.codex/harness`: audit, config-gate, provenance-lock, and SQLite FTS5 memory scripts.
- `~/.agents/skills/agent-harness-introspect`: a skill for inspecting the local Codex harness.
- `~/.codex/skills/agent-harness-introspect`: a junction to the shared skill when possible, otherwise a copy.
- `~/.codex/memories`: seven starter memory files, including a retention policy and session log.
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

# Preview an update without writing anything
powershell -ExecutionPolicy Bypass -File .\install.ps1 -UpdateRuntime -MigrateConfig -DryRun

# Update runtime scripts and the managed AGENTS block; existing memory is preserved
powershell -ExecutionPolicy Bypass -File .\install.ps1 -UpdateRuntime -MigrateConfig -InitializeMemory

# Explicit high-risk user-data replacement; every overwritten file is backed up first
powershell -ExecutionPolicy Bypass -File .\install.ps1 -ReplaceUserData

# Avoid junction creation and copy the skill into ~/.codex/skills instead
powershell -ExecutionPolicy Bypass -File .\install.ps1 -NoJunctions
```

`-InitializeMemory` creates only missing memory files. `-Force` is retained as a safe compatibility alias for `-UpdateRuntime -MigrateConfig`; it never replaces memory or other user data. Backups are written under `~/.codex/harness/backups/` before any existing managed file is overwritten.

## Memory Retrieval

Markdown remains canonical. The router reads known files directly, uses SQLite FTS5 for ordinary lookup, and only hands temporal/relationship questions to Graphiti when its existing ports are healthy:

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\memory_router.py" "browser Edge rule"
```

Every result is a bounded evidence pack. Vector and graph stores are optional indexes; failure falls back locally without starting or repairing services. Proposed durable writes can be checked without mutation:

```powershell
Get-Content .\candidate.json | python "$env:USERPROFILE\.codex\harness\scripts\memory_write_gate.py"
```

`harness.lock.json` schema v2 records resolved plugin packages, source/installed component versions, Git remote/branch/commit, license evidence, verification state, local patches, and rollback refs. Unknown fields remain explicit instead of being guessed.

Optional `skill_contracts.py` runs machine-specific positive/negative routing prompts. The repository ships an example; active contracts are local state and are not silently enabled for another machine.

## Repository Safety Model

This repository is intentionally small. It captures the harness architecture, not a user's private machine state. The installer creates local reports after installation so each user can review their own setup.

Run the package validation check before publishing changes:

```powershell
python .\tests\validate_package.py
python -m unittest discover -s .\tests
powershell -ExecutionPolicy Bypass -File .\tests\smoke_install.ps1
```
