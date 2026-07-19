---
name: agent-harness-introspect
description: Audit and explain the local AI harness across Codex, shared skills, and OpenClaw. Use when the task is to upgrade the agent architecture, inspect installed skills/plugins/automations/memory, review what is active, find link drift between shared and runtime-specific skills, or prepare the next safe upgrade round.
---

# Agent Harness Introspect

Use this skill when the user is asking about the agent's own setup rather than an external project.

## What this skill covers

- Codex runtime state under `%USERPROFILE%\.codex`
- Shared skill pool under `%USERPROFILE%\.agents\skills`
- OpenClaw cross-reference state under `%USERPROFILE%\.openclaw`
- Memory loop health under `%USERPROFILE%\.codex\memories`
- Automation coverage under `%USERPROFILE%\.codex\automations`
- Cached plugin packages under `%USERPROFILE%\.codex\plugins\cache`
- Safe intake of third-party skills/plugins through the local harness catalog and quarantine area

## Default workflow

1. Read the global memory entry points first:
   - `%USERPROFILE%\.codex\memories\PROFILE.md`
   - `%USERPROFILE%\.codex\memories\ACTIVE.md`
2. Inspect these local control points:
   - `%USERPROFILE%\.codex\config.toml`
   - `%USERPROFILE%\.codex\agents\`
   - `%USERPROFILE%\.codex\automations\`
   - `%USERPROFILE%\.codex\plugins\cache\`
   - `%USERPROFILE%\.codex\harness\README.md`
   - `%USERPROFILE%\.codex\harness\catalog\import-backlog.json`
   - `%USERPROFILE%\.codex\harness\catalog\external-round1.md`
3. Refresh the local inventory when the answer depends on current state:
   - Run `python %USERPROFILE%\.codex\harness\scripts\build_skill_inventory.py`
   - Run `python %USERPROFILE%\.codex\harness\scripts\harness_audit.py`
4. When a user asks to import or migrate outside resources:
   - Prefer cataloging first
   - Store third-party items in `%USERPROFILE%\.codex\harness\vendor\`
   - Keep them quarantined until manually reviewed
5. Summarize:
   - what is active now
   - what is missing or drifting
   - what is safe to upgrade immediately
   - what should stay deferred

## Safe upgrade rules

- Do not auto-edit `AGENTS.md` unless the user explicitly asks.
- Do not auto-enable third-party code or plugins merely because they are popular.
- Treat plugin cache entries as cached packages, not proof that they are enabled.
- Prefer shared skills in `%USERPROFILE%\.agents\skills` and runtime-specific junctions over copied duplicates.
- If a skill or plugin comes from an external repository, preserve provenance in a manifest before activation.
- For supply-chain-sensitive items, migrate metadata or a quarantined snapshot first, then leave activation as a separate step.

## Good outputs

- A concise explanation of the current harness architecture
- A list of drift, duplication, or missing links
- A safe upgrade plan with immediate changes and deferred items
- Updated harness reports or backlog files when the user asked for changes
