"""Rebuild the October report from committed, non-secret evidence (ReportLab)."""
from pathlib import Path
import json
import os
import math

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/harness-audit-2026-10-01.pdf'
FONT = Path(os.environ.get('HARNESS_REPORT_FONT', 'C:/Windows/Fonts/msyh.ttc'))
FONT_BOLD = Path(os.environ.get('HARNESS_REPORT_BOLD_FONT', 'C:/Windows/Fonts/msyhbd.ttc'))
pdfmetrics.registerFont(TTFont('ZH', str(FONT)))
pdfmetrics.registerFont(TTFont('ZHB', str(FONT_BOLD)))
W,H=595.28,841.89
INK=HexColor('#173044'); TEAL=HexColor('#007F7B'); MUTED=HexColor('#617482')
BG=HexColor('#F6F8F8'); LINE=HexColor('#D7E1E4'); AMBER=HexColor('#A65E10')
c=canvas.Canvas(str(OUT),pagesize=(W,H))
c.setTitle('BraveCow Harness 月度技术侦察与升级 | 2026-10-01')
c.setAuthor('BraveCow Harness')
body=ParagraphStyle('body',fontName='ZH',fontSize=10.5,leading=17,textColor=INK,wordWrap='CJK',spaceAfter=6)
small=ParagraphStyle('small',parent=body,fontSize=9,leading=14)
table_style=ParagraphStyle('table',parent=body,fontSize=9.3,leading=14)
page=0

def paragraph(text,x,y,width=499,style=body):
    p=Paragraph(text,style)
    _,height=p.wrap(width,1000)
    if y-height<53:
        raise ValueError(f'Page {page} overflow: {text[:50]}')
    p.drawOn(c,x,y-height)
    return y-height-8

def start(kicker,title,subtitle=''):
    global page
    if page:
        c.showPage()
    page+=1
    c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(TEAL);c.rect(40,H-49,25,3,fill=1,stroke=0)
    c.setFont('ZH',8.5);c.drawString(74,H-50,kicker)
    c.setFillColor(INK);c.setFont('ZHB',24);c.drawString(40,H-99,title)
    c.setStrokeColor(LINE);c.line(40,42,W-40,42)
    c.setFont('ZH',8);c.setFillColor(MUTED)
    c.drawString(40,27,'BRAVECOW / HARNESS 0.13.0 / 2026.10.01')
    c.drawRightString(W-40,27,f'{page:02d}')
    return paragraph(subtitle,40,H-116,515,small) if subtitle else H-127

def label(text,x,y,size=12,color=INK):
    c.setFont('ZHB',size);c.setFillColor(color);c.drawString(x,y,text)

def box(x,y,w,h,title,text,fill=white):
    c.setFillColor(fill);c.roundRect(x,y-h,w,h,8,fill=1,stroke=0)
    label(title,x+13,y-25,11)
    paragraph(text,x+13,y-36,w-26,small)

def table(rows,widths,y):
    cells=[[Paragraph(str(v),table_style) for v in row] for row in rows]
    t=Table(cells,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#E3ECEE')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),
        ('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),0.4,LINE),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#F0F4F5')])]))
    _,height=t.wrap(sum(widths),1000)
    if y-height<56:raise ValueError(f'table overflow page {page}: {height}')
    t.drawOn(c,40,y-height)
    return y-height-16

def arrow(x1,y1,x2,y2):
    c.setStrokeColor(MUTED);c.setFillColor(MUTED);c.setLineWidth(1)
    c.line(x1,y1,x2,y2)
    angle=math.atan2(y2-y1,x2-x1)
    path=c.beginPath();path.moveTo(x2,y2)
    for delta in [-0.5,0.5]:
        path.lineTo(x2-7*math.cos(angle+delta),y2-7*math.sin(angle+delta))
    path.close();c.drawPath(path,fill=1,stroke=0)

def pair_bars(title,before,after,x,y,w=235):
    label(title,x,y,12)
    scale=(w-65)/max(before,after,1)
    for i,(name,value,color) in enumerate([('之前',before,MUTED),('之后',after,TEAL)]):
        yy=y-29-i*30
        c.setFont('ZH',9);c.setFillColor(INK);c.drawString(x,yy,name)
        c.setFillColor(color);c.roundRect(x+30,yy-2,value*scale,10,3,fill=1,stroke=0)
        c.setFillColor(INK);c.setFont('ZH',9);c.drawString(x+35+value*scale,yy-1,str(value))

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
accept=load('reports/evidence-2026-10-01/acceptance.json')
radar=load('harness/catalog/technology-radar-2026-10-01.json')

y=start('MONTHLY EVOLUTION / VERIFIED DELIVERY','把失败路径变成可靠能力','技术侦察、存档、全控制面审计与安全升级；保留两项明确的外部阻塞。')
for x,value,title in [(40,'4 / 4','原始故障实验已修复'),(216,'5 / 5','已安装 CLI 流程通过'),(392,'0','启动 token 净变化')]:
    c.setFillColor(white);c.roundRect(x,y-102,163,102,8,fill=1,stroke=0)
    label(value,x+15,y-44,25,TEAL);label(title,x+15,y-75,10)
y-=126
y=paragraph('本轮发布 0.13.0：已知 Markdown 读取绕过数据库；损坏或锁定索引自动退回有界文本检索；短中文词可检索；源目录失联不再清空索引。启动测量与配置门禁使用同一 CLI，审计结果明确标注时间和范围。',40,y)
y=paragraph('四项采用均有本机收益证据。SQLite 回退与渐进披露属于成熟技术在本 Harness 的新应用，并非本月发明；外部版本、协议与论文独立记录，避免把“新发布”当成“应该安装”。',40,y)
label('14 个候选的决策漏斗',40,y-14,13)
y-=48
counts=[('采用',4,TEAL),('实验',1,HexColor('#66B5B0')),('延期',8,HexColor('#C5D3D9')),('拒绝',1,AMBER)]
xx=40
for name,n,color in counts:
    ww=515*n/14;c.setFillColor(color);c.rect(xx,y-16,ww,22,fill=1,stroke=0);xx+=ww
y-=42
y=paragraph('采用 4 项 · 实验 1 项 · 延期 8 项 · 拒绝 1 项。详细实验、兼容门禁、成本和回滚记录见技术雷达 JSON。',40,y,515,small)
y=paragraph('<b>仍需关注：</b>Memory Tidy 更新 API 失败，原定义回读未变，旧项目 ID 不在现有项目列表；内置 Edge 扩展连接失败，浏览器冒烟未通过。两者不伪装为完成，也未扩大权限或改写绑定。',40,y)
y=paragraph('回滚基线：harness-baseline-2026-10-01<br/>基线提交：e5c98972d48ca9bc8601fa0edf49f58640d13780<br/>更改前快照提交：34c2292；基线 tag 已在改动前推送并核对。',40,y,515,small)

y=start('01 / CONTROL PLANE','一个事实源，多个执行入口','覆盖 .codex、.agents、.claude、.openclaw，并交叉核对 .bravecow / ZCode。')
box(40,y,160,83,'执行入口','Codex / ZCode<br/>Claude / OpenClaw')
box(218,y,337,83,'共享 Harness','受管脚本、共享 Skill 与 runtime links<br/>inventory / lock / audit / acceptance')
arrow(201,y-42,216,y-42)
y-=109
box(40,y,247,89,'私有运行状态','账号、配置、自动化 prompt、水位线<br/>原地保留；仅发布非秘密证据')
box(306,y,249,89,'可复现仓库','受管实现、来源锁、验收与回滚契约<br/>日期快照、技术雷达与报告')
arrow(385,y+26,385,y+3)
y-=116
box(40,y,515,90,'记忆读取链路','已知文件 → 直接 Markdown；普通查询 → FTS5<br/>索引损坏 / 锁定 / 短词零命中 → 有界 Markdown 扫描<br/>Markdown 是事实源；索引是可替换缓存；Graphiti 保持退休。')
y-=115
y=table([['控制面','实测状态','边界'],['Codex / shared','52 个有效本地 Skill / 19 个共享 Skill','无共享副本遮蔽'],['插件缓存','36 个包；30 个逻辑插件已解析','87 个解析 Skill ≠ 当前注入数量'],['Claude / OpenClaw','5 / 26 个目录或链接项','各 1 个断链残留，保留并显式报告'],['自动化','5 个有定义任务 + 1 个历史目录','2 个 Harness 核心组件'],['第三方来源','27 个候选；19 个待审','不执行或启用未审计代码']],[106,221,188],y)
y=paragraph('插件缓存不等于启用；配置解析不等于实际连接；历史 PASS 不等于本轮验收。许可证文件检出为 18/60 个唯一 Skill 路径，只表示本地可见证据，不等于其余项目无许可证。',40,y,515,small)

y=start('02 / FINDINGS','先修可复现的错误','未发现本轮证据支持的 P0 事件。P1 代表可造成检索中断、错误测量或自动化维护失败的问题。')
y=table([['级别 / 状态','证据与影响','实际处理'],['P1 · 已修复','坏数据库使已知文件读取也报错；普通检索无降级。','直接读取跳过索引；异常回退有界 Markdown。'],['P1 · 已修复','“记忆”只有两个字符，trigram 无命中；缺失源目录曾删掉 1 条索引记录。','短词回退；不存在 / 不可读根目录不能触发索引清理。'],['P1 · 已修复','默认 PATH CLI 无法解析 features；配置门使用 0.159.2 可通过。','共用 CLI resolver；记录测量时间、可执行文件与范围。'],['P1 · 待处理','Memory Tidy API 更新失败；旧项目 ID 未注册。','定义完整保留，备份及候选 prompt 只保存在本机。'],['P1 · 待处理','Edge 扩展清单与会话命名均连接失败。','未创建标签或 daemon；浏览器版本升级延期。'],['P2 · 已修复','断链被 is_dir() 过滤而从 inventory 消失。','把 dangling link / junction 记为 broken-link。'],['P2 · 保留','Claude 字幕旧别名、OpenClaw desktop-control 链接目标缺失。','未确认替代语义，避免把旧入口随意指向新工具。'],['P2 · 保留','第三方工作树有私有改动；来源 / 安装版本分层。','保留 overlay；记录当前版本、官方 ref 与迁移门禁。']],[87,224,204],y)
y=paragraph('未修改现有 AGENTS.md 或全局记忆。33 个受保护配置 / 指令 / 记忆 / 自动化定义文件的哈希前后相同；安装器对 AGENTS 的测试只发生在独立临时目录。',40,y,515,small)

y=start('03 / TECHNOLOGY RADAR','采用机制，而不是追版本','首选能隔离实验、按现机验收、回滚成本低的改动。来源与决策逐项登记。')
cards=[('采用 01  /  有界检索回退','成熟 SQLite 特性在 Harness 的新应用。4 个原始故障从全部失败到全部通过；无网络、无向量服务、无数据改写。'),('采用 02  /  故障注入验收','把 agent eval 的路径与结果验证落实为本地测试：损坏、锁定、源丢失、编码错误、路径逃逸，以及安装后真实 CLI 调用。'),('采用 03  /  带来源的运行观测','配置门禁与 token probe 共用 CLI 解析器；记录日期与范围。自动化只读检查标为静态契约，不推断调度成功或实际用量。'),('采用 04  /  Skill 按需披露','入口 802 → 454 token，减少 348（43.4%）；升级细节移至条件引用。描述保持不变，启动 token 无变化。'),('实验 01  /  程序化工具发现','合成 100 个工具，仅投射 5 个候选：14,302 → 132 token。仅证明载荷减少；尚未证明选工具正确率、生产延迟或账单收益。')]
for title,text in cards:
    box(40,y,515,94,title,text);y-=108
y=paragraph('实验性方向沿用原生 code mode，无新增 MCP 服务或第三方执行层。执行工具前仍需完整 schema；减少输出不能以隐藏关键语义为代价。',40,y,515,small)

y=start('04 / DEFERRED & REJECTED','延期都有具体门槛','8 项延期、1 项拒绝；未达兼容与实机验收条件的版本，不进入受管安装来源。')
y=table([['候选','当前判断','再次评估需满足'],['MCP 2026-07-28 Tasks','Tasks 从核心移至扩展；本机适配未验证。','双端能力协商、取消、状态权限测试。'],['API 压缩 / 缓存诊断','原生 context management 已配置；Harness 不控制 Desktop API 请求。','自有 API 工作负载与 cached_tokens / 成本对照。'],['Browser Harness 0.1.13','本机 0.1.8 fork 有补丁；Edge 扩展连接失败。','逐项移植补丁并通过真实 Edge 操作和清理。'],['OpenClaw 2026.9.7','本机 2026.6.5；跨版本迁移与认证渠道风险未验证。','隔离迁移、渠道恢复与会话回滚测试。'],['ECC 2.2.2','Pi profile 不匹配本机需求；现有仅 3 个补丁 Skill。','目标文件 diff、许可证和 Codex 触发兼容。'],['Meta Harness 新 CLI','与现有安装器职责重叠，工作树有私有改动。','证明缺失能力，避免第二套配置写入者。'],['Windows CU 0.40 来源 pin','现机已解析 0.40；新安装锁仍为 0.39。','可审计 source commit、构建和原生 UI 验收。'],['Memory Tidy 契约','API 失败且旧项目不在当前列表。','明确项目绑定后，接口更新并完整回读。'],['图 / 向量服务 · 拒绝','未发现能抵偿服务和同步成本的实际召回缺口。','代表性漏召回数据集证明净收益再重启评估。']],[118,193,204],y)
y=paragraph('Codex CLI 最新稳定 0.159.3 增加账户安全设置提醒；现机 0.159.2 属于桌面应用管理。本轮不替换桌面内置二进制，也不将此补丁当作 Harness 能力升级。',40,y,515,small)

y=start('05 / VERSIONS & CONTEXT','节省发生在哪里','o200k_base 静态估算；同一 CLI、同一工作目录。不是活跃 Desktop 对话的上下文或计费用量。')
pair_bars('CLI 启动 prompt',6770,6770,40,y-5,235)
pair_bars('审计 Skill 正文',802,454,312,y-5,220)
y-=123
y=paragraph('启动：6,770 → 6,770，净变化 0。描述：2,585 → 2,585，49 个 CLI catalog 条目。Skill 入口缩短 43.4%；升级任务还需加载新 reference，不能把入口节省外推为所有任务的节省。',40,y,515,small)
y=table([['组件','当前 / 本轮落地','一手来源观察','处理'],['BraveCow Harness','0.12.0 → 0.13.0','本仓库','升级'],['Codex CLI','0.159.2','0.159.3','保留桌面所有权'],['Browser Harness','0.1.8 + 本地补丁','0.1.13','延期迁移'],['OpenClaw','2026.6.5','2026.9.7','延期迁移'],['ECC active slice','v2.1.0 兼容补丁','2.2.2','保留 3 个 Skill'],['Meta Harness','0.4 / eafb747','b6f543172494','保留本地版本'],['Windows Computer Use','0.40.0 已安装','安装器锁 0.39.0','记录分层差异']],[129,153,106,127],y)
y=paragraph('最新版本通过官方 GitHub release API 与 tag/commit 解析核实，记录观察时间、来源 URL、不可变 ref 和声明许可证。没有执行上游安装器或新增第三方依赖。',40,y,515,small)

y=start('06 / ACCEPTANCE','先证明坏了，再证明恢复','结果来自隔离故障注入、已安装脚本调用与本机已知 Markdown 读取。')
y=table([['故障 fixture','更改前','更改后'],['已知 Markdown + 坏数据库','DatabaseError','direct；不打开数据库'],['普通查询 + 坏数据库','DatabaseError','markdown-scan；坏文件保留'],['两字中文“记忆”','零结果','命中 canonical Markdown'],['源目录不存在','索引删除 1 条','拒绝更新；旧索引保留']],[217,125,173],y)
label('已安装 CLI：5 / 5 通过',40,y-3,13,TEAL)
y-=27
for item in accept['installed_cli_cases']:
    name=item['case']; ms=item['decision']['latency_ms']
    c.setFillColor(INK);c.setFont('ZH',9.5);c.drawString(40,y,name)
    c.setFillColor(TEAL);c.roundRect(156,y-2,max(3,ms*9),9,3,fill=1,stroke=0)
    c.setFillColor(INK);c.drawString(425,y,f'{ms:.2f} ms')
    y-=25
y-=8
y=paragraph('坏索引回退：20 次小型 fixture，中位数 1.315 ms，最大 1.67 ms；本机已知文件直读 0.60 ms。这些是观测值，不是生产 SLA；锁等待上限为每连接 250 ms。',40,y,515,small)
y=table([['验收项','结果与边界'],['Python 单测','58 项：57 通过，1 项因本机不允许建 symlink 跳过；实际 junction 已在 live inventory 检出。'],['配置 / 触发契约','现机语义门禁 PASS；50/50 触发契约通过（非实时模型路由测试）。'],['安装器 / 发布包','Windows Codex + ZCode 临时安装 PASS；用户文件 sentinel 保留；package gate PASS。'],['真实本机 / 保护','已安装 CLI 五条流程 + live Markdown 直读 PASS；33 个受保护文件未变。']],[124,391],y)

y=start('07 / AUTOMATION & ROLLBACK','状态、边界和恢复点','本轮自动化定义没有成功变更；提议保存在私有本地目录，仓库仅保存契约与结果。')
y=paragraph('<b>月度进化：</b>身份、调度结构、执行目标静态检查通过。旧运行记忆最后写于 8 月 1 日，与调度给出的 9 月触发时间不一致；不能据此补写“9 月成功”。本轮结束时记录当前证据与结果。',40,y)
y=paragraph('<b>Memory Tidy：</b>现有水位线文件可按 UTF-8 解码并带 BOM，最后修改为 8 月 16 日；本机未见其 backups 目录。prompt 中有增量与编码规则，但备份、secret 门禁、失败后水位线规则不明确。官方更新 API 返回失败，完整回读与原定义相同；旧项目 ID 不在当前注册列表，尚未证明这是 API 失败的唯一原因。',40,y)
y=paragraph('<b>数据与成本：</b>两项核心 prompt 的静态估计为 1,904 / 453 token；实际运行 token、延迟和历史成功率未观测。Graphiti 自动化仅留历史目录；不再有图同步水位线。本轮没有写全局记忆，也没有启动外部记忆服务。',40,y)
box(40,y,515,95,'受管文件备份','5 个 Python 脚本 + VERSION + 上游观察 + prompt baseline，共 8 项。<br/>私有收据保存前后 SHA-256；Skill 通过既有 repo junction 生效。<br/>位置：本自动化目录下 backups/2026-10-01。')
y-=117
y=paragraph('<b>回滚步骤：</b>停止新的 Harness 维护调用，按私有收据逐项恢复对应文件；Skill 从 baseline tag 恢复。再运行 config gate、inventory / audit 与相应测试。只恢复本轮受管文件，不回滚用户配置、自动化运行历史或 canonical Markdown。',40,y)
y=paragraph('<b>发布边界：</b>仅提交本轮代码、公开来源、脱敏快照与报告；推送 main 并回读远端 SHA。PDF 与其生成脚本同仓发布。基线 annotated tag 对象为 0ec63e0ea4de821d70e8a9fbd74da46d5cae0c2e，解引用提交为 e5c98972d48ca9bc8601fa0edf49f58640d13780。',40,y,515,small)
y=paragraph('<b>资源清理：</b>临时安装目录由 smoke test 清理；未创建浏览器标签、watcher 或 daemon，用户普通窗口未动。无其他仓库被修改。',40,y,515,small)

y=start('08 / SOURCES & REPRODUCTION','证据可以重新检查','以下为本轮实际读取的一手来源；完整候选字段与不可变版本 ref 在仓库 evidence / catalog 中。')
sources=[
('01  Codex 发布日志与 0.159.3','https://learn.chatgpt.com/docs/changelog'),
('02  MCP 2026-07-28 协议变化','https://blog.modelcontextprotocol.io/posts/2026-07-28/'),
('03  SQLite FTS5 / trigram 边界','https://www.sqlite.org/fts5.html#the_trigram_tokenizer'),
('04  代码执行与 MCP','https://www.anthropic.com/engineering/code-execution-with-mcp'),
('05  MCP 设计取舍原始论文','https://arxiv.org/abs/2602.15945'),
('06  Agent 工作流评测','https://developers.openai.com/api/docs/guides/agent-evals'),
('07  上下文工程与渐进披露','https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents'),
('08  API 压缩','https://developers.openai.com/api/docs/guides/compaction'),
('09  Prompt 缓存诊断','https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics'),
('10  Browser Harness 0.1.13','https://github.com/browser-use/browser-harness/releases/tag/v0.1.13'),
('11  ECC 2.2.2','https://github.com/affaan-m/ECC/releases/tag/v2.2.2'),
('12  OpenClaw 2026.9.7','https://docs.openclaw.ai/releases/2026.9.7'),
('13  Meta-Harness 同名研究（非本机仓库）','https://arxiv.org/abs/2603.28052'),
('14  Computer Use API 与安全边界','https://developers.openai.com/api/docs/guides/tools-computer-use'),
('15  本机 Meta Harness 的上游提交','https://github.com/SaehwanPark/meta-harness/commit/b6f54317249478f4c196cabe68e1c948aaa6a404')]
for title,url in sources:
    y=paragraph(f'<link href="{url}" color="#007F7B">{title}</link>',40,y,515,small)
y-=6
y=paragraph('<b>复现入口</b><br/>python -m unittest discover -s tests<br/>python tests/validate_package.py<br/>powershell -File tests/smoke_install.ps1<br/>python reports/build_audit_2026_10_01.py',40,y,515,small)
y=paragraph('关键证据：reports/evidence-2026-10-01/acceptance.json；baseline 与 post-upgrade 日期目录；harness/catalog/technology-radar-2026-10-01.json。PDF 重建需要 ReportLab 和可嵌入中文字体，字体路径可通过 HARNESS_REPORT_FONT / HARNESS_REPORT_BOLD_FONT 指定。',40,y,515,small)
c.save()
print(f'Created {OUT.name}: {page} pages')
