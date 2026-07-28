# Architecture

BraveCow Harness Codex keeps the runtime small, observable, and degradable.

## Layers

1. **Memory entry points**
   - `~/.codex/memories/PROFILE.md`
   - `~/.codex/memories/ACTIVE.md`
   - `~/.codex/memories/MEMORY_POLICY.md`
   - `~/.codex/memories/SESSION_LOG.md`
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

5. **Codex plugin cache visibility**
   - `~/.codex/plugins/cache` is scanned read-only for plugin manifests and provided skills.
   - Cache presence is reported separately from activation state.

6. **Retrieval router**
   - Known path: read canonical Markdown directly.
   - Ordinary exact/substring search: local SQLite FTS5.
   - Semantic retrieval: optional vector backend.
   - Temporal/entity relationships: optional Graphiti backend.
   - Every backend produces a bounded evidence pack; external-service failure falls back to Markdown/FTS5.

7. **Version and update control**
   - `harness.lock.json` schema v2 records observed skill/plugin hashes, resolved packages, component source/installed versions, Git remote/branch/commit, license evidence, verification status, local patches, and rollback refs.
   - The lock is evidence, not auto-update authorization.
   - A semantic change preserves one previous snapshot for deterministic weekly/local diffing; timestamps alone do not create drift.
   - Runtime, config, memory initialization, and user-data replacement are separate installer operations.

## Operating Principles

- Catalog first, activate later.
- Prefer shared skills and runtime junctions over copied duplicates.
- Keep external resources quarantined until provenance and safety are reviewed.
- Keep private state out of Git.
- Let each machine generate its own inventory and audit report.
- Treat plugin cache entries as evidence of downloaded packages, not enabled plugins.
- Resolve one package per logical plugin using remote-install markers first and exact config ids second; retain older cache entries for rollback.
- Keep Markdown canonical and all retrieval databases replaceable.
- Validate durable-memory candidates for reuse, source, scope, confidence, expiry, conflicts, and secrets before any human-approved write.
- Back up before overwriting; never let an ordinary runtime update replace user data.
- Measure startup context, retrieval evidence, retries, and failure-degrade latency.
