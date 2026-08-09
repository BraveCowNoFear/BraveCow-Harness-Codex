# BraveCow Harness

Current release: `0.7.1`.

BraveCow Harness is a portable control plane for ordinary Codex and ZCode users. The same shared skills, Markdown memory, safety rules, provenance inventory, and audit tooling work across four supported combinations:

| Host | Codex | ZCode |
| --- | --- | --- |
| Windows | Supported | Supported |
| macOS | Supported | Supported |

After installation, the calling app automatically opens a separate task and starts a 12-lesson interactive beginner course taught by **Brave Cow (勇敢牛牛)** in a warm, patient, respectful voice. It explains tasks, workspaces, Plan and Goal modes, model and thought-level choices, tools, skills, memory, and the Harness through everyday examples instead of programming exercises.

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
- Codex agent profiles where supported.

Legacy `~/.codex/harness` and `~/.codex/memories` data are adopted without deletion. API keys, browser sessions, vaults, personal profiles, private automation prompts, plugin caches, and third-party vendor source are never packaged.

## Post-install Course

The `bravecow-onboarding` skill teaches one lesson per turn and waits for the learner. It adapts to the actual app, OS, visible models, and available thought controls. It uses a community book event, travel options, and a household budget as practice material.

The course also distills the transferable workflow lessons from [BV1dFTv6yEcZ](https://www.bilibili.com/video/BV1dFTv6yEcZ/): clarify before acting, add decision checkpoints, preserve rollback points, split long goals into milestones, choose tools by permission and purpose, and inspect the real output before declaring completion. Its development-specific example and time-sensitive product claims are not copied into the general-audience path.

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
```

```sh
python3 ./tests/validate_package.py
python3 -m unittest discover -s ./tests
sh ./tests/smoke_install_macos.sh
```

CI covers Windows/macOS × Codex/ZCode separately. The Codex App Server launcher also has a simulated end-to-end task creation test. ZCode's desktop launch still requires a real GUI acceptance check because it depends on a visible app window and OS Accessibility permission.

Official capability references: [Codex App Server](https://learn.chatgpt.com/docs/app-server), [Codex commands](https://learn.chatgpt.com/docs/reference/slash-commands), [ZCode install](https://zcode.z.ai/en/docs/install), [ZCode skills](https://zcode.z.ai/en/docs/skill), [ZCode agents](https://zcode.z.ai/en/docs/agents), [ZCode Goal mode](https://zcode.z.ai/en/docs/goal), and [ZCode shortcuts](https://zcode.z.ai/en/docs/keyboard-shortcuts).
