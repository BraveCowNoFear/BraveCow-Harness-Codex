# BraveCow Harness Workspace

This directory is the local control plane for Codex harness maintenance.

## Layout

- `catalog/`: generated skill/plugin inventories and import backlog metadata.
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

Prepare a quarantined vendor manifest:

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\vendor_skill.py" --title "Example" --source-url "https://example.com" --kind skill
```

Review before activation. Do not auto-enable third-party code merely because it was cataloged.

Plugin cache results show what Codex has downloaded locally. They do not prove that a plugin is currently enabled.
