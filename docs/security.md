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

The smoke test installs only into a uniquely named temporary directory and removes that directory after verification.

## Installing Third-Party Resources

Use `vendor_skill.py` to create a manifest in `~/.codex/harness/vendor/<slug>` before activating an external skill, plugin, framework, runtime, or model.

Activation should be a separate step after review.
