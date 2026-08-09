# BraveCow Harness

当前版本：`0.7.0`。

BraveCow Harness 是给普通用户准备的跨平台助手工作层。它让同一套 Skills、记忆规则、安全边界和审计能力同时服务于：

| 系统 | Codex | ZCode |
| --- | --- | --- |
| Windows | 支持 | 支持 |
| macOS | 支持 | 支持 |

安装完成后，安装它的 Codex 或 ZCode 会自动新建一个独立任务，启动 12 课交互式新手指南。课程不要求计算机背景，会用读书会、旅行选择和家庭预算等例子，逐步讲清任务、工作区、计划模式、目标模式、模型、思考等级、工具、Skills 和 Harness；每课都会等用户回答，不会一次扔出一整本说明书。

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
- `~/.codex/agents`：Codex 支持的 agent profile 模板。

旧版 `~/.codex/harness` 和 `~/.codex/memories` 会被安全接入新的共享目录，不会偷偷删除或覆盖。

仓库不包含 API key、浏览器登录态、vault、个人资料、自动化 prompt、插件缓存或第三方 vendor 源码。

## 新手指南的 12 课

1. 助手、任务与第一次对话
2. 当前任务和新任务的区别
3. 工作区与运行环境
4. 目标、材料、限制、完成标准
5. 计划模式何时有用
6. 执行、权限与对外动作
7. 目标模式何时有用
8. 如何按难度选择模型
9. 如何选择思考等级
10. 文件、网页、浏览器和桌面工具
11. Harness、Skills、规则与记忆
12. 一个完整的非技术毕业小项目

课程会读取当前应用实际显示的模型和选项，不硬编码一份可能过期的名单。Codex 中如果当前可见 Sol，可把它理解为适合困难、多步骤和高要求审查的选择；简单整理通常更适合更快的模型。ZCode 同样以界面当前可见的模型和 Off/High/Max 等思考选项为准。

课程还蒸馏了 [《40分钟成为 Codex 高级玩家 完整教程》](https://www.bilibili.com/video/BV1dFTv6yEcZ/) 中可迁移的工作方法：先澄清再行动、关键选择设检查点、保留可回退版本、长目标拆里程碑、按权限选择工具、真实查看产物后再宣布完成。视频中的开发案例和可能过期的产品结论不会照搬给普通用户。

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
