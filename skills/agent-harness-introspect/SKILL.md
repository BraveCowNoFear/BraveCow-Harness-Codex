---
name: agent-harness-introspect
description: Audit and explain the local Codex harness across config, skills, memories, automations, agent profiles, and quarantined imports.
---

# Agent Harness Introspect

Use this skill when the user asks about Codex's own local setup rather than an external project.

## What This Skill Covers

- Codex runtime state under `%USERPROFILE%\.codex`
- Shared skill pool under `%USERPROFILE%\.agents\skills`
- Optional cross-runtime state under `%USERPROFILE%\.openclaw`
- Memory loop health under `%USERPROFILE%\.codex\memories`
- Automation coverage under `%USERPROFILE%\.codex\automations`
- Safe intake of third-party skills/plugins through the local harness catalog and quarantine area

## Default Workflow

1. Read the memory entry points first when they exist:
   - `%USERPROFILE%\.codex\memories\PROFILE.md`
   - `%USERPROFILE%\.codex\memories\ACTIVE.md`
2. Inspect these local control points:
   - `%USERPROFILE%\.codex\config.toml`
   - `%USERPROFILE%\.codex\agents\`
   - `%USERPROFILE%\.codex\automations\`
   - `%USERPROFILE%\.codex\harness\README.md`
   - `%USERPROFILE%\.codex\harness\catalog\import-backlog.json`
   - `%USERPROFILE%\.codex\harness\vendor\`
3. Refresh local reports when the answer depends on current state:
   - `python "%USERPROFILE%\.codex\harness\scripts\build_skill_inventory.py"`
   - `python "%USERPROFILE%\.codex\harness\scripts\harness_audit.py"`
4. When a user asks to import or migrate outside resources:
   - Catalog first.
   - Store third-party items in `%USERPROFILE%\.codex\harness\vendor\`.
   - Keep them quarantined until manually reviewed.
5. Summarize:
   - what is active now
   - what is missing or drifting
   - what is safe to upgrade immediately
   - what should stay deferred

## Safe Upgrade Rules

- Do not auto-enable third-party code or plugins merely because they are popular.
- Prefer shared skills in `%USERPROFILE%\.agents\skills` and runtime-specific junctions over copied duplicates.
- If a skill or plugin comes from an external repository, preserve provenance in a manifest before activation.
- For supply-chain-sensitive items, migrate metadata or a quarantined snapshot first, then leave activation as a separate step.
- Do not edit `AGENTS.md` unless the user explicitly asks or the current task is an installation/update flow where editing `AGENTS.md` is the requested outcome.

## Good Outputs

- A concise explanation of the current harness architecture.
- A list of drift, duplication, or missing links.
- A safe upgrade plan with immediate changes and deferred items.
- Updated harness reports or backlog files when the user asked for changes.

