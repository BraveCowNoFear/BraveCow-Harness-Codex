# Post-install onboarding design

The onboarding is intentionally a task, not a static manual.

## Launch matrix

| Host | Runtime | New-task mechanism | Recovery |
| --- | --- | --- | --- |
| Windows | Codex | App Server `thread/start` + `turn/start` | Run `$bravecow-onboarding` in a new task |
| macOS | Codex | App Server `thread/start` + `turn/start` | Run `$bravecow-onboarding` in a new task |
| Windows | ZCode | Activate ZCode, `Ctrl+N`, paste skill invocation | Run `/bravecow-onboarding` |
| macOS | ZCode | Activate ZCode, `Command+N`, paste skill invocation | Grant Accessibility permission or run the command manually |

The installer writes a machine-readable receipt to `~/.bravecow/harness/onboarding/last-launch.json`. A failed automatic launch is reported as an installation failure rather than silently claiming that onboarding started.

## Course behavior

The portable `bravecow-onboarding` skill detects runtime and host, then teaches as **勇敢牛牛**: a warm, patient teacher who stays concise, respects adult learners, corrects without judgment, and avoids childish language or empty praise. It teaches one of 12 lessons per turn. The learner can ask for the table of contents, skip, review, change the example, pause, continue, or exit. Model names and UI controls are always read from the current app when possible because product catalogs change over time.

Practice materials are non-technical: a community book event, travel options, and a household budget. The final exercise requires the learner to decide whether Plan or Goal mode is appropriate, provide constraints, create an artifact, and check it against an explicit completion standard.

The workflow lessons also distill the transferable parts of [BV1dFTv6yEcZ](https://www.bilibili.com/video/BV1dFTv6yEcZ/): clarify before acting, invite useful questions, checkpoint important choices, keep rollback points, split long goals into milestones, choose the least-powerful sufficient tool, and inspect real outputs before calling work complete. Its software-development example and time-sensitive product claims are not copied into the general-audience course.

## Computer Use plugin lesson

The four host/runtime combinations share the course, but they do not pretend to have identical desktop-control implementations:

| Host | Runtime | Course behavior |
| --- | --- | --- |
| Windows | Codex | Explain native Computer Use |
| macOS | Codex | Explain native Computer Use |
| Windows | ZCode | Teach the pinned `$bravecow-windows-computer-use` Skill-based extension as the real plugin example |
| macOS | ZCode | Explain why the Windows-only extension was skipped |

The Windows + ZCode installer records provenance and verification in `~/.bravecow/harness/catalog/zcode-computer-use-install.json`. Onboarding verifies only `ui_control.py --help`; it does not capture the screen, enumerate private window titles, move the pointer, type, or click. A live exercise requires a separate explicit request and uses the extension's lock, approval, and screenshot-act-verify workflow.
