# BraveCow Harness Codex

BraveCow Harness Codex 是一个给 Codex Desktop 用的 Windows 优先 harness 安装包。它把一套可审计的本机控制层装到新机器上：skills 管理、memory 文件、agent profiles、harness inventory/audit 脚本，以及一个专门检查 harness 的 skill。

它不是把某台电脑的 `.codex` 原样打包。它不会包含 API key、浏览器登录态、vault、个人资料、自动化任务、插件缓存或第三方 vendor 源码。

## 一键安装

在这个仓库目录打开 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

安装后可以直接让 Codex 执行：

```text
使用 agent-harness-introspect skill，检查并总结我本机的 Codex harness。
```

## 会安装什么

- `~/.codex/harness`：inventory/audit 脚本和 harness 说明。
- `~/.agents/skills/agent-harness-introspect`：共享 skill。
- `~/.codex/skills/agent-harness-introspect`：默认创建到共享 skill 的 junction；失败时复制。
- `~/.codex/memories`：`PROFILE.md`、`ACTIVE.md`、`LEARNINGS.md`、`ERRORS.md`、`FEATURE_REQUESTS.md` 模板。
- `~/.codex/agents`：`default`、`explorer`、`worker` 三个 agent profile 模板。
- `~/.codex/AGENTS.md` 和当前 workspace 的 `AGENTS.md`：追加一段 memory/harness 入口规则。

## 常用参数

```powershell
# 不改当前目录的 AGENTS.md
powershell -ExecutionPolicy Bypass -File .\install.ps1 -NoWorkspaceAgents

# 覆盖更新已有模板和脚本
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Force

# 不创建 junction，直接复制 skill
powershell -ExecutionPolicy Bypass -File .\install.ps1 -NoJunctions
```

## 给朋友的最短用法

把这个链接发给朋友，让他丢给 Codex：

```text
请下载并安装这个 Codex harness：https://github.com/BraveCowNoFear/BraveCow-Harness-Codex
按 README.zh-CN.md 运行 install.ps1，然后用 agent-harness-introspect 检查安装结果。
```
