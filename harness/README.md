# BraveCow Harness Workspace

This directory is the local control plane for Codex harness maintenance.

## Layout

- `catalog/`: inventory, `harness.lock.json`, plugin enabled/cache-only states, and intake metadata.
- `index/`: disposable local SQLite FTS5 indexes; Markdown remains canonical.
- `reports/`: point-in-time audit reports.
- `scripts/`: local audit and maintenance scripts.
- `vendor/`: quarantined third-party resources before activation.

## Suggested Workflow

Refresh the skill and cached-plugin inventory:

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\build_skill_inventory.py"
```

Generate the audit report:

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\harness_audit.py"
```

Search canonical Markdown memory without starting external services:

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\memory_search.py" "query"
```

Validate that the installed Codex CLI can semantically parse the current config:

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\config_gate.py"
```

Prepare a quarantined vendor manifest:

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\vendor_skill.py" --title "Example" --source-url "https://example.com" --kind skill
```

Review before activation. Do not auto-enable third-party code merely because it was cataloged.

Plugin cache results show what Codex downloaded. `enabled-by-config` is reported separately from `cache-only`, and neither state authorizes automatic updates.
