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

The portable `bravecow-onboarding` skill detects runtime and host, then offers two equal routes: learn through a real project, or learn the software and its principles without a project. **勇敢牛牛** asks only for information needed by the selected route and generates the course at runtime instead of following a fixed syllabus.

Technical and scientific learners receive engineering terminology, architecture, boundaries, trade-offs, failure modes, and verification. Non-technical learners receive the same conceptual truth through defined terms and plain causal explanations. Project-route exercises normally come from the learner's own domain; the principles-only route uses neutral micro-exercises and never pretends a fallback asset is the learner's project.

A normal lesson stays within the progress line plus five short spoken sentences. It says why the step matters, gives one direct action, and asks what the learner sees. The learner can request the current route, skip, review, change depth or example, pause, continue, or exit. Model names and UI controls are read from the current app when possible because product catalogs change over time.

The generated route may distill transferable methods from [BV1dFTv6yEcZ](https://www.bilibili.com/video/BV1dFTv6yEcZ/): clarify before acting, invite useful questions, checkpoint important choices, keep rollback points, split long goals into milestones, choose the least-powerful sufficient tool, and inspect real outputs before calling work complete. These are selected only when they advance the learner's goal.

## Computer Use plugin lesson

The four host/runtime combinations share the course, but they do not pretend to have identical desktop-control implementations:

| Host | Runtime | Course behavior |
| --- | --- | --- |
| Windows | Codex | Explain native Computer Use |
| macOS | Codex | Explain native Computer Use |
| Windows | ZCode | Teach the pinned `$bravecow-windows-computer-use` Skill-based extension as the real plugin example |
| macOS | ZCode | Explain why the Windows-only extension was skipped |

The Windows + ZCode installer records provenance and verification in `~/.bravecow/harness/catalog/zcode-computer-use-install.json`. Onboarding verifies only `ui_control.py --help`; it does not capture the screen, enumerate private window titles, move the pointer, type, or click. A live exercise requires a separate explicit request and uses the extension's lock, approval, and screenshot-act-verify workflow.
