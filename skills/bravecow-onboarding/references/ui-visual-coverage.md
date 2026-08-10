# BraveCow 课程界面可视化覆盖表

本文件定义新手课中所有需要用户点击的 Codex / ZCode 控件，以及对应教学图片。凡是要求用户点击的按钮，都必须先展示一张经过真实界面核验的红圈图；纯概念或键盘命令不得伪造按钮。

## 图片硬性规则

1. 使用当前已安装应用的真实截图，不使用凭空生成的 UI。
2. 每张图只教学一个主要按钮；目标按钮使用单个粗红圈标出。
3. 项目名、任务标题、文件路径、对话正文、账户信息和来源列表必须遮挡到不可读。
4. 保留应用名称、课程所需菜单名和目标按钮周边最小必要上下文。
5. 图片文件名稳定，课程只引用 `assets/ui/<runtime>/` 或 `assets/ui/shared/` 下的最终图；包含私密信息的原始截图必须保存在课程 Skill 目录之外，不得随课程分发。
6. 应用版本或界面位置变化时，先重新截图和核验，再替换最终图。

## Codex 图片清单

| ID | 课程 | 教学动作 | 最终图片 |
|---|---:|---|---|
| C01 | 1 | 新建任务/新对话 | `assets/ui/codex/01-new-task.png` |
| C02 | 2 | 在左侧任务列表切换任务 | `assets/ui/codex/02-task-list.png` |
| C03 | 3 | 新建项目 | `assets/ui/codex/03-new-project.png` |
| C04 | 3 | 选择或打开项目文件夹 | `assets/ui/codex/04-open-project-folder.png` |
| C05 | 3 | 选择当前界面实际显示的项目类型/环境 | `assets/ui/codex/05-environment.png` |
| C06 | 5 | 当前版本无独立 Plan 按钮时的计划流程卡（无红圈） | `assets/ui/codex/06-plan-mode.png` |
| C07 | 6 | 查看权限/访问级别与外部动作确认 | `assets/ui/codex/07-access-mode.png` |
| C08 | 7 | 进入 Goal 模式 | `assets/ui/codex/08-goal-mode.png` |
| C09 | 8 | 打开模型选择菜单 | `assets/ui/codex/09-model-selector.png` |
| C10 | 9 | 选择思考等级 | `assets/ui/codex/10-reasoning-level.png` |
| C11 | 10 | 添加附件或材料 | `assets/ui/codex/11-attachment.png` |
| C12 | 10 | 打开工具/Computer Use 入口 | `assets/ui/codex/12-tools-computer-use.png` |
| C13 | 11 | 打开插件页面 | `assets/ui/codex/13-plugins.png` |
| C14 | 11 | 调用 Skill 的输入位置 | `assets/ui/codex/14-skill-input.png` |
| C15 | 12 | 识别并打开个人项目交付物链接（中性文件名示意） | `assets/ui/codex/15-open-output.png` |

## ZCode 图片清单

| ID | 课程 | 教学动作 | 最终图片 |
|---|---:|---|---|
| Z01 | 1 | 新建任务 | `assets/ui/zcode/01-new-task.png` |
| Z02 | 2 | 切换任务或会话 | `assets/ui/zcode/02-task-list.png` |
| Z03 | 3 | 新建或打开项目文件夹 | `assets/ui/zcode/03-open-project-folder.png` |
| Z04 | 3 | 选择本地或远程工作区 | `assets/ui/zcode/04-workspace-location.png` |
| Z05 | 5 | 进入 Plan 模式 | `assets/ui/zcode/05-plan-mode.png` |
| Z06 | 6 | 查看权限并确认外部动作 | `assets/ui/zcode/06-permissions.png` |
| Z07 | 7 | 在输入框调用 `/goal` | `assets/ui/zcode/07-goal-command.png` |
| Z08 | 8 | 打开模型选择菜单 | `assets/ui/zcode/08-model-selector.png` |
| Z09 | 9 | 当前版本无独立思考等级按钮时的替代策略卡（无红圈） | `assets/ui/zcode/09-thought-level.png` |
| Z10 | 10 | 添加附件或材料 | `assets/ui/zcode/10-attachment.png` |
| Z11 | 10 | 打开工具或命令入口 | `assets/ui/zcode/11-tools.png` |
| Z12 | 11 | 打开 Skills 列表 | `assets/ui/zcode/12-skills.png` |
| Z13 | 11 | 调用 `$bravecow-windows-computer-use` 的输入位置 | `assets/ui/zcode/13-computer-use-skill.png` |
| Z14 | 12 | 无安全可展示文件链接时的毕业项目验收流程卡（无红圈） | `assets/ui/zcode/14-open-output.png` |

## 跨平台概念卡

| ID | 课程 | 教学概念 | 最终图片 |
|---|---:|---|---|
| S04 | 4 | 目标、材料、限制、完成标准四件套 | `assets/ui/shared/04-requirement-card.png` |
| S06 | 6 | 文档、Git、GitHub 三种版本分支 | `assets/ui/shared/06-version-flow.png` |
| S11 | 11 | Harness、Skills、插件、规则、记忆与检查机制 | `assets/ui/shared/11-harness-map.png` |

## 每课图片路由

每课最多显示一张图。若当课需要用户点击，优先显示当前平台的实拍红圈图；若不需要点击或当前版本没有对应控件，显示共享或平台专用概念卡。

| 课程 | Codex | ZCode |
|---:|---|---|
| 1 | C01 | Z01 |
| 2 | C02 | Z02 |
| 3 | C03；完成后按需要改用 C04 或 C05 | Z03；远程项目改用 Z04 |
| 4 | S04 | S04 |
| 5 | C06 | Z05 |
| 6 | S06；需要调整权限时改用 C07 | S06；需要调整权限时改用 Z06 |
| 7 | C08 | Z07 |
| 8 | C09 | Z08 |
| 9 | C10 | Z09 |
| 10 | C11；需要桌面操作时改用 C12 | Z10；需要命令入口时改用 Z11 |
| 11 | S11；需要点击时改用 C13 或 C14 | S11；需要点击时改用 Z12 或 Z13 |
| 12 | C15 | Z14；若本次任务已有安全文件链接，现场生成对应红圈图 |

## 完成判定

- 清单中的每个图片文件存在且可以打开。
- 实拍操作图只有一个主要红圈，红圈确实包围目标控件；明确标注为概念卡的图片不画红圈。
- OCR 或人工查看不能读出项目名、任务标题、文件路径、正文和账户信息。
- Codex 图片来自 Codex，ZCode 图片来自 ZCode；不得跨平台复用假装一致。
- 课程在识别出运行平台后，只发送对应平台的图片。
