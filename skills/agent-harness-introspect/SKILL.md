---
name: agent-harness-introspect
description: Safely audit or upgrade BraveCow Harness across Codex, ZCode, shared skills, memory, and OpenClaw state.
---

# Agent Harness Introspect

Use this skill when the user asks about the assistant's own setup rather than an external project.

## What this skill covers

- Shared Harness state under `~/.bravecow/harness`
- Canonical memory under `~/.bravecow/memories`
- Codex state under `~/.codex`
- ZCode state under `~/.zcode`
- Shared skills under `~/.agents/skills`
- OpenClaw cross-reference state under `~/.openclaw`
- Codex automation and plugin-cache coverage, when Codex is installed
- Safe intake of third-party skills and plugins through the Harness catalog and quarantine area

`~` means the current user's home folder on Windows or macOS. Detect the host before showing platform-specific commands.

## Default workflow

1. Read `~/.bravecow/memories/PROFILE.md` and `ACTIVE.md` first.
2. Inspect the shared control points:
   - `~/.bravecow/harness/README.md`
   - `~/.bravecow/harness/catalog/import-backlog.json`
   - `~/.bravecow/harness/catalog/external-round1.md`
   - `~/.agents/skills/`
3. Inspect installed runtime control points only when present:
   - Codex: `~/.codex/config.toml`, `agents/`, `automations/`, and `plugins/cache/`
   - ZCode: `~/.zcode/AGENTS.md`, `commands/`, and `skills/`
4. Refresh current evidence when the answer depends on it:
   - Run `python ~/.bravecow/harness/scripts/build_skill_inventory.py`
   - Run `python ~/.bravecow/harness/scripts/harness_audit.py`
   - Read `catalog/harness.lock.json` for runtime presence, skill links, drift, verification, and rollback evidence.
5. Retrieve memory through the cheapest sufficient path:
   - Read known Markdown directly.
   - Otherwise run `python ~/.bravecow/harness/scripts/memory_router.py "<query>"`.
   - Use Graphiti only when already healthy and the question genuinely needs temporal or relationship reasoning.
   - Run `memory_write_gate.py` on proposed durable-memory candidates; it validates but never writes.
6. For outside resources, catalog first, store third-party material in `~/.bravecow/harness/vendor/`, and keep it quarantined until reviewed.
7. Summarize what is active, missing or drifting, safe to upgrade, and intentionally deferred.

## Safe upgrade rules

- Do not auto-edit `AGENTS.md` unless the user explicitly asks.
- Do not auto-enable third-party code merely because it is popular.
- Treat cache entries as evidence, not proof of activation.
- Treat `harness.lock.json` as observed provenance, not update permission.
- Keep private automation prompts and runtime state out of Git.
- Adopt technology only after a small isolated experiment and end-to-end verification.
- Keep Markdown canonical; FTS5, vector, and graph stores are replaceable indexes.
- Prefer shared skills in `~/.agents/skills` with runtime-specific links over duplicated copies.
- Preserve source and version metadata before activating external material.

## Good outputs

- A concise map of the current Windows/macOS and Codex/ZCode setup
- A list of drift, duplication, broken links, or missing runtime pieces
- A safe upgrade plan with immediate and deferred changes
- Updated Harness reports or backlog files when the user requested changes
