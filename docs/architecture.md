# Architecture

BraveCow Harness Codex keeps the runtime small and observable.

## Layers

1. **Memory entry points**
   - `~/.codex/memories/PROFILE.md`
   - `~/.codex/memories/ACTIVE.md`
   - `~/.codex/memories/LEARNINGS.md`
   - `~/.codex/memories/ERRORS.md`
   - `~/.codex/memories/FEATURE_REQUESTS.md`

2. **Harness workspace**
   - `~/.codex/harness/scripts`: local maintenance scripts.
   - `~/.codex/harness/catalog`: generated inventories and import backlog.
   - `~/.codex/harness/reports`: point-in-time audit reports.
   - `~/.codex/harness/vendor`: quarantine area for third-party resources.

3. **Shared skill pool**
   - `~/.agents/skills` is the preferred canonical location for reusable skills.
   - `~/.codex/skills` can link to shared skills or hold Codex-specific wrappers.

4. **Agent profiles**
   - `~/.codex/agents/default.toml`
   - `~/.codex/agents/explorer.toml`
   - `~/.codex/agents/worker.toml`

## Operating Principles

- Catalog first, activate later.
- Prefer shared skills and runtime junctions over copied duplicates.
- Keep external resources quarantined until provenance and safety are reviewed.
- Keep private state out of Git.
- Let each machine generate its own inventory and audit report.

