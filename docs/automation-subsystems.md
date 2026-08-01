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

The global `session-log-graphiti-sync` automation is the Harness global memory/RAG indexing subsystem. `memory-tidy` is its durable Markdown maintenance companion. Project-scoped Markdown-to-RAG jobs are managed extensions when they follow the same contracts.

- Markdown remains canonical.
- SQLite FTS5 is the deterministic default retrieval path.
- Graphiti, vector, and graph stores are optional indexes used only when semantic or temporal relationships add value.
- Ordinary tasks do not start Docker or wait for Graphiti recovery; they degrade immediately to Markdown/FTS5.
- Explicit synchronization may perform one bounded health recovery, deduplicate by stable source and content identity, and must not delete Graphiti data.
- Prompts, local paths, secrets, waterlines, index state, and user data stay local.

## Ownership and Audit Boundary

The Harness audit reports an automation's id, display name, status, role, and ownership boundary without copying its prompt. Known core components are classified explicitly; project RAG indexes can be classified as managed extensions; unrelated local automations remain external.

The monthly evolution subsystem audits schedule and prompt contracts, data boundaries, encoding and secret gates, deduplication and waterlines, passive health, degradation latency, dependency provenance, token and latency cost, backup, and rollback. This makes the automation layer part of the Harness without turning private runtime state into repository content.
