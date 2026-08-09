# ZCode Computer Use 插件课

本课只在“当前应用是 ZCode”时展开。老师仍叫“勇敢牛牛”，保持亲切、尊重成年人的口吻。

## 先讲清楚差异

- Codex 自带 Computer Use 能力，不需要安装这一份扩展。
- ZCode 不自带同等的 Computer Use，所以 BraveCow Harness 会在 **Windows + ZCode** 组合中安装
  [`BraveCowNoFear/desktop-control-for-windows`](https://github.com/BraveCowNoFear/desktop-control-for-windows) 的锁定版本。
- 这个项目在日常语言里可以叫“插件式扩展”，但技术上是一个带本地脚本的 **Skill 仓库**。Harness 为 ZCode 添加兼容适配后安装为 `$bravecow-windows-computer-use`。
- 它只控制 Windows 桌面，因此 **macOS + ZCode 不安装**。这不是安装失败，而是正确的兼容性边界。

## 用它教会用户什么是插件

插件不是“更聪明的模型”，而是给助手增加一类原本没有的行动能力。用“旅行助理”打比方：模型像会做攻略的人；插件像订票网站、地图或电话。多一个工具也意味着多一份权限和风险，所以安装前后都要回答六个问题：

1. 来源是谁？这里是 BraveCowNoFear 的公开 GitHub 仓库。
2. 装的哪一版？Harness 记录精确提交，而不是永远追随会变化的 `main`。
3. 能做什么？查看窗口、截图，以及经授权后使用鼠标、键盘和剪贴板。
4. 权限有多大？它能影响可见桌面，所以不能把付款、密码、删除等动作当普通练习。
5. 怎样证明装好了？先做只读或无副作用检查，不拿真实界面冒险。
6. 出问题怎样回退？保留旧提交和安装前备份，把来源锁改回已验证的提交后重新安装，而不是临时下载一份来历不明的副本。

## 教学演示

Windows + ZCode：

1. 请用户在当前 ZCode 的 Skills 列表或 `~/.zcode/skills/bravecow-windows-computer-use` 中确认扩展存在。
2. 告诉用户 Harness 的安装回执在 `~/.bravecow/harness/catalog/zcode-computer-use-install.json`，其中记录来源、提交和安装位置。
3. 只运行 `.venv\Scripts\python.exe scripts\ui_control.py --help`，让用户看到它有哪些能力类别。
4. 不在新手课中自动截图、读取窗口标题、移动鼠标或输入文字。若用户主动同意继续，可另开一个小任务，用记事本等无敏感内容的应用做截图—操作—复验练习。

macOS + ZCode：

1. 明确告诉用户这份 Windows 扩展未安装。
2. 借此解释“插件必须同时匹配应用、操作系统和权限”，不要假装四种组合的所有附加能力完全相同。

## 互动问题

用一个非技术问题收尾：

> 如果让助手把你写好的一段活动通知粘贴到桌面聊天软件里，你希望它在“打开聊天窗口”“选中收件人”“真正发送”三个节点中的哪些地方先问你？为什么？

根据回答解释：浏览和草拟通常风险较低，选择收件人需要复核，真正发送属于对外动作，默认应在最后一步得到明确确认。
