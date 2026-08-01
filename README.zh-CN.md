# BraveCow Harness Codex

当前版本：`0.6.1`。

BraveCow Harness Codex 是一个给 Codex Desktop 用的 Windows 优先控制层：它提供 Skill/插件启用态盘点、来源锁、安全更新边界、Markdown + SQLite FTS5 本地记忆检索、agent profiles 和审计报告。

它不是把某台电脑的 `.codex` 原样打包。它不会包含 API key、浏览器登录态、vault、个人资料、自动化定义或 prompt、插件缓存或第三方 vendor 源码。属于 Harness 的自动化仍保留为本机私有运行状态，但审计器会把它们的非敏感角色纳入控制面。

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

Markdown 永远是可信源。检索路由器会直接读取已知文件，普通查询走本机 SQLite FTS5，只有时间/实体关系问题且现有 Graphiti 端口健康时才建议交给 Graphiti：

```powershell
python "$env:USERPROFILE\.codex\harness\scripts\memory_router.py" "Edge 浏览器规则"
```

返回结果受证据字符预算限制。Graphiti/向量库故障时立即回退到本机检索，不会自动启动或修复外部服务。持久记忆候选可先经过只校验、不写入的门禁：

```powershell
Get-Content .\candidate.json | python "$env:USERPROFILE\.codex\harness\scripts\memory_write_gate.py"
```

`harness.lock.json` v2 会记录插件解析结果、组件源码/安装版本、Git 远端/分支/提交、许可证证据、验证状态、本地补丁和回滚点；无法确认的字段会明确标为未知，不做猜测。

## 自动化子系统

月度演进自动化是 Harness 的技术雷达与安全升级闭环：它从一手来源侦察快速变化的 AI 能力，先做最小兼容实验，只采纳在当前机器上有可测净收益的变化。全局“记忆 → Graphiti”自动化和 Markdown 记忆维护共同构成 Harness 的记忆/RAG 控制面。本机定义不会被导出；审计只记录安全的角色、状态、归属、健康、成本与回滚元数据。详见 [docs/automation-subsystems.md](docs/automation-subsystems.md)。

可选的 `skill_contracts.py` 会运行本机专属的正/负触发提示回归。仓库只附示例，不会把一台机器的激活契约静默套到另一台机器。

0.6 版把已解析的插件 Skill 按“插件名:Skill名”纳入 inventory 和触发契约，记录运行时组件的官方上游观测，并测量真实 Codex 启动 prompt。配置门禁也能精确识别旧版桌面 CLI 对 `priority` 的 schema 落后，用兼容别名 `fast` 验证其余配置，不修改用户配置。

月度审计可以从仓库示例生成 `~/.codex/harness/catalog/upstream-observations.json`。每条观测必须指向官方仓库、release、tag、commit 或包完整性值；观测只是证据，绝不会授权自动升级。

可用以下命令保存脱敏、可复现的运行时快照并测量 prompt 成本：

```powershell
python .\harness\scripts\export_runtime_snapshot.py --output .\reports\runtime-snapshot
python .\harness\scripts\measure_prompt_baseline.py --output "$env:USERPROFILE\.codex\harness\catalog\prompt-baseline.json"
```

## 给朋友的最短用法

把这个链接发给朋友，让他丢给 Codex：

```text
请下载并安装这个 Codex harness：https://github.com/BraveCowNoFear/BraveCow-Harness-Codex
按 README.zh-CN.md 运行 install.ps1，然后用 agent-harness-introspect 检查安装结果。
```
