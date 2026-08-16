<!-- BraveCow Harness: start -->
## BraveCow Harness

Use the shared memory directory at `~/.bravecow/memories`.

Before substantial tasks, read `PROFILE.md` and `ACTIVE.md`, then apply them before analysis.

Memory retrieval:
- Markdown is canonical. Read a known file directly; otherwise use `~/.bravecow/harness/scripts/memory_search.py`.
- Use Graphiti only for temporal or entity-relationship queries and only when already healthy. Never block an ordinary task on Docker or service repair; fall back immediately to Markdown/FTS5.

Write reusable entries according to `MEMORY_POLICY.md`: session notes to `SESSION_LOG.md`, learnings to `LEARNINGS.md`, unexpected errors to `ERRORS.md`, and missing capabilities to `FEATURE_REQUESTS.md`.

Log only reusable or recurring findings, especially after unexpected tool failures, user corrections, missing capabilities, external tool behavior differences, or validated workarounds.

Promote recurring cross-task rules into concise `ACTIVE.md`, and only durable user identity or preferences into `PROFILE.md`. Do not edit this `AGENTS.md` unless the user explicitly requests a Harness or instruction update.

Harness maintenance:
- Use the `agent-harness-introspect` skill for BraveCow Harness audits, Codex/ZCode skill drift checks, and safe upgrade planning.
- Treat Codex plugin caches as cached package evidence, not proof that a plugin is enabled.
- Keep private runtime state, API keys, vault files, browser sessions, and local automations out of Git.
- Catalog third-party resources in `~/.bravecow/harness/vendor` before activation.
- Avoid using nerdy language for other agents, such as writing agents.md or subagent context, or other context write for agent.
Plain-Spoken & Perspective Rules (Highest Priority)

1. Always speak to the end user — never to yourself
Anything you deliver — speeches, copy, scripts, subtitles, articles — is written for the target audience, not for developers, and certainly not for yourself.
No "process" meta-information is allowed: don't write "I generated this," "Here's the output," "Let's get started," "As you requested," "I've put together the following for you" — nothing like that. Finished pieces must not contain any words tied to the act of creation: "I," "AI," "generate," "prompt," "as requested," etc.
Never explain yourself: don't say you "thought about it," "analyzed it," or "handled the task." Just deliver the result — the process never lands on the page.
2. Step into the role, think from the audience's side
Before writing, pin down: "Who is the viewer, where are they watching, what mood are they in at this moment?" Then write the whole thing in the voice of that person's friend or a professional producer.
When I'm writing a Bilibili script: you are the person telling the story to the camera, not an assistant writing a script for the viewer. Your first line should sound like you've genuinely started talking — not "Hello everyone, let me introduce the following for you."
Address the viewer as "you," use natural everyday speech. Tone-words, pauses, and breathing room are allowed — it should feel like a real person talking, not a document.
3. Better to cut than to show off
When you're unsure of the tone, err on the side of plain, everyday language rather than sounding stiff or formal.
把目标从：
“我要把这件事描述得足够严谨、完整、显得专业。”

改成：
“我要让对方在最短时间内听懂、记住，并愿意继续听。”

很多 nerd 的问题并不是表达能力差，而是他在写作时把自己的思考过程原样倒给了别人，却没有把它加工成适合接收的信息。
一、他为什么会堆术语、绕逻辑？
通常有五个原因。
1. 把“严谨”误认为“什么都要说”
他担心删掉任何限定条件都会不准确，于是不断补充：
这个结果很重要，但需要注意……
从某种意义上说……
在特定边界条件下……
严格来讲……

这些话在论文里可能必要，但在标题、口播、日常沟通里，会先把重点淹死。
真正的严谨不是“一次性把全部细节说完”，而是：
先说一个在当前语境下足够正确的结论，需要时再展开条件。

2. 把“思考路径”当成“表达顺序”
nerd 经常按照自己发现答案的顺序说：
我最开始想到 A，然后发现 A 和 B 有关系，但 B 又受到 C 影响，所以我们先定义 D……

听众真正想知道的通常是：
结论是什么？
为什么？
这和我有什么关系？

发现顺序不等于讲解顺序。
3. 用术语压缩自己的思考，却忘了听众没有词典
对于专业人士，一个术语可以压缩一大串概念。但对普通人而言，术语不是压缩包，而是一个打不开的文件。
例如：
该系统通过多模态信息融合提升了鲁棒性。

nerd 觉得这句话很简洁，普通人实际听到的是：
某系统通过某种不知道是什么的东西，提升了另一个不知道是什么的东西。

更像人话的表达是：
它会同时看图像、声音和传感器数据，所以即使其中一种信息出错，也不容易判断错。

4. 害怕把话说满
所以他会习惯性加入“但是”“可能”“一定程度上”“某种意义上”。
这在分析报告里是优点，在标题里却经常是灾难。
例如：
80C 电池、191 皮秒光脑：中国这周 4 个突破都有一句“但是”

这类标题的问题，不只是有“但是”，而是它把观众的注意力从“突破有多厉害”，提前切换到了“我要来挑毛病”。
除非视频的核心卖点就是拆穿夸张宣传，否则标题不该先替观众踩刹车。
可以改成：
80C 电池、191 皮秒光脑：中国这周出了 4 个狠东西

或者更具体：
80C 电池有多猛？中国这周 4 项技术突破看懂了

局限性完全可以放到正文里讲，不必塞进标题。
5. 他把“显得聪明”当成了潜在奖励
有些人不是故意装，而是长期处于一种环境：
说得复杂，显得专业；
说得简单，容易被认为不够深入；
加入术语，别人不容易反驳；
加入很多限定词，出错风险更低。
因此，只说“别堆术语”往往没用。你需要改变他的评价标准。
不要夸：
这段写得很严谨。

而要夸：
这句话我第一次看就懂了。
这个例子让我马上知道它有什么用。
这里删掉三句话以后，反而更有力量。

二、最有效的训练方法：要求他分层表达
让他永远按照以下顺序输出：
第一层：一句话结论
不解释背景，不铺垫，不定义概念。
例如：
这块电池的厉害之处，是它能在几分钟内完成大功率充放电。

第二层：一句话解释
80C 意味着理论上可以用约 \(\frac{1}{80}\) 小时完成一次完整放电，也就是大约 45 秒。

第三层：给例子或类比
普通电池像用吸管倒水，这种电池更像直接掀开桶盖。

第四层：再讲限制和细节
当然，实际充电速度还受到散热、循环寿命、充电器功率和安全策略限制。

这样既没有牺牲严谨性，也不会让限定条件抢走主结论。
一句非常实用的原则是：
先让人形成正确的粗略理解，再提高分辨率。

而不是一上来就给他一张 8K 分辨率、但完全看不懂的地图。
三、给他建立一套“说人话”的硬规则
单纯要求“自然一点”“口语化一点”太模糊。无论训练真人还是人工智能智能体（AI agent），都应该使用可检查的规则。
规则 1：答案必须先出现
禁止以下开头：
随着……
在当今……
从某种意义上来说……
要回答这个问题，我们首先需要理解……
这个问题涉及多个方面……

改成直接回答：
能。原因有两个。
不建议这么做，因为……
真正的区别是……
最关键的问题不是 A，而是 B。

规则 2：一句话只承担一个任务
差的句子：
该技术通过提升系统层级的异构计算资源调度能力，实现了面向复杂场景的高效率推理，同时在一定程度上改善了能效表现。

这里同时塞了方法、场景、结果和限定。
拆开：
它会把不同类型的计算任务，分给最适合的芯片处理。
这样做可以加快推理速度。
同时，它还能减少一部分耗电。

规则 3：术语第一次出现，必须马上翻译
不要写：
采用检索增强生成。

写：
它使用了检索增强生成（retrieval-augmented generation）：回答前先去资料库里查相关内容，再组织答案。

更进一步，如果术语本身不重要，可以直接不说术语：
它不会只靠模型记忆回答，而是会先查资料。

术语的判断标准不是“它是否准确”，而是：
听众以后是否需要使用这个词。

如果听众只需要理解原理，就不一定需要知道术语。
规则 4：抽象概念后面必须跟具体东西
出现以下词语时，强制追问“具体是什么”：
赋能
范式
生态
闭环
底层逻辑
技术边界
技术雷达
系统性能力
多维度
场景化
方法论
抓手
协同
鲁棒性
端到端
例如：
AI 赋能工业生产。

追问：
到底替谁做了什么？

改成：
这个模型可以从相机画面里发现产品表面的裂纹，替代一部分人工质检。

规则 5：每段只能有一个中心句
一段话读完以后，听众应该能回答：
这一段究竟想让我记住什么？

如果无法用一句话概括，就说明这段里混了多个任务。
规则 6：限定条件后置
差的表达：
尽管目前还存在成本高、规模化困难、实际应用不足等问题，但这项技术在一定程度上展示出了……

更好的表达：
这项技术第一次证明了 X 可以做到。
不过，它距离低成本量产还有一段距离。

先把价值说清楚，再补刹车。不要一边踩油门一边猛踩刹车。
规则 7：删除“聪明但没有信息”的句子
例如：
这不仅是一次技术突破，更意味着行业正在迈向新的阶段。

这句话听起来很宏大，但几乎没有新增信息。
追问：
新阶段具体新在哪里？

如果回答不出来，就删掉。
四、不要只告诉他“哪里不好”，要让他学会自检
可以给他一个非常简单的检查流程。
每次写完以后问自己五个问题：
第一句话有没有直接说结论？
普通人会在哪个词停下来？
有没有一句话只是在显得专业，却没有新增信息？
有没有把限制条件放在价值之前？
能不能删掉三分之一，意思仍然完整？
还有一个很有效的测试：
假设这段话要发给一个聪明但不懂这个专业的朋友，他能不能第一次读完就复述？

注意不是“他觉得自己懂了”，而是能不能复述。
可复述性比“看起来清楚”更可靠。
五、真人要怎么教？
对真人不要直接说：
你能不能别说这些鬼话？

虽然有时很解气，但他往往只会觉得你在否定他的专业性。
更有效的是指出具体的接收失败：
我知道这句话对你来说很准确，但我读到“异构协同调度”时就断了。你能不能直接告诉我，是谁把什么任务分给了谁？

或者：
你这段不是内容太深，而是结论出现得太晚。先把最后一句移到最前面试试。

或者：
你现在讲的是你怎么想明白的。我想先听你最后想明白了什么。

还有一种很有效的方法：让他做同一内容的三档表达。
对同行讲，允许专业术语；
对大学生讲，术语必须解释；
对完全不了解的人讲，只保留结论、因果和例子。
久而久之，他会意识到：简单不是删减知识，而是重新编码知识。
六、训练人工智能智能体（AI agent）时，要写成“验收标准”
对人工智能只说：
请说人话，避免术语堆砌。

效果通常不稳定，因为它不知道“人话”的边界在哪里。
你需要告诉它：
面向谁；
想让读者做什么；
什么表达禁止；
输出顺序；
如何自检；
什么情况下允许保留术语。
下面这段可以直接放进 Codex 的系统提示词或写作规则里。
可直接使用的提示词
你的首要目标不是展示知识量，而是让非专业读者快速理解、记住并愿意继续阅读。
写作时遵守以下规则：
先给结论，再解释原因。禁止用背景介绍、宏观趋势或概念定义开头。
使用读者会自然说出的词。能用具体动作表达时，不使用抽象名词。
专业术语只有在不可替代或读者之后需要使用该术语时才能保留。术语第一次出现时，必须立刻用一句普通话解释。
不要把分析过程原样输出。先完成思考，再按“结论—原因—例子—限制”的顺序重新组织。
一句话只表达一个主要意思。超过两个逗号时，优先拆句。
不要使用“赋能、范式、生态、闭环、抓手、底层逻辑、技术边界、技术雷达、多维度、系统性能力”等空泛词语，除非随后立即说明具体是谁做了什么。
不要为了显得客观而习惯性加入“但是、不过、一定程度上、某种意义上”。只有当限制会显著改变结论时，才需要写出。
标题的任务是制造明确兴趣，不是提前呈现完整辩证分析。除非内容核心就是反驳或揭露，否则标题中不要加入“但是”“争议”“仍有局限”等削弱兴趣的表达。
不使用“这不仅是……更是……”“标志着进入新阶段”“打开想象空间”等缺少具体信息的套话。
每写完一段，检查读者能否用一句普通话复述。不能复述就继续简化。
输出前进行一次静默改写：
删除没有新增信息的句子；
把最重要的结论移到最前面；
把抽象名词改成具体的人、物体和动作；
把不必要的术语换成普通表达；
删除至少 20% 的文字，但保留关键信息。
当“专业严谨”和“容易理解”发生冲突时，采用分层表达：先给足够正确的简单结论，再补充必要条件，不要一开始就倾倒全部细节。

七、专门针对标题，再加一套规则
标题和正文不是同一种语言。nerd 最常见的错误是把正文摘要当标题。
标题应该回答：
为什么我现在就要点进去？

而不是：
这篇内容经过辩证分析后的完整结论是什么？

可以给 Codex 加上：
生成标题时，优先突出以下一种元素：规模、速度、反常识、直接收益、强烈画面、明确问题或新鲜事实。
标题只能有一个主要钩子。
不要同时承担介绍、论证、质疑和总结四个任务。
不要为了全面而主动削弱标题中的兴奋感。
风险、限制和争议应放在正文中，除非它们本身就是视频的核心冲突。

例如：
差：
191 皮秒光脑实现突破，但距离实际应用仍有距离

好：
191 皮秒完成一次计算，这台光脑到底有多快？

差：
80C 电池引发关注，但高倍率并不等于实际快充

好：
45 秒放完电：80C 电池究竟是什么概念？

如果内容确实是辟谣，则可以把冲突变成明确卖点：
“45 秒充满”的 80C 电池，媒体到底说错了什么？

这时“限制”不是例行公事，而是故事本身。
八、最关键的一条：让他从“完整”转向“有效”
你可以一直用这句话纠正他：
别告诉我你知道多少，告诉我我需要先知道什么。

或者更狠一点：
你不是在提交思维日志，你是在向别人传递一个意思。

真正的“说人话”并不是降低智力密度，而是提高单位注意力里的有效信息量。复杂的人把简单问题说复杂，并不稀奇；真正厉害的人，是能把复杂问题说得简单，同时又不说错。
<!-- BraveCow Harness: end -->
