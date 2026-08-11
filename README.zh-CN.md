# BraveCow Harness

当前版本：`0.10.2`。

BraveCow Harness 是给普通用户准备的跨平台助手工作层。它让同一套 Skills、记忆规则、安全边界和审计能力同时服务于：

| 系统 | Codex | ZCode |
| --- | --- | --- |
| Windows | 支持 | 支持 |
| macOS | 支持 | 支持 |

安装完成后，Codex 或 ZCode 会自动新建一个独立任务，由“勇敢牛牛”带课。用户可以拿手头的真实项目边做边学，也可以暂时不定项目，只熟悉软件和背后的原理；第二种路线不会要求用户硬填需求或编一个毕业项目。课程只问当前路线真正需要的信息，文案按自然口播来写，课数、顺序、深度和练习会随回答调整。

每一个界面操作步骤都会把对应平台的实拍红圈图直接放在回复第一项，再说点击步骤；不让用户猜、找或记按钮位置。多次点击会拆成多轮，每轮只圈当前目标。

## 中国大陆 ZCode 接入指南

没有稳定 ChatGPT 账号、计划使用 ZCode 与火山方舟模型服务的用户，可先阅读 [《ZCode + 火山方舟 AI Agent 接入指南》](docs/guides/zcode-volcengine-agent-setup.zh-CN.docx)。文档包含订阅 Agent Plan、添加模型供应商、使用 Responses API、安装 BraveCow Harness 与启动教程的完整截图步骤。

截图记录于 2026 年 8 月，产品界面、套餐、模型与额度可能调整，请以对应官方页面的当前信息为准。任何 API Key 都不要发送到聊天、截图或公开仓库。

## 一键安装

最简单的方式是把仓库链接交给 Codex 或 ZCode：

```text
请下载并安装 BraveCow Harness：
https://github.com/BraveCowNoFear/BraveCow-Harness-Codex
请按 README.zh-CN.md 为我当前的系统和应用安装。安装完成后不要在当前任务里讲教程，让安装器自动开启一个新的新手指南任务。
```

也可以自己运行：

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

macOS 终端：

```sh
sh ./install.sh
```

默认同时为 Codex 和 ZCode 安装。只装一个运行时：

```powershell
.\install.ps1 -Targets Codex
.\install.ps1 -Targets ZCode
```

```sh
sh ./install.sh --targets codex
sh ./install.sh --targets zcode
```

安装器会优先识别是谁发起安装，并在相同应用中开启教程。也可通过 `-OnboardingRuntime Codex|ZCode` 或 `--onboarding-runtime codex|zcode` 明确指定。若暂时不想开教程，使用 `-SkipOnboarding` 或 `--skip-onboarding`。

## 安装内容

- `~/.bravecow/harness`：跨平台 inventory、来源锁、检查、检索和新手任务启动器。
- `~/.bravecow/memories`：两套应用共享的 Markdown 记忆模板；升级默认不覆盖用户内容。
- `~/.agents/skills`：共享 Skills，包括 Harness 审计与新手指南。
- `~/.codex/skills`、`~/.zcode/skills`：指向共享 Skills 的链接，无法链接时安全复制。
- `~/.codex/AGENTS.md`、`~/.zcode/AGENTS.md`：各应用的受管入口规则。
- `~/.zcode/commands/bravecow-onboarding.md`：可手动运行的 ZCode 新手命令。
- Windows + ZCode：从锁定提交安装 `$bravecow-windows-computer-use`，为 ZCode 补上本地桌面操作能力，并使用独立 Python 环境。
- `~/.codex/agents`：Codex 支持的 agent profile 模板。

旧版 `~/.codex/harness` 和 `~/.codex/memories` 会被安全接入新的共享目录，不会偷偷删除或覆盖。

仓库不包含 API key、浏览器登录态、vault、个人资料、自动化 prompt、插件缓存或第三方 vendor 源码。

## 自适应新手指南

课程不再套固定 12 课。它会从新任务、工作区、计划与执行、权限、模型、工具、Skills、版本回退和真实检查等内容里，只挑用户现在需要的部分。已经会的直接跳过；卡住时只补眼前这一步。老师会像坐在旁边一样说明“为什么要这样做、现在点哪里、看到什么算成功”，不会把课程设计术语直接念给用户。模型和按钮始终以当前应用实际显示为准。

课程还会按需吸收 [《40分钟成为 Codex 高级玩家 完整教程》](https://www.bilibili.com/video/BV1dFTv6yEcZ/) 中可迁移的工作方法：先澄清再行动、关键选择设检查点、保留可回退版本、长目标拆里程碑、按权限选择工具、真实查看产物后再宣布完成，而不是照搬固定案例或可能过期的产品结论。

在 Windows + ZCode 组合里，课程会把 [`BraveCowNoFear/desktop-control-for-windows`](https://github.com/BraveCowNoFear/desktop-control-for-windows) 当作真实的插件教学例子：解释来源、精确版本、权限、验证和回退。它技术上是带本地控制器的 Skill 仓库，由 Harness 安装成 ZCode 适配扩展。新手课只运行无副作用的 `--help` 验证，不会擅自截图、读取窗口标题、移动鼠标或输入文字。Codex 使用原生 Computer Use；macOS 上的 ZCode 会明确跳过这份 Windows 专用扩展。

## 自动开启新任务

- Codex：通过官方 App Server 的 `thread/start`、`thread/name/set` 和 `turn/start` 创建并启动任务。
- ZCode / Windows：激活 ZCode 后使用官方 `Ctrl+N` 新任务快捷键。
- ZCode / macOS：激活 ZCode 后使用官方 `Command+N`；首次使用可能需要授予 macOS“辅助功能”权限。
- 每次尝试都会写入 `~/.bravecow/harness/onboarding/last-launch.json`。如果系统权限阻止自动操作，安装器会明确报错；用户仍可在新任务中输入 `$bravecow-onboarding`，或在 ZCode 运行 `/bravecow-onboarding`。

## 安全更新参数

```powershell
# 只预览
.\install.ps1 -UpdateRuntime -MigrateConfig -DryRun

# 更新程序与受管配置，保留已有记忆
.\install.ps1 -UpdateRuntime -MigrateConfig -InitializeMemory

# 不改当前工作区 AGENTS.md
.\install.ps1 -NoWorkspaceAgents

# 不建立目录链接，改为复制
.\install.ps1 -NoJunctions
```

macOS 使用对应的 `--dry-run`、`--update-runtime`、`--migrate-config`、`--initialize-memory`、`--no-workspace-agents` 和 `--no-links`。只有显式使用 `-ReplaceUserData` / `--replace-user-data` 才会替换记忆模板，而且替换前会备份。

## 验证

Windows：

```powershell
python .\tests\validate_package.py
python -m unittest discover -s .\tests
powershell -ExecutionPolicy Bypass -File .\tests\smoke_install.ps1
powershell -ExecutionPolicy Bypass -File .\tests\smoke_zcode_computer_use.ps1
```

macOS：

```sh
python3 ./tests/validate_package.py
python3 -m unittest discover -s ./tests
sh ./tests/smoke_install_macos.sh
```

四象限 CI 会分别验证 Windows/macOS × Codex/ZCode。Codex 新任务接口另有模拟端到端测试；ZCode 自动开任务依赖真实桌面窗口和系统辅助权限，因此 CI 验证安装契约，真实设备仍应做一次安装验收。

## 官方能力依据

- [Codex App Server](https://learn.chatgpt.com/docs/app-server)
- [Codex slash commands](https://learn.chatgpt.com/docs/reference/slash-commands)
- [Codex environments and modes](https://learn.chatgpt.com/docs/environments/modes)
- [ZCode install](https://zcode.z.ai/en/docs/install)
- [ZCode skills](https://zcode.z.ai/en/docs/skill)
- [ZCode commands](https://zcode.z.ai/en/docs/commands)
- [ZCode agents, modes and thought levels](https://zcode.z.ai/en/docs/agents)
- [ZCode Goal mode](https://zcode.z.ai/en/docs/goal)
- [ZCode keyboard shortcuts](https://zcode.z.ai/en/docs/keyboard-shortcuts)
