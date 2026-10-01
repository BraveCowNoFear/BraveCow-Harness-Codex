# BraveCow Harness Audit

Generated: 2026-10-01T09:01:49.923464+00:00

## Runtime

- Host OS: `Windows AMD64`
- Harness version: `0.12.0`
- Shared harness home: `%USERPROFILE%\.bravecow\harness`
- Shared memory home: `%USERPROFILE%\.bravecow\memories`
- Codex home: `%USERPROFILE%\.codex`
- ZCode home: `%USERPROFILE%\.zcode`
- Model: `gpt-6.1-sol`
- Reasoning effort: `high`
- Approval policy: `never`
- Sandbox mode: `danger-full-access`
- Config syntax gate: `pass`
- Config runtime gate: `pass`
- Codex CLI: `codex-cli 0.159.2`
- Last measured startup prompt: `8700` tokens
- Skill descriptions: `2749` tokens across `52` catalog entries
- Prompt probe mode: `native`

## Memory Entry Points

- `PROFILE.md`: present
- `ACTIVE.md`: present
- `MEMORY_POLICY.md`: present
- `SESSION_LOG.md`: present
- `LEARNINGS.md`: present
- `ERRORS.md`: present
- `FEATURE_REQUESTS.md`: present
- SQLite FTS5 index: `ready`
- Indexed Markdown files: `13`
- Indexed sections: `2167`
- Incremental updates this run: `4`
- Retrieval router result: `fts`
- Retrieval degradation latency: `13.67 ms`
- Durable-memory write gate: `accept`; writes performed: `False`

## Agent Profiles

- `critic`
- `default`
- `explorer`
- `release_manager`
- `researcher`
- `visual_qa`
- `worker`
- ZCode custom agents: `none`

## Automations

- Harness components: `2/6`
- `automation-3` — `视频生产每日任务`; role: `external-local-automation`; boundary: `external`; status: `ACTIVE`
- `automation-4` — `社区总管每日任务`; role: `external-local-automation`; boundary: `external`; status: `ACTIVE`
- `automation-5` — `视频发布每日任务`; role: `external-local-automation`; boundary: `external`; status: `ACTIVE`
- `bravecow-harness` — `BraveCow Harness 月度技术侦察与升级`; role: `continuous-technology-evolution`; boundary: `core`; status: `ACTIVE`
- `memory-tidy` — `Memory Tidy`; role: `durable-memory-maintenance`; boundary: `core`; status: `ACTIVE`
- `session-log-graphiti-sync` — `session-log-graphiti-sync`; role: `external-local-automation`; boundary: `external`; status: `missing-config`

## Skill Coverage

- Shared skills: `19`
- Codex skill entries: `55`
- ZCode skill entries: `4`
- OpenClaw skill entries: `25`
- Valid shared skills: `19`
- Valid Codex skills: `52`
- Valid ZCode skills: `4`
- Valid OpenClaw skills: `25`
- Unique discoverable real paths: `60`
- Entries declaring a version: `8`
- Trigger contract: `0/50 failed (0.0%)`; passed: `True`
- Harness lock skills: `60`
- Harness lock plugins: `36`
- Harness lock components: `6`
- Previous-lock drift snapshot: `ready`; changes: `27`
- Provenance + rollback coverage: `60/60 (100.0%)`
- Skills with detected license files: `18/60`
- Skills with recorded passing verification: `1/60`

## Codex Plugin Cache

Remote install markers and exact config ids choose one resolved package per logical plugin. Other cache entries remain rollback evidence.

- Cached plugin packages: `36`
- Plugin-provided skills: `110`
- Packages with apps: `22`
- Packages with MCP content: `0`
- Invalid plugin manifests: `0`
- Enabled by config: `15`
- Installed through remote markers: `16`
- Resolved logical plugins: `30`
- Resolved plugin skill entries: `87`
- Cache-only packages: `5`
- `windows-computer-use@0.40.0` from `brave-cow-windows-tools`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `windows-computer-use`
- `browser@26.928.31416` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `none`
- `chrome@26.928.31416` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `none`
- `code-review@26.928.31416` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `none`
- `codex-app-tools@0.1.5` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `none`
- `computer-use@26.928.31416` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `computer-use`
- `unified-computer-use@26.928.31416` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `none`
- `visualize@1.0.45` from `openai-bundled`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `visualize`
- `canva@1.0.2` from `openai-curated`; state: `cache-only`; resolved: `False`; reason: `unresolved`; skills: `canva-branded-presentation, canva-resize-for-all-social-media, canva-translate-design`
- `github@0.1.6` from `openai-curated`; state: `cache-only`; resolved: `False`; reason: `unresolved`; skills: `gh-address-comments, gh-fix-ci, github, yeet`
- `google-calendar@1.2.6` from `openai-curated`; state: `superseded-config-cache`; resolved: `False`; reason: `superseded-by:1.2.7@openai-curated-remote`; skills: `none`
- `notion@0.1.5` from `openai-curated`; state: `cache-only`; resolved: `False`; reason: `unresolved`; skills: `notion-knowledge-capture, notion-meeting-intelligence, notion-research-documentation, notion-spec-to-implementation`
- `outlook-calendar@0.1.0` from `openai-curated`; state: `cache-only`; resolved: `False`; reason: `unresolved`; skills: `outlook-calendar, outlook-calendar-daily-brief, outlook-calendar-free-up-time, outlook-calendar-group-scheduler, outlook-calendar-meeting-prep, outlook-calendar-shared-calendars`
- `outlook-email@0.1.0` from `openai-curated`; state: `cache-only`; resolved: `False`; reason: `unresolved`; skills: `outlook-email, outlook-email-inbox-triage, outlook-email-reply-drafting, outlook-email-shared-mailboxes, outlook-email-subscription-cleanup, outlook-email-task-extraction`
- `slack@0.1.7` from `openai-curated`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `none`
- `app-69312da8e4dc81919370cb86fd172b6c@10.0.0` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `adobe-batch-edit-photos, adobe-create-mockups, adobe-create-social-variations, adobe-design-from-template, adobe-edit-quick-cut, adobe-fonts, adobe-retouch-portraits`
- `app-6938a94a61d881918ef32cb999ff937c@1.0.0` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `canva@17.0.1` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `data-analytics@1.0.11` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `analyze-data-quality, build-dashboard, build-report, convert-to-doc, convert-to-slides, create-data-context, design-kpis, gather-business-context, index, jupyter-notebooks, kpi-reporting, market-sizing, metric-diagnostics, product-business-analysis, publish-artifact-to-sites, report-to-pdf, schedule-refresh-jobs, share-artifact-summary, validate-data, visualize-data`
- `github@0.1.12-5f7cd798dc99` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `gmail@0.1.10` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `google-calendar@1.2.7` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `google-contacts@1.0.0` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `none`
- `google-drive@0.1.16` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `google-docs, google-drive, google-drive-comments, google-sheets, google-slides`
- `notion@0.1.8` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `notion-knowledge-capture, notion-meeting-intelligence, notion-research-documentation, notion-spec-to-implementation`
- `openai-templates@0.1.1` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `artifact-template-analytics-dashboard, artifact-template-business-review, artifact-template-design-report, artifact-template-experiment-analysis, artifact-template-financial-budget, artifact-template-investment-committee-memo, artifact-template-legal-memorandum, artifact-template-market-trends-report, artifact-template-minimal-letterhead, artifact-template-operating-calendar, artifact-template-operating-review, artifact-template-project-kickoff, artifact-template-project-tracker, artifact-template-sales-pipeline, artifact-template-simple-dark-mode, artifact-template-simple-light-mode, artifact-template-strategy-memorandum, artifact-template-system-design, artifact-template-team-alignment, artifact-template-three-statement-forecast`
- `pages@0.1.18` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `maintain-space, manage-schedules, organize-space, write-page`
- `plugin-management@0.1.0` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `plugin-management`
- `product-design@0.1.56` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `audit, design-qa, get-context, ideate, image-to-code, index, research, share, url-to-code, user-context`
- `sites@0.1.75` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `sites-building, sites-hosting, sites-mcp, sites-preview-troubleshooting`
- `work-pets@0.1.6` from `openai-curated-remote`; state: `resolved-remote-install`; resolved: `True`; reason: `remote-install-marker`; skills: `create-pet, pets, update-pet`
- `documents@26.909.12148` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `documents`
- `pdf@26.909.12148` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `pdf`
- `presentations@26.909.12148` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `presentations`
- `spreadsheets@26.909.12148` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `excel-live-control, spreadsheets`
- `template-creator@26.909.12148` from `openai-primary-runtime`; state: `resolved-config`; resolved: `True`; reason: `exact-config-id`; skills: `template-creator`

## Pinned Components

- `codex-cli`: declared `0.159.2`, installed `0.159.2`, state `drift`, rollback `34549ded6e2aee87c911c62d025e52e26c488683d0f489cd68f756baef1a6df6`
- `zcode-desktop`: declared `unknown`, installed `unknown`, state `installed`, rollback `unknown`
- `openclaw`: declared `2026.6.5`, installed `2026.6.5`, state `drift`, rollback `2026.6.5`
- `browser-harness`: declared `0.1.8`, installed `0.1.8`, state `installed`, rollback `aa2ecb4e4eb430268eeeb65df5672f50406288aa`
- `meta-harness`: declared `0.4`, installed `0.4`, state `installed`, rollback `eafb74711f6ef54270b78835cf809b24ad650a9f`
- `everything-claude-code-active-slice`: declared `2.0.0-rc.1`, installed `v2.1.0-frontmatter-compatible`, state `targeted-local-patch`, rollback `37d319830d05c3c05786536333915d2712eb4088`

## Shared Mirrors

- Mirrored into Codex via shared path: `19`
- Mirrored into ZCode via shared path: `3`
- Mirrored into OpenClaw via shared path: `18`

## Missing Shared Links

- Missing in Codex: `none`
- Missing in ZCode: `agent-introspection-debugging, bilibili-subtitle, bilibili-video-download, codebase-onboarding, context-budget, find-skills, guizang-ppt-skill, harness, local-qwen-tts, nextjs-app-router-patterns, remotion-best-practices, shadcn, tailwind-design-system, text-to-speech, vercel-react-best-practices, web-design-engineer`
- Missing in OpenClaw: `bravecow-onboarding`

## Shared Skill Shadows

- Codex local copies of shared skill ids: `none`
- ZCode local copies of shared skill ids: `none`
- OpenClaw local copies of shared skill ids: `none`

## Vendor Quarantine

- Quarantined candidates: `27`
- Pending review: `19`
- Vendor dirs missing manifest: `chatgpt2api, codex-chatgpt-web, hermes-luna-free, will-tibo-reset`
- `agents-md-format`: `specification` / `pending` / `quarantined`
- `aider`: `framework` / `pending` / `quarantined`
- `archon`: `framework` / `quarantined` / `vendor-only`
- `automem-mcp`: `plugin` / `pending` / `quarantined`
- `browser-use-browser-harness`: `runtime-skill` / `already-installed` / `active-existing-junction`
- `claude-code-subagents-hooks`: `framework` / `pending` / `quarantined`
- `claude-task-master`: `framework` / `pending` / `quarantined`
- `cline-mcp-marketplace`: `marketplace` / `pending` / `quarantined`
- `comfyui`: `runtime` / `pending` / `quarantined`
- `deepseek-harness`: `runtime` / `reviewed` / `active-isolated-diagnostic`
- `deepseek-official-harness`: `runtime` / `reviewing` / `quarantined`
- `deepseek-tui`: `runtime` / `reviewed` / `active-global-runtime`
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
- Treat Harness-owned automation definitions as private local runtime state while auditing their non-secret role, health, cost, and rollback contract.
- Treat the generated harness lock as observation evidence, not authorization to auto-update.
- Treat this report as local state, not a portable artifact.
