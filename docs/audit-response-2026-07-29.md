# Audit Response — 2026-07-29

This release implements the actionable recommendations from the local Harness audit PDF and records the remaining external constraints without treating them as completed work.

## Completed

- Safe installer boundaries, backup-before-overwrite, dry-run, isolated smoke install, and Codex config runtime gate.
- `harness.lock.json` schema v2: resolved plugin package, source/installed/available component versions, Git remote/branch/commit, content hash, license evidence, verification status, local patch state, and rollback ref.
- Remote plugin markers supersede matching legacy config-cache packages while keeping old caches visible for rollback.
- Markdown remains canonical; direct read, incremental FTS5, bounded evidence packs, semantic fallback, and already-healthy Graphiti handoff are explicit routes.
- Graphiti failure falls back locally without starting services and is tested below five seconds.
- Durable-memory candidates are checked for reuse, source, scope, confidence, expiry, conflicts, and likely secrets; the gate never writes.
- Browser Harness `0.1.8` plus the Windows Edge allow-prompt patch passed its unit suite and a real Edge page-load, screenshot, task-tab cleanup, daemon cleanup, and watcher cleanup E2E.
- Meta Harness is at project version `0.4` and its validation passes.
- Only the three active Everything Claude Code skills were synchronized with the `v2.1.0` metadata contract; the unused full duplicate was archived recoverably.
- Duplicate generic PDF entry retired; Bilibili compatibility path reduced to a router; Vercel rule loading made selective; Guizang, Maoxuan, and Spec-Kit use short entrypoints with progressive references.
- Fifty deterministic positive/negative Skill trigger cases pass with zero mismatches. This is a structural regression gate, not a claim about live-model routing accuracy.
- Semantic lock changes preserve one previous snapshot for read-only drift diffing.

## Measured Boundaries

- Unique local Skill-description payload: `2,536` tokens, below the `3,000` target.
- Full Codex prompt-input sample: `11,034` tokens (`5,670` Skill catalog, `3,715` app-owned memory injection, `571` AGENTS, `795` plugin instructions, `283` other).
- The PDF's `7,500` total-startup target is not claimed: reaching it would require mutating app-owned memory/plugin injection or disabling useful installed capabilities, neither of which is a safe Harness-only optimization.
- Provenance plus rollback coverage: `100%` of discoverable local Skills. License and executable-test coverage remain separately reported instead of being inferred.

## Intentionally Deferred

- Graphiti source is `0.29.1`, its MCP environment is `0.28.2`, and latest verified stable tag is `v0.29.3`. Upgrade is deferred while provider health is partial; the lock exposes the drift and preserves rollback.
- Vector retrieval is not added merely to match a fashion. FTS5 is the ordinary path; vector search becomes worthwhile only with a measured semantic-query corpus and a fixed evaluation improvement.
- No protocol or marketplace cache is auto-migrated. External code remains catalog-first and activation remains a separate reviewed action.
