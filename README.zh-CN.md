# BraveCow Harness Codex

BraveCow Harness Codex 是一个给 Codex Desktop 用的 Windows 优先控制层：它提供 Skill/插件启用态盘点、来源锁、安全更新边界、Markdown + SQLite FTS5 本地记忆检索、agent profiles 和审计报告。

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

- `~/.codex/harness`：inventory、来源锁、配置语义门、FTS5 检索与审计脚本。
- `~/.agents/skills/agent-harness-introspect`：共享 skill。
- `~/.codex/skills/agent-harness-introspect`：默认创建到共享 skill 的 junction；失败时复制。
- `~/.codex/memories`：七个分层记忆模板，新增 `MEMORY_POLICY.md` 与 `SESSION_LOG.md`。
- `~/.codex/agents`：`default`、`explorer`、`worker` 三个 agent profile 模板。
- `~/.codex/AGENTS.md` 和当前 workspace 的 `AGENTS.md`：追加一段 memory/harness 入口规则。

## 发布前验证

```powershell
python .\tests\validate_package.py
python -m unittest discover -s .\tests
powershell -ExecutionPolicy Bypass -File .\tests\smoke_install.ps1
```

## 常用参数

```powershell
# 不改当前目录的 AGENTS.md
powershell -ExecutionPolicy Bypass -File .\install.ps1 -NoWorkspaceAgents

# 只预览，不写文件
powershell -ExecutionPolicy Bypass -File .\install.ps1 -UpdateRuntime -MigrateConfig -DryRun

# 更新运行时代码和受管 AGENTS 片段；绝不覆盖已有记忆
powershell -ExecutionPolicy Bypass -File .\install.ps1 -UpdateRuntime -MigrateConfig -InitializeMemory

# 高危、显式替换用户数据；覆盖前自动备份
powershell -ExecutionPolicy Bypass -File .\install.ps1 -ReplaceUserData

# 不创建 junction，直接复制 skill
powershell -ExecutionPolicy Bypass -File .\install.ps1 -NoJunctions
```

`-InitializeMemory` 只创建缺失的记忆文件。兼容参数 `-Force` 现在只等价于 `-UpdateRuntime -MigrateConfig`，不会替换 memory 或其他用户数据。所有被覆盖的受管文件会先备份到 `~/.codex/harness/backups/`。

## 记忆检索

Markdown 永远是可信源。已知路径直接读取，普通查询优先走本机 SQLite FTS5：

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\memory_search.py" "Edge 浏览器规则"
```

Graphiti/向量库只作为时间关系或语义查询的可选索引；服务故障不得阻塞普通任务。

## 给朋友的最短用法

把这个链接发给朋友，让他丢给 Codex：

```text
请下载并安装这个 Codex harness：https://github.com/BraveCowNoFear/BraveCow-Harness-Codex
按 README.zh-CN.md 运行 install.ps1，然后用 agent-harness-introspect 检查安装结果。
```
