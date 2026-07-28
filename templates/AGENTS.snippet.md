<!-- BraveCow Harness Codex: start -->
## BraveCow Harness Codex

Use the global memory directory at `%USERPROFILE%\.codex\memories`.

Before substantial tasks, read `PROFILE.md` and `ACTIVE.md`, then apply them before analysis.

Memory retrieval:
- Markdown is canonical. Read a known file directly; otherwise use `%USERPROFILE%\.codex\harness\scripts\memory_search.py`.
- Use Graphiti only for temporal/entity relationship queries and only when already healthy. Never block an ordinary task on Docker or service self-heal; fall back immediately to Markdown/FTS5.

Write reusable entries according to `MEMORY_POLICY.md`: session notes to `SESSION_LOG.md`, learnings to `LEARNINGS.md`, unexpected errors to `ERRORS.md`, and missing capabilities to `FEATURE_REQUESTS.md`.

Log only when the result is reusable or likely to recur, especially after unexpected tool failures, user corrections, missing capabilities, external tool/API behavior differences, or validated workarounds.

Promote recurring cross-task rules into concise `ACTIVE.md`, and only durable user identity/preferences into `PROFILE.md`. Do not edit this `AGENTS.md` unless the user explicitly requests a harness or instruction update.

Harness maintenance:
- Use the `agent-harness-introspect` skill for local Codex harness audits, skill drift checks, and safe upgrade planning.
- Treat `%USERPROFILE%\.codex\plugins\cache` as cached package evidence, not proof that a plugin is enabled.
- Keep private runtime state, API keys, vault files, browser sessions, and local automations out of Git.
- Catalog third-party resources in `%USERPROFILE%\.codex\harness\vendor` before activation.
<!-- BraveCow Harness Codex: end -->
