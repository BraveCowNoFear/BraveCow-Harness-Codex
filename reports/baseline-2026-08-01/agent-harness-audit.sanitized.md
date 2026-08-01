# Agent Harness Audit

Generated: 2026-08-01T09:13:22.878414+00:00

## Runtime

- Model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Approval policy: `never`
- Sandbox mode: `danger-full-access`
- Config syntax gate: `pass`
- Config runtime gate: `runtime-schema-mismatch`
- Codex CLI: `codex-cli 0.130.0-alpha.5`
- Config gate diagnostic: `Error: <local-path>:7:16: unknown variant `priority`, expected `fast` or `flex` | unknown variant `priority`, expected `fast` or `flex``

## Memory Entry Points

- `PROFILE.md`: present
- `ACTIVE.md`: present
- `MEMORY_POLICY.md`: present
- `SESSION_LOG.md`: present
- `LEARNINGS.md`: present
- `ERRORS.md`: present
- `FEATURE_REQUESTS.md`: present
- SQLite FTS5 index: `ready`
- Indexed Markdown files: `12`
- Indexed sections: `969`
- Incremental updates this run: `1`
- Retrieval router result: `fts`
- Retrieval degradation latency: `262.52 ms`
- Durable-memory write gate: `accept`; writes performed: `False`

## Agent Profiles

- `default`
- `explorer`
- `worker`

## Automations

- `automation`
- `bravecow-harness`
- `memory-tidy`
- `outlook-browser-email`
- `p5`
- `session-log-graphiti-sync`
- `work-workspace-md-into-graphiti`

## Skill Coverage

- Shared skills: `18`
- Codex skill entries: `50`
- OpenClaw skill entries: `25`
- Valid shared skills: `18`
- Valid Codex skills: `47`
- Valid OpenClaw skills: `25`
- Unique discoverable real paths: `54`
- Entries declaring a version: `8`
- Trigger contract: `2/50 failed (4.0%)`; passed: `False`
- Harness lock skills: `54`
- Harness lock plugins: `24`
- Harness lock components: `4`
- Previous-lock drift snapshot: `ready`; changes: `13`
- Provenance + rollback coverage: `54/54 (100.0%)`
- Skills with detected license files: `10/54`
- Skills with recorded passing verification: `1/54`

## Codex Plugin Cache

Remote install markers and exact config ids choose one resolved package per logical plugin. Other cache entries remain rollback evidence.

- Cached plugin packages: `24`
- Plugin-provided skills: `89`
- Packages with apps: `14`
- Packages with MCP content: `1`
- Invalid plugin manifests: `0`
- Enabled by config: `14`
- Installed through remote markers: `8`
- Resolved logical plugins: `19`
- Cache-only packages: `2`
- `windows-computer-use@0.40.0` from `brave-cow-windows-tools`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `windows-computer-use`
- `browser@26.727.51351` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `control-in-app-browser`
- `chrome@26.727.51351` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `control-chrome`
- `computer-use@26.727.51351` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `computer-use`
- `sites@0.1.33` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `sites-building, sites-hosting`
- `visualize@1.0.16` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `visualize`
- `canva@1.0.2` from `openai-curated`; state: `superseded-config-cache`; resolved: `False`; reason: `superseded-by:13.0.0@openai-curated-remote`; skills: `canva-branded-presentation, canva-resize-for-all-social-media, canva-translate-design`
- `github@0.1.6` from `openai-curated`; state: `superseded-config-cache`; resolved: `False`; reason: `superseded-by:0.1.8-2841cf9749ae@openai-curated-remote`; skills: `gh-address-comments, gh-fix-ci, github, yeet`
- `notion@0.1.5` from `openai-curated`; state: `superseded-config-cache`; resolved: `False`; reason: `superseded-by:0.1.7@openai-curated-remote`; skills: `notion-knowledge-capture, notion-meeting-intelligence, notion-research-documentation, notion-spec-to-implementation`
- `outlook-calendar@0.1.0` from `openai-curated`; state: `cache-only`; resolved: `False`; reason: `unresolved`; skills: `outlook-calendar, outlook-calendar-daily-brief, outlook-calendar-free-up-time, outlook-calendar-group-scheduler, outlook-calendar-meeting-prep, outlook-calendar-shared-calendars`
- `outlook-email@0.1.0` from `openai-curated`; state: `cache-only`; resolved: `False`; reason: `unresolved`; skills: `outlook-email, outlook-email-inbox-triage, outlook-email-reply-drafting, outlook-email-shared-mailboxes, outlook-email-subscription-cleanup, outlook-email-task-extraction`
- `app-69312da8e4dc81919370cb86fd172b6c@5.0.0` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `app-6938a94a61d881918ef32cb999ff937c@1.0.0` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `canva@13.0.0` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `data-analytics@0.2.8-13ceeea1f599` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `analyze-data-quality, build-dashboard, build-report, create-data-context, design-kpis, gather-business-context, index, jupyter-notebooks, kpi-reporting, market-sizing, metric-diagnostics, product-business-analysis, publish-artifact-to-sites, validate-data, visualize-data`
- `github@0.1.8-2841cf9749ae` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `gh-address-comments, gh-fix-ci, github, yeet`
- `notion@0.1.7` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `notion-knowledge-capture, notion-meeting-intelligence, notion-research-documentation, notion-spec-to-implementation`
- `openai-templates@0.1.1` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `artifact-template-analytics-dashboard, artifact-template-business-review, artifact-template-design-report, artifact-template-experiment-analysis, artifact-template-financial-budget, artifact-template-investment-committee-memo, artifact-template-legal-memorandum, artifact-template-market-trends-report, artifact-template-minimal-letterhead, artifact-template-operating-calendar, artifact-template-operating-review, artifact-template-project-kickoff, artifact-template-project-tracker, artifact-template-sales-pipeline, artifact-template-simple-dark-mode, artifact-template-simple-light-mode, artifact-template-strategy-memorandum, artifact-template-system-design, artifact-template-team-alignment, artifact-template-three-statement-forecast`
- `product-design@0.1.52` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `audit, design-qa, get-context, ideate, image-to-code, index, research, share, url-to-code, user-context`
- `documents@26.731.11130` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `documents`
- `pdf@26.731.11130` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `pdf`
- `presentations@26.731.11130` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `presentations`
- `spreadsheets@26.731.11130` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `excel-live-control, spreadsheets`
- `template-creator@26.731.11130` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `template-creator`

## Pinned Components

- `browser-harness`: declared `0.1.8`, installed `0.1.8`, state `installed`, rollback `aa2ecb4e4eb430268eeeb65df5672f50406288aa`
- `graphiti-core`: declared `0.29.1`, installed `0.28.2`, state `drift`, rollback `b051b46ee3e71e7ebab64e34b2adde7bf73248a5`
- `meta-harness`: declared `0.4`, installed `0.4`, state `installed`, rollback `eafb74711f6ef54270b78835cf809b24ad650a9f`
- `everything-claude-code-active-slice`: declared `2.0.0-rc.1`, installed `v2.1.0-frontmatter-compatible`, state `targeted-local-patch`, rollback `37d319830d05c3c05786536333915d2712eb4088`

## Shared Mirrors

- Mirrored into Codex via shared path: `18`
- Mirrored into OpenClaw via shared path: `18`

## Missing Shared Links

- Missing in Codex: `none`
- Missing in OpenClaw: `none`

## Shared Skill Shadows

- Codex local copies of shared skill ids: `none`
- OpenClaw local copies of shared skill ids: `none`

## Vendor Quarantine

- Quarantined candidates: `24`
- Pending review: `19`
- Vendor dirs missing manifest: `none`
- `agents-md-format`: `specification` / `pending` / `quarantined`
- `aider`: `framework` / `pending` / `quarantined`
- `archon`: `framework` / `quarantined` / `vendor-only`
- `automem-mcp`: `plugin` / `pending` / `quarantined`
- `browser-use-browser-harness`: `runtime-skill` / `already-installed` / `active-existing-junction`
- `claude-code-subagents-hooks`: `framework` / `pending` / `quarantined`
- `claude-task-master`: `framework` / `pending` / `quarantined`
- `cline-mcp-marketplace`: `marketplace` / `pending` / `quarantined`
- `comfyui`: `runtime` / `pending` / `quarantined`
- `everything-claude-code`: `framework` / `partially-reviewed` / `selective-activation`
- `google-adk`: `framework` / `pending` / `quarantined`
- `goose-aaif`: `framework` / `pending` / `quarantined`
- `local-skills-mcp`: `tooling` / `pending` / `quarantined`
- `mcp-registry-official`: `registry` / `pending` / `quarantined`
- `meta-harness`: `skill` / `reviewed` / `active-shared-skill-junction`
- `mini-swe-agent`: `framework` / `pending` / `quarantined`
- `netresearch-claude-code-marketplace`: `marketplace` / `pending` / `quarantined`
- `openai-agents-sdk`: `framework` / `pending` / `quarantined`
- `opencode`: `framework` / `pending` / `quarantined`
- `openhands`: `framework` / `pending` / `quarantined`
- `superclaude-framework`: `framework` / `pending` / `quarantined`
- `tech-leads-club-agent-skills`: `marketplace` / `pending` / `quarantined`
- `wan2.2`: `model` / `pending` / `quarantined`
- `wshobson-agents`: `marketplace` / `quarantined` / `vendor-only`

## Baseline Guidance

- Keep private runtime state out of Git.
- Prefer shared skills and runtime junctions over copied duplicates.
- Catalog external resources before activation.
- Use Markdown plus SQLite FTS5 as the default local memory path; keep graph/vector retrieval optional.
- Treat the generated harness lock as observation evidence, not authorization to auto-update.
- Treat this report as local state, not a portable artifact.
