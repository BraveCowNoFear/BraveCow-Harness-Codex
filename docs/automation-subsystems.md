# Harness Automation Subsystems

BraveCow Harness includes a private local automation control plane in addition to its skills, plugins, scripts, memory files, and reports. Automation definitions stay under the user's Codex home and are not copied into this repository. The repository records only non-secret architecture, role, acceptance, and rollback contracts.

## Continuous Technology Evolution

The monthly `bravecow-harness` automation exists to keep the Harness useful while AI technology changes quickly. Each run scouts first-party model and agent-runtime releases, tool calling, MCP, context engineering, memory and RAG, evaluation and observability, browser or Computer Use, and security or supply-chain improvements.

Candidates move through one evidence loop:

1. Discover from official documentation, repositories, releases, tags, commits, or published research.
2. Identify the current-machine gap and the expected measurable benefit.
3. Run the smallest isolated compatibility and safety experiment.
4. Measure capability, correctness, stability, speed, token cost, security, and maintainability.
5. Adopt only changes with a verifiable net benefit; otherwise defer or reject them with evidence.
6. Verify end to end and preserve a rollback point before release.

"New" is not the same as "useful here." The monthly loop keeps those decisions separate.

## Memory and RAG Control Plane

`memory-tidy` maintains durable Markdown. Codex manages its own native memory; Harness supports direct Markdown reads and bounded local FTS5 retrieval.

- Markdown remains canonical.
- SQLite FTS5 is the deterministic default retrieval path.
- Prompts, local paths, secrets, waterlines, index state, and user data stay local.

## Ownership and Audit Boundary

The Harness audit reports an automation's id, display name, status, role, and ownership boundary without copying its prompt. Known core components are classified explicitly; unrelated local automations remain external.

The monthly evolution subsystem audits schedule and prompt contracts, data boundaries, encoding and secret gates, deduplication and waterlines, passive health, degradation latency, dependency provenance, token and latency cost, backup, and rollback. This makes the automation layer part of the Harness without turning private runtime state into repository content.

## Evidence boundaries

The audit now records identity matching, schedule shape, execution-target presence, prompt size, definition hash and retained-state presence. These are static checks: they do not prove a scheduler ran, a prompt was followed, or a token budget was met. A state-only directory after automation retirement is retained history, not an active scheduled task. Actual scheduler outcomes and billed usage remain `not-observed` until a runtime supplies them.

The live app definition is the only schedule authority. This repository stores neither a schedule copy nor private prompt text. When no automation mutation is needed, preserve the definition byte-for-byte. Backups and rollback receipts remain local. Local monthly evidence is deduplicated by run date and baseline ref; memory/index maintenance uses content hashes and transactionally committed metadata. There is no graph synchronization watermark after Graphiti retirement.

## Retrieval degradation contract

Known Markdown reads skip SQLite entirely. Ordinary queries use FTS5; an unavailable, corrupt or locked index falls back to a literal Markdown scan capped at 64 candidate documents and 4 MiB of source bytes. SQLite lock waits are capped at 250 ms per connection. Short queries that cannot match trigram tokens also use this fallback when FTS5 returns no hits.

Fallback results expose truncation, skipped files and read volume; absence of hits in a bounded scan is not proof that no fact exists. Invalid UTF-8 is skipped during fallback rather than silently repaired. A missing or unreadable canonical root cannot prune the existing index. Canonical files are never written by retrieval, and a corrupt index is preserved for deliberate recovery. No network, graph service or vector dependency is started.
