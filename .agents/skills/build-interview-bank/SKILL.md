---
name: build-interview-bank
description: 将面经裸题编写为教学面试题：语义去重、来源定难度、编写推荐答案与进阶理解并附实际查阅的官方参考，经未参与编写的独立 Agent 审核通过（SHA-256 一致）后按分类/难度单题入库。
---

# 面经题编写与入库

输入为批次 `candidates.json` 中 `pending` 的裸题，或已有题目的修订请求。产出 1.0 契约单题 JSON，经独立审核后入库。

## 流程

1. **去重**：按 [准入审核](references/admission-review.md) 四维规则与既有题库及本批已保留题比较，>70% 弃，登记 `duplicate_of:Qxx`；同题面再次出现时给已有题的 `editorial_provenance.frequency` 加一并修订教研备注。
2. **定档**：直问概念/机制默认 low；需要选型、定位、边界判断为 medium；high 仅当帖子真实出现系统性追问链或跨模块设计题，补写场景不升档。
3. **编写**：按 [数据契约](references/content-contract.md) 生成 JSON，答案依据官方文档/论文编写，`technical_references` 只记实际查阅的来源；候选人自述答法只作题面语境，不作为技术依据。
4. **独审**：交未参与编写的独立 Agent 审核并生成审核记录；`passed` 且 SHA-256 与文件字节一致才登记。
5. **入库**：`python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --file <相对路径>`，随后同步根 README 统计。

## 硬性规则

- 公司/岗位/轮次经 `editorial_provenance` 记录，并在学员版 Markdown 的「真题来源」行渲染（标注发帖人自述、未核实）；答案正文等学员侧 JSON 字段（title/tags/question_guide/recommended_answer/technical_answer/example）仍不得内嵌公司名——公司信息只走来源行，不混入教学内容。
- 发帖人身份与原帖正文/图片只进批次记录（教研侧），学员版不展示；按公司刷真题的入口为批次目录 `mianjing/`（学员可用）。
- 不虚构企业项目、业绩数字；无结果的验证写验证计划。
- ID 全局唯一递增（Q001 起），编号空洞不复用；编号分配前检查 catalog 与本批预留。
- 修订已有题：改 JSON → 重新独审绑定新 SHA → `--question Qxx` 重新生成。
- 学员正文不出现「博主/发帖人/原帖/教研补充」旁白。
