# BraveCow Harness Workspace

This directory is the shared local control plane for Codex and ZCode Harness maintenance on Windows and macOS.

## Layout

- `catalog/`: inventory, `harness.lock.json`, the external-component source lock, install receipts, resolved namespaced plugin skills, upstream observations, and intake metadata.
- `index/`: disposable local SQLite FTS5 indexes; Markdown remains canonical.
- `reports/`: point-in-time audit reports.
- `scripts/`: local audit and maintenance scripts.
- `vendor/`: quarantined third-party resources before activation.

## Automation Control Plane

Harness-owned automations are private local runtime state, so the installer does not copy their definitions or prompts. The audit still classifies their non-secret role and boundary. The monthly evolution automation continuously scouts and safely applies useful AI advances; the global memory-to-Graphiti automation and durable Markdown maintenance form the memory/RAG subsystem. See `docs/automation-subsystems.md` in the repository for the full contract.

## Suggested Workflow

Refresh the skill and cached-plugin inventory:

```powershell
python "$env:USERPROFILE\.bravecow\harness\scripts\build_skill_inventory.py"
```

Generate the audit report:

```powershell
python "$env:USERPROFILE\.bravecow\harness\scripts\harness_audit.py"
```

Route a memory query and receive a bounded evidence pack without starting external services:

```powershell
python "$env:USERPROFILE\.bravecow\harness\scripts\memory_router.py" "query"
```

Validate a durable-memory candidate without writing it:

```powershell
Get-Content .\candidate.json | python "$env:USERPROFILE\.bravecow\harness\scripts\memory_write_gate.py"
```

To enable deterministic trigger regression, copy `skill-contracts.example.json` to `skill-contracts.json`, replace the examples with machine-relevant skills, then run:

```powershell
python "$env:USERPROFILE\.bravecow\harness\scripts\skill_contracts.py"
```

Each semantic inventory change preserves one previous lock snapshot. Compare it read-only (for example from a weekly task):

```powershell
python "$env:USERPROFILE\.bravecow\harness\scripts\lock_diff.py"
```

Validate that the installed Codex CLI can semantically parse the current config:

```powershell
python "$env:USERPROFILE\.bravecow\harness\scripts\config_gate.py"
```

Prepare a quarantined vendor manifest:

```powershell
python "$env:USERPROFILE\.bravecow\harness\scripts\vendor_skill.py" --title "Example" --source-url "https://example.com" --kind skill
```

Review before activation. Do not auto-enable third-party code merely because it was cataloged.

The Windows + ZCode installer has one explicit managed exception: it fetches the immutable `desktop-control-for-windows` revision from `external-components.lock.json`, verifies the Git commit, installs the ZCode adapter into `~/.zcode/skills/bravecow-windows-computer-use`, keeps dependencies in that skill's `.venv`, and records `catalog/zcode-computer-use-install.json`. It is never installed for Codex or macOS.

Plugin resolution prefers an explicit remote-install marker, then an exact enabled config id. Superseded and cache-only packages remain visible as rollback evidence. No observed state authorizes automatic updates.

For a monthly audit, copy `upstream-observations.example.json` to the active catalog as `upstream-observations.json` and populate it only from official first-party sources. The inventory compares those observations with installed versions but never executes an upgrade.

Measure the actual startup prompt without editing `config.toml`:

```powershell
python "$env:USERPROFILE\.bravecow\harness\scripts\measure_prompt_baseline.py"
```
