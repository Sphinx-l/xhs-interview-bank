# 准入审核与独立知识审核

## 语义去重（四维评审）

对候选题与最相近既有题按四维打分：核心问题 40、解题路径 30、知识边界 20、关键约束 10。

- 合计 **>70% 不入库**，candidates 记 `duplicate_of:Qxx`，reason 写各项分值与理由。
- 恰好 70% 复审：只有来源支持的实质增量才保留。
- 这是教研语义评审，不冒充 Embedding 分数或统计概率。不靠换公司名、改数字、加模拟约束掩盖重复。
- 同题面再出现：已有题 `frequency` +1 并修订教研备注，不新建题。

## 难度

| 档 | 条件 |
| --- | --- |
| low | 直接解释概念、组成、机制、区别 |
| medium | 选型、定位瓶颈、边界判断 |
| high | 帖子真实出现系统性追问链或跨模块设计题（保留原帖证据） |

## 独立知识审核（硬门禁）

- 审核者为**未参与该题编写**的 Agent；通读推荐答案、进阶理解、示例与导读。
- 逐项核对：题干子问覆盖、术语与机制、API/版本边界、关键主张对照官方文档实际核查、示例可理解性。
- 审核记录 `batches/<batch_id>/reviews/content-<ID>.json`：

```json
{
  "question_id": "Q001", "note_id": "…",
  "author_agent": "…", "reviewer_agent": "…",
  "canonical_path": "question_bank/<cat>/<level>/Q001.json",
  "canonical_sha256": "…",
  "reviewed_sections": ["recommended_answer", "technical_answer"],
  "claims_checked": [{"claim": "…", "evidence": "官方文档 URL", "result": "confirmed"}],
  "issues": [], "revision_history": [],
  "decision": "passed", "reviewed_at": "2026-11-16T12:00:00"
}
```

- `needs_revision` 退回编写者修订后复核；根本概念错误不放行。审核者不代写后给自己通过；结构脚本通过不替代知识审核。
- 仅 `decision=passed` 且 `canonical_sha256` 与当前 JSON 字节一致时，`manage_bank.py --file` 才会登记。
