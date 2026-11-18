# 1.1 数据契约

唯一事实源：`question_bank/<category-id>/<low|medium|high>/<ID>.json`。同路径 `.md` 与 `editorial/<ID>.md` 由脚本生成，不手改。

分类与难度以 `question_bank/taxonomy.json` 为准（9 类，英文 ID）。TAG 3–5 个具体技术词，禁用泛词：ai、面试、高级、人工智能、大模型、agent、llm。

## 字段

| 字段 | 约定 |
| --- | --- |
| `id` / `version` | `Q\d{3}` 递增；`"1.1"` |
| `answer_type` | v1.1 仅 `"technical"` |
| `category_id` / `difficulty` | taxonomy 注册分类；`low/medium/high` |
| `title` | 题面改写的教学化问句，独立可读 |
| `tags` | 3–5 个，具体概念/机制/方法/框架 |
| `question_guide` | `background/pain_point/focus/approach` 四键非空；背景 1–2 句，思路 2–3 步 |
| `recommended_answer` | `summary` 1–2 句直接结论；`points` 1–6 条非空，覆盖题干全部子问；整体约 180–350 汉字 |
| `technical_answer` | 无 `summary` 键；`sections` ≥1 段（heading/body）；可选 `example`（scenario/steps/observation） |
| `source` | `source_type:"xhs_note"`、`note_id`、`question_verbatim`（题面原文，含原错别字）、`extraction`（`note_text/image_reading`）、`batch_id` |
| `editorial_provenance` | `company/role/round`（无信息 `"unspecified"`）、`frequency`（≥1 整数）、`notes`；渲染为学员版「真题来源」行（标注发帖人自述），`notes` 明细仅教研侧 |
| `technical_references` | ≥1 条 `{title,url}`，实际查阅的官方文档/论文 |
| `related_questions` | 0–4 条，有具体理由才加，不含自身、不重复 |

## editorial_provenance（仅教研侧）

| 键 | 约定 |
| --- | --- |
| `company` / `role` / `round` | 无信息 `"unspecified"`；一律自述原文，不推断 |
| `occurrences` | ≥1 条出现记录，首条为入库来源。每条：`batch_id`、`note_id` 或 `recall_id`（与 `source_type` 匹配）、`company/role/round`（无信息 `"unspecified"`）、`seen_at`（`YYYY-MM-DD`，取批次采集日）。`(batch_id, 来源ID)` 组合不得重复 |
| `frequency` | 派生值 = `occurrences` 条数；可省略，填了必须相等。首条随编写录入，后续由 `--sighting` 登记，不手工改 |
| `follow_up_chain` | 可选：同一场面试真实追问链的 Qxxx ID 列表，按发问顺序、含自身、不重复。仅录帖子/口述真实出现的追问（对应采集侧 `chain_order`），补写场景不入链 |
| `notes` | 纠错、改写与其他教研备注 |

`first_seen` / `last_seen` 不入题目 JSON，由脚本从 `occurrences.seen_at` 派生写入 catalog，支撑"最近 N 周"类查询。

## 编写规范

- 推荐答案可直接用于面试表达；进阶理解解释机制、条件与边界，不与推荐答案同义重复。
- 示例先说明谁在做什么、要解决什么问题，再给动作与观察；术语先解释对象与用途。
- `question_verbatim` 保留原帖题面（含原错别字）；纠错与改写说明写 `editorial_provenance.notes`。
- 学员口述来源（student_recall）的 `question_verbatim` 为口述整理稿；公司/岗位/轮次仍按学员自述记入教研侧。

完整合法示例见 `scripts/test_manage_bank.py` 的 `BASE` 基件。
