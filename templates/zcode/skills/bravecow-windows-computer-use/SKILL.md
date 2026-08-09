---
name: bravecow-windows-computer-use
description: Control visible Windows desktop applications from ZCode when no reliable API, CLI, browser, or accessibility path exists. Use only on Windows in ZCode for screenshots, windows, mouse, keyboard, clipboard, image matching, and verified desktop actions through the bundled local controller.
---

# BraveCow Windows Computer Use for ZCode

This is the ZCode compatibility adapter for the pinned
[`BraveCowNoFear/desktop-control-for-windows`](https://github.com/BraveCowNoFear/desktop-control-for-windows)
source installed by BraveCow Harness. It runs locally on Windows and does not require ZCode to provide a delegation or Computer Use feature.

## Boundaries

- Use this adapter only in ZCode on Windows. Codex already has its own Computer Use capability; macOS is not supported by this Windows controller.
- Prefer a reliable API, command, browser tool, or application-specific integration before visible desktop control.
- During the beginner course, demonstrate installation and capability with `--help`. Do not click, type, capture the screen, or inspect window titles merely to prove the extension exists.
- Treat screenshots, clipboard contents, and window titles as potentially sensitive.

## Runtime

Run commands from this skill directory with the isolated interpreter installed by Harness:

```powershell
& .\.venv\Scripts\python.exe .\scripts\ui_control.py --help
```

Read `references/control-api.md` for complete syntax. The original `references/subagent-workflow.md` describes the Codex worker pattern and is not mandatory in ZCode. If ZCode offers a suitable isolated agent, it may be used, but missing delegation must not block this adapter.

## Safe workflow

1. Clarify the exact target app, desired outcome, and whether any external or irreversible action is allowed.
2. Start the warm progress overlay before touching the desktop.
3. Acquire the global UI lock and keep its token private.
4. Inspect the current state with a minimal status call or screenshot while holding the lock.
5. Activate the intended window and use the smallest reliable action. Prefer shortcuts and clipboard paste over coordinates.
6. Use `--dry-run` for a long or risky plan.
7. Verify the result with a fresh status call or screenshot.
8. Release the lock in cleanup, then show the cool completion overlay.

Example skeleton:

```powershell
$ui = ".\.venv\Scripts\python.exe"
& $ui .\scripts\ui_control.py overlay --mode start --task "short task label"
& $ui .\scripts\ui_control.py lock acquire --owner "short task label"
& $ui .\scripts\ui_control.py --lock-token <token> status --windows
& $ui .\scripts\ui_control.py --lock-token <token> screenshot --out "$env:TEMP\zcode-ui.png"
# Inspect, perform the smallest authorized action, and verify it.
& $ui .\scripts\ui_control.py lock release --token <token>
& $ui .\scripts\ui_control.py overlay --mode finish --status success --task "short task label" --completed "Verified the requested result"
```

Global options such as `--lock-token` must appear before the subcommand. Every live command in a multi-step desktop phase must use the same held lock token.

## Safety

- Keep the PyAutoGUI corner failsafe enabled.
- Never type secrets, approve payments, grant elevated permissions, delete data, or make irreversible changes unless the user explicitly requested that exact action.
- Do not control UAC secure desktops, password managers, banking flows, or other high-risk interfaces without the user present and an unambiguous request.
- Add `--require-approval` when an action crosses an external or irreversible boundary.
- Keep screenshots local and return concise summaries unless the user needs an image.
- If text encoding, active-window identity, screen scale, or coordinates are uncertain, stop and re-inspect instead of guessing.
