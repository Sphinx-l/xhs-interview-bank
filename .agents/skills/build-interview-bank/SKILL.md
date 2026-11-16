---
name: build-interview-bank
description: 将面经裸题编写为教学面试题：语义去重、来源定难度、编写推荐答案与进阶理解并附实际查阅的官方参考，经未参与编写的独立 Agent 审核通过（SHA-256 一致）后按分类/难度单题入库。
---

# 面经题编写与入库

输入为批次 `candidates.json` 中 `pending` 的裸题，或已有题目的修订请求。产出 1.0 契约单题 JSON，经独立审核后入库。

## 流程

1. **去重**：按 [准入审核](references/admission-review.md) 四维规则与既有题库及本批已保留题比较，>70% 弃，登记 `duplicate_of:Qxx`；命中已有题时立即用 `--sighting` 把本次出现登记到该题的 `occurrences`（出现时间、公司/岗位/轮次、批次与笔记 ID），热度信号不丢弃。
2. **定档**：直问概念/机制默认 low；需要选型、定位、边界判断为 medium；high 仅当帖子/口述真实出现系统性追问链或跨模块设计题（追问链记入 `follow_up_chain`，按发问顺序、含自身），补写场景不升档。
3. **编写**：按 [数据契约](references/content-contract.md) 生成 JSON，答案依据官方文档/论文编写，`technical_references` 只记实际查阅的来源；候选人自述答法只作题面语境，不作为技术依据。`occurrences` 首条为入库来源。
4. **独审**：交未参与编写的独立 Agent 审核并生成审核记录；`passed` 且 SHA-256 与文件字节一致才登记。
5. **入库**：`python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --file <相对路径>`，随后同步根 README 统计。

## 硬性规则

- 公司/岗位/轮次、发帖人、原帖信息只进 `editorial_provenance` 与批次记录，学员版 JSON 字段与 Markdown 均不得出现。
- `occurrences` / `frequency` / `follow_up_chain` 为教研侧字段：`frequency` 由脚本派生不手改；后续出现只经 `--sighting` 登记（脚本校验并重绑审核哈希）；`follow_up_chain` 只录真实追问链。
- 不虚构企业项目、业绩数字；无结果的验证写验证计划。
- ID 全局唯一递增（Q001 起），编号空洞不复用；编号分配前检查 catalog 与本批预留。
- 修订已有题：改 JSON → 重新独审绑定新 SHA → `--question Qxx` 重新生成。
- 学员正文不出现「博主/发帖人/原帖/教研补充」旁白。
