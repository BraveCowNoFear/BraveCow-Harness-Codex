<!-- BraveCow Harness Codex: start -->
## BraveCow Harness Codex

Use the global memory directory at `%USERPROFILE%\.codex\memories`.

Before starting substantial tasks:
1. Read `%USERPROFILE%\.codex\memories\PROFILE.md` if it exists.
2. Read `%USERPROFILE%\.codex\memories\ACTIVE.md` if it exists.
3. Apply those preferences before analyzing the request.

Write reusable entries by type:
- `%USERPROFILE%\.codex\memories\LEARNINGS.md` for learnings, corrections, knowledge gaps, and best practices.
- `%USERPROFILE%\.codex\memories\ERRORS.md` for unexpected errors and debugging notes.
- `%USERPROFILE%\.codex\memories\FEATURE_REQUESTS.md` for missing capabilities the user wants.

Log only when the result is reusable or likely to recur, especially after unexpected tool failures, user corrections, missing capabilities, external tool/API behavior differences, or validated workarounds.

Promotion rules:
1. If a pattern recurs or is broadly useful across tasks, promote it into `%USERPROFILE%\.codex\memories\ACTIVE.md`.
2. Keep `ACTIVE.md` concise and current.
3. Promote into `PROFILE.md` only for durable user preferences, identity facts, or stable working style.
4. Do not edit this `AGENTS.md` automatically unless the user explicitly asks or the current task is to install/update the harness itself.

Harness maintenance:
- Use the `agent-harness-introspect` skill for local Codex harness audits, skill drift checks, and safe upgrade planning.
- Keep private runtime state, API keys, vault files, browser sessions, and local automations out of Git.
- Catalog third-party resources in `%USERPROFILE%\.codex\harness\vendor` before activation.
<!-- BraveCow Harness Codex: end -->

