# BraveCow Harness

Current release: `0.10.2`.

BraveCow Harness is a portable control plane for ordinary Codex and ZCode users. The same shared skills, Markdown memory, safety rules, provenance inventory, and audit tooling work across four supported combinations:

| Host | Codex | ZCode |
| --- | --- | --- |
| Windows | Supported | Supported |
| macOS | Supported | Supported |

After installation, the calling app opens a separate task taught by **Brave Cow (勇敢牛牛)**. Learners choose either to work through a real project or to learn the software and its underlying principles without inventing a project. The course asks only for information needed by that route, speaks in concise natural language, and adapts lesson count, order, depth, examples, and completion evidence continuously.

Every UI-action step must place the matching real screenshot for the current runtime as the reply's first content block, then give one click instruction. The course never asks learners to find or guess controls; multi-click operations are split into one pictured target per turn.

For Chinese instructions, see [README.zh-CN.md](README.zh-CN.md).

## Quick Start

Give this repository URL to Codex or ZCode and ask it to follow the README for the current platform, or run the installer directly:

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

```sh
# macOS
sh ./install.sh
```

Both runtimes are installed by default. Use `-Targets Codex|ZCode` on Windows or `--targets codex|zcode` on macOS to install one. Use `-SkipOnboarding` or `--skip-onboarding` only when a new course task is not wanted.

## What It Installs

- `~/.bravecow/harness`: portable inventory, audit, retrieval, and onboarding launchers.
- `~/.bravecow/memories`: shared canonical Markdown memory, preserved by default during upgrades.
- `~/.agents/skills`: shared Harness skills.
- `~/.codex/skills` and `~/.zcode/skills`: links to shared skills, or safe copies when links are disabled.
- Runtime-specific `AGENTS.md` entry rules and a ZCode `/bravecow-onboarding` command.
- On Windows + ZCode only, the pinned `$bravecow-windows-computer-use` extension and its isolated Python environment.
- Codex agent profiles where supported.

Legacy `~/.codex/harness` and `~/.codex/memories` data are adopted without deletion. API keys, browser sessions, vaults, personal profiles, private automation prompts, plugin caches, and third-party vendor source are never packaged.

## Post-install Course

The `bravecow-onboarding` skill treats its curriculum as a learning-outcome pool, not a fixed syllabus. It selects only the concepts the learner needs, skips demonstrated knowledge, and adjusts depth after every answer. The project route uses the learner's own work; the principles-only route uses tiny neutral exercises and never forces a fake requirement-gathering flow or capstone.

The course also distills the transferable workflow lessons from [BV1dFTv6yEcZ](https://www.bilibili.com/video/BV1dFTv6yEcZ/): clarify before acting, add decision checkpoints, preserve rollback points, split long goals into milestones, choose tools by permission and purpose, and inspect the real output before declaring completion. Its development-specific example and time-sensitive product claims are not copied into the general-audience path.

On Windows + ZCode, the course uses [`BraveCowNoFear/desktop-control-for-windows`](https://github.com/BraveCowNoFear/desktop-control-for-windows) as a real plugin lesson. Technically it is a Skill repository with a local controller; Harness pins its exact commit, installs a ZCode adapter, isolates dependencies, and verifies the CLI without controlling the desktop. Codex uses native Computer Use. macOS + ZCode correctly skips this Windows-only extension and teaches that compatibility boundary.

Codex task creation uses the official App Server. ZCode task creation uses its documented new-task shortcut (`Ctrl+N` on Windows, `Command+N` on macOS). macOS may request Accessibility permission. Every attempt writes `~/.bravecow/harness/onboarding/last-launch.json`; if desktop automation is blocked, start a new task manually and enter `$bravecow-onboarding`, or run `/bravecow-onboarding` in ZCode.

## Safe Update Options

```powershell
.\install.ps1 -UpdateRuntime -MigrateConfig -InitializeMemory
.\install.ps1 -UpdateRuntime -MigrateConfig -DryRun
```

```sh
sh ./install.sh --update-runtime --migrate-config --initialize-memory
sh ./install.sh --update-runtime --migrate-config --dry-run
```

Existing memory is replaced only by the explicit `-ReplaceUserData` / `--replace-user-data` option, and managed files are backed up first.

## Verification

```powershell
python .\tests\validate_package.py
python -m unittest discover -s .\tests
powershell -ExecutionPolicy Bypass -File .\tests\smoke_install.ps1
powershell -ExecutionPolicy Bypass -File .\tests\smoke_zcode_computer_use.ps1
```

```sh
python3 ./tests/validate_package.py
python3 -m unittest discover -s ./tests
sh ./tests/smoke_install_macos.sh
```

CI covers Windows/macOS × Codex/ZCode separately. The Codex App Server launcher also has a simulated end-to-end task creation test. ZCode's desktop launch still requires a real GUI acceptance check because it depends on a visible app window and OS Accessibility permission.

Official capability references: [Codex App Server](https://learn.chatgpt.com/docs/app-server), [Codex commands](https://learn.chatgpt.com/docs/reference/slash-commands), [ZCode install](https://zcode.z.ai/en/docs/install), [ZCode skills](https://zcode.z.ai/en/docs/skill), [ZCode agents](https://zcode.z.ai/en/docs/agents), [ZCode Goal mode](https://zcode.z.ai/en/docs/goal), and [ZCode shortcuts](https://zcode.z.ai/en/docs/keyboard-shortcuts).
