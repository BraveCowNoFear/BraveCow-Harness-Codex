<!-- BraveCow Harness: start -->
## BraveCow Harness

Use the shared memory directory at `~/.bravecow/memories`.

Before substantial tasks, read `PROFILE.md` and `ACTIVE.md`, then apply them before analysis.

Memory retrieval:
- Markdown is canonical. Read a known file directly; otherwise use `~/.bravecow/harness/scripts/memory_search.py`.
- Use Graphiti only for temporal or entity-relationship queries and only when already healthy. Never block an ordinary task on Docker or service repair; fall back immediately to Markdown/FTS5.

Write reusable entries according to `MEMORY_POLICY.md`: session notes to `SESSION_LOG.md`, learnings to `LEARNINGS.md`, unexpected errors to `ERRORS.md`, and missing capabilities to `FEATURE_REQUESTS.md`.

Log only reusable or recurring findings, especially after unexpected tool failures, user corrections, missing capabilities, external tool behavior differences, or validated workarounds.

Promote recurring cross-task rules into concise `ACTIVE.md`, and only durable user identity or preferences into `PROFILE.md`. Do not edit this `AGENTS.md` unless the user explicitly requests a Harness or instruction update.

Harness maintenance:
- Use the `agent-harness-introspect` skill for BraveCow Harness audits, Codex/ZCode skill drift checks, and safe upgrade planning.
- Treat Codex plugin caches as cached package evidence, not proof that a plugin is enabled.
- Keep private runtime state, API keys, vault files, browser sessions, and local automations out of Git.
- Catalog third-party resources in `~/.bravecow/harness/vendor` before activation.
<!-- BraveCow Harness: end -->
