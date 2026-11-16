# 设计：小红书面经 → AI/Agent 面试题库工作流

日期：2026-11-16
状态：已与使用者确认，作为实施依据

## 1. 背景与目标

参考现有抖音题库工作流（`douyin-data-analyze`，只读，不改动），为本项目搭建一套从小红书**面试经验帖（面经）**中提取 AI/Agent 方向面试题的内容工作流。

与抖音流程的本质差异：抖音博主提供「讲解」，题库主要做校验与结构化；面经帖提供的是**真实被问到的裸题**，答案完全由本项目编写并查证。因此本项目的重心在采集筛选、题面提取、答案编写与独立审核。

**验收形态**：跑通一个关键词批次的完整链路——采集 → 筛选 → 题面提取 → 语义去重 → 答案编写 → 独立 Agent 审核 → 单题 JSON 入库 → 生成 Markdown 索引，统计口径可追溯。

## 2. 已确认的范围决策

| 决策点 | 结论 |
| --- | --- |
| 素材类型 | 面经帖（候选人分享的真实面试题），非技术教程笔记 |
| 技术范围 | 仅 AI/Agent/大模型方向 |
| 项目位置 | 独立仓库 `D:\yuege\xhs-interview-bank`；参考仓库只读，不改动、不复制其题库与审核记录 |
| 交付范围 | 先做内容流程（Skill + 批次 + 题库 JSON + 脚本），刷题网站为后续可选阶段 |
| 采集入口 | 小红书关键词/话题搜索，不按作者主页组织 |
| 公司/岗位/轮次 | 仅存教研侧（manifest 与 editorial 备忘），学员版不展示、不筛选 |
| 图片处理 | 画面复核：保存原图由 Agent 视觉读取，不引入 OCR 工具链 |

## 3. 总体架构

```text
xhs-interview-bank/
  .agents/skills/harvest-xhs-interviews/   # Skill 1：小红书采集与筛选
    SKILL.md
    references/acquisition.md              # 搜索采集、画面复核、清单冻结
  .agents/skills/build-interview-bank/     # Skill 2：编题与入库
    SKILL.md
    references/content-contract.md         # 单题 JSON 契约（1.0）
    references/admission-review.md         # 去重、难度、独立审核门禁
    scripts/manage_bank.py                 # 登记/校验/生成脚本
    scripts/test_manage_bank.py
  question_bank/                           # 单题 JSON（唯一事实源）+ 生成的 Markdown
    catalog.json / taxonomy.json / README.md / TAGS.md
    <category-id>/<high|medium|low>/Qxx.json
    editorial/Qxx.md                       # 教研备注（生成）
  batches/YYYY-MM-DD-keyword-slug/         # 每次搜索采集一个批次
    README.md / manifest.json / screening_log.md
    notes/          # 笔记正文快照、图片、画面提取结果
    reviews/        # 独立审核记录
  docs/                                    # 本设计文档与工作流说明
```

分层原则：**采集归批次、编题归 Skill、事实归 JSON**。两个 Skill 通过批次目录与 manifest 衔接：`harvest-xhs-interviews` 产出「冻结清单 + 裸题候选表」，`build-interview-bank` 从候选表开始编题。

## 4. 采集层（harvest-xhs-interviews）

### 4.1 搜索与清单冻结

- 入口为关键词/话题搜索（如「Agent 面经」「大模型面试题」），经用户已登录浏览器操作，滚动分页加载。
- 按笔记 ID 去重，排除搜索结果中的广告与推荐流；冻结本批清单，记录采集日期、关键词、结果总数与是否加载到底。
- 每次采集用一个批次目录，`manifest.json` 按 `note_id` 记录：`url`、`title`、`published_at`（核实到才填）、`status`（`retained` / 具体排除或失败状态）、`reason`、`company`、`role`、`round`（帖子里有则记原文，无则 `unspecified`，不推断）、`question_refs`（该笔记产出的题目 ID）。
- 工具与登录状态随环境变化，不沿用旧 tab ID 或过期签名；新采集方式先用一个候选验证再批量。遇验证码/风控时如实记录，不轮询猜测接口。

### 4.2 内容获取与筛选

- 小红书笔记以图文为主：内容提取 = **正文文本 + 图片画面复核**。保存正文原文快照与原图；题目在图片里的，由 Agent 视觉读取，提取文字单独保存并标注「画面提取」及来源图片文件名。
- 图片清晰度不足以可靠读取的题目不入库，该笔记或该题记为 `unreadable_image`，不冒充已提取。
- 标题/正文初筛直接排除：非 AI/Agent 方向、纯引流卖课、明显 AI 批量生成的题目合集（无真实面试来源痕迹）、剧情/日常。理由记入 `screening_log.md`，标注「按标题排除，未读正文」或具体复核结论。
- 候选笔记需读完整内容后复核：题面是否真实面试题、是否属于本项目技术范围、公司岗位信息是否可信（一律视为发帖人自述，不做事实断言）。
- 不持久化 Cookie/令牌/私钥；原始笔记内容只进教研侧批次目录。

## 5. 题面提取与语义去重（两 Skill 交接处）

- 一条面经帖通常含多条裸题。逐条提取为候选题，记录：原题面文字（正文或画面提取）、来源笔记 ID、公司/岗位/轮次（教研侧）。
- **帖内去重**：同一帖重复出现的题合并。
- **跨帖去重**：沿用参考仓库的四维语义评审——核心问题 40 / 解题路径 30 / 知识边界 20 / 关键约束 10，与既有题库及本批已保留题比较，**>70% 弃**；恰好 70% 复审，有实质增量才保留。分数是教研判断记录，不冒充 Embedding 或统计概率。
- 面经题重复率高（「什么是 Agent」「RAG 流程」会在大量帖子里出现）：先入库版本为基准，后来的重复题在 manifest 登记为「已有题 Qxx 覆盖」，不重复入库；同一题面的出现次数记入教研侧 `frequency`，作为热门考点参考。
- 不以换公司名、改数字、加模拟约束掩盖重复。

## 6. 答案编写与独立审核（build-interview-bank）

### 6.1 数据契约（1.0 版）

借鉴参考仓库 3.1 契约简化，从零定义，不兼容其历史数据：

- 回答类型：`technical`（技术问答）为主；面经基本无企业场景，初期不设 `case_study`，后续确有系统性设计题再扩展。
- `technical` 必需 `recommended_answer = {summary, points}`：summary 1–2 句直接结论；points 1–6 条非空文本，覆盖题干全部子问；约 180–350 汉字。
- `technical_answer` 为进阶理解（机制、对比、流程、小例子、边界），无 summary 字段，不与推荐答案同义重复。
- 保留四块导读：背景、痛点、考点（含 3–5 个具体技术 TAG）、思路。
- 来源块：`source_type: "xhs_note"`、`note_id`、题面原文字句、画面提取标记；公司/岗位/轮次只进 `editorial_provenance` 与批次 manifest。
- `technical_references` 记录答案编写时**实际查阅**的官方文档/论文，不是装饰字段。
- 分类沿用参考仓库的 9 类 taxonomy（AI Agent 架构设计、Agent 性能优化、Agent 成本优化、RAG 检索与知识组织、Agent 评测与可靠性、模型选型与微调、Agent 数据治理、Agent 工程化与运行环境、Agent 学习与策略优化），英文 ID，允许按面经实际分布新增注册。
- 难度：直问概念/机制默认 low；需要选型、定位、边界判断为 medium；**high 需帖子里真实出现系统性追问链或跨模块设计题**才可评，补写场景不升档。
- 题目 ID：`Q` + 三位递增数字，全局唯一，编号空洞不复用。

### 6.2 答案编写规范

- 答案依据官方文档/论文编写，绝对化结论修正为可验证表述；帖子里附带的候选人个人答法不作为技术依据，只作题面语境参考。
- 示例先说明谁在做什么、要解决什么问题，再给动作与观察；术语、字段先解释对象与用途。
- 不虚构企业项目、空 STAR、分阶段业绩；无结果的验证写验证计划。
- 学员版不出现博主/发帖人/原帖/教研补充旁白。

### 6.3 独立知识审核（硬门禁）

照搬参考仓库的门禁逻辑：

- 每题最终 JSON 交**未参与编写的独立 Agent** 通读审核：推荐答案是否覆盖全部子问、进阶理解是否成立、术语/机制/API 版本边界、关键主张对照官方文档实际核查、示例是否可理解。
- 审核记录存批次 `reviews/`：`question_id`、`note_id`、`author_agent`、`reviewer_agent`、`canonical_path`、`canonical_sha256`、`reviewed_sections`、`claims_checked`、`issues`、`revision_history`、`decision`（`passed/needs_revision/rejected`）、`reviewed_at`。
- 仅 `passed` 且审核 SHA-256 与当前文件字节一致才登记入库、生成 Markdown；`needs_revision` 退回编写者修订后复核；根本错误不放行。
- 审核者不代写后给自己通过；结构脚本通过不能替代知识审核。

## 7. 脚本与工具

自己实现（参考仓库脚本只读借鉴思路）：

```sh
python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --file <rel-path>   # 新题登记
python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --question Q01      # 单题校验+生成
python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --check            # 全量只读审计
python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --all              # 全量重建
```

校验项：分类/难度路径合法、TAG 数量 3–5 且非泛词、`recommended_answer` 结构、`technical_answer` 无 summary 残留、来源笔记覆盖（每题有 note_id 且 manifest 可追溯）、学员版无公司/发帖人信息泄漏、教研字段不进学员版、审核哈希一致性、模拟数据标记。配 `test_manage_bank.py` 单元测试。

## 8. 统计口径与文档

- 批次 README 记录：搜索关键词、可见笔记数、标题排除数、内容复核数、画面提取数、不可读数、裸题提取数、去重弃数、入库数，口径不混用。
- 根 README 从最新 catalog/taxonomy/manifest 汇总当前题数、分类与难度分布；不把清单总量说成提取量或入库量。
- 每次交付说明：新增/排除/失败数量、独审结果、可用入口、影响使用的限制。

## 9. 非目标

- 不搭建 React 刷题网站（后续可选阶段，届时另行设计）。
- 不改动、不复制参考仓库的题库、批次、审核记录与其 Skill。
- 不做无人值守采集服务；浏览器登录由用户维护。
- 不引入云端 OCR/ASR 或付费服务。

## 10. 交付节奏

1. 搭建仓库骨架：两个 Skill 文档、契约与审核规范、脚本与测试、空题库结构。
2. 首个关键词批次试运行，验证契约与脚本，暴露问题后修订。
3. 扩展更多关键词批次，沉淀题库。
