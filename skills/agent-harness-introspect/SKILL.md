---
name: agent-harness-introspect
description: Safely audit or upgrade BraveCow Harness across Codex, ZCode, shared skills, memory, and OpenClaw state.
---

# Agent Harness Introspect

Audit the installed Harness; an explanation request authorizes inspection, while an upgrade request authorizes tested changes.
Detect Windows or macOS first. `~` is the current user's home; paths below are relative to `~/.bravecow/harness` unless stated otherwise.

## Workflow

1. Read `~/.bravecow/memories/PROFILE.md` and `ACTIVE.md`, then `README.md`, `catalog/import-backlog.json`, and `catalog/external-round1.md`.
2. Inspect present control surfaces: shared `~/.agents/skills`; Codex config, agents, automations and plugin cache; ZCode instructions, commands and skills; Claude and OpenClaw cross-runtime links. Cache presence does not establish activation.
3. Refresh `scripts/build_skill_inventory.py` and `scripts/harness_audit.py` with Python. Read `catalog/harness.lock.json` for drift, provenance, verification dates and rollback refs. The lock records observations, not update permission.
4. Read known Markdown directly; otherwise run `scripts/memory_router.py "query"`. For proposed durable-memory writes, `scripts/memory_write_gate.py` validates only. Markdown stays canonical; indexes remain replaceable.
5. For authorized upgrades, follow [upgrade acceptance](references/upgrade-acceptance.md). Catalog outside resources and preserve source/version metadata under `vendor/` before review or activation.
6. Report active capabilities, missing or conflicting paths, measured changes, unresolved risks and deferred candidates. Save reports or backlog updates only within the requested scope.

## Boundaries

- Preserve private configuration, local patches, automation prompts/state, secrets and memory outside Git.
- Change `AGENTS.md` only on explicit user request; otherwise give a candidate patch.
- Use `$writing-for-agents` for skills, instruction files and role briefs.
- Share skills through runtime links to `~/.agents/skills` where compatible.
- Activate reviewed technology only after an isolated experiment and end-to-end acceptance with a rollback point.
