# Security Notes

This repository is designed to be public-safe. It intentionally excludes private runtime state.

## Excluded by Design

- API keys and tokens.
- Browser profiles, cookies, and login sessions.
- Password vault files and account indexes.
- Personal profile memory from another machine.
- Local automations and cron/heartbeat task definitions.
- Marketplace caches and downloaded plugin runtimes.
- Vendored third-party code snapshots.

## Before Publishing Changes

Run:

```powershell
python .\tests\validate_package.py
```

The validator checks for common private path fragments, token-looking strings, and required package files. It is not a complete secret scanner, but it catches the mistakes this harness is most likely to make.

Run the isolated installer smoke test as well:

```powershell
powershell -ExecutionPolicy Bypass -File .\tests\smoke_install.ps1
```

On macOS, run `sh ./tests/smoke_install_macos.sh`.

The smoke test installs only into a uniquely named temporary directory and removes that directory after verification.

## Safe Update Boundaries

- `-UpdateRuntime` updates scripts and the managed introspection skill.
- `-MigrateConfig` updates agent templates and marked AGENTS blocks.
- Missing memory files may be initialized, but existing memory is preserved by default.
- `-ReplaceUserData` is the only operation allowed to replace existing memory templates.
- Any existing managed file is backed up before overwrite; `-DryRun` previews the plan without writes.
- `-Force` is a non-destructive compatibility alias and never implies user-data replacement.
- The ZCode onboarding launcher automates only the documented new-task shortcut after positively activating the ZCode process. It does not type into an unknown foreground app.
- macOS may require explicit Accessibility permission before ZCode can receive the automated `Command+N` shortcut.
- Windows + ZCode downloads only the exact `desktop-control-for-windows` commit recorded in `external-components.lock.json`, verifies `HEAD`, installs dependencies in the extension's own `.venv`, and writes a provenance receipt.
- The post-install course validates the controller with `--help` only. It does not take screenshots, read window titles, or perform mouse/keyboard actions.

## Installing Third-Party Resources

Use `vendor_skill.py` to create a manifest in `~/.bravecow/harness/vendor/<slug>` before activating an external skill, plugin, framework, runtime, or model.

Activation should be a separate step after review.

The user-requested BraveCow Windows Computer Use integration is a documented exception to the generic intake flow. Its author, repository, license, platform, runtime, and immutable commit are reviewed in the repository lock; the installer activates it only for Windows + ZCode. macOS and Codex do not receive this external adapter.
