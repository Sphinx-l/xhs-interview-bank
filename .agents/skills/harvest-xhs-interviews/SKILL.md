---
name: harvest-xhs-interviews
description: 从小红书关键词/话题搜索采集面试经验帖：冻结清单、筛选 AI/Agent 方向候选、正文与图片画面复核提取裸题，产出批次 manifest 与 candidates 交接给 build-interview-bank。
---

# 小红书面经采集与筛选

产出「冻结清单 + 裸题候选表」，交给 build-interview-bank Skill 编题。本 Skill 不编写答案。

## 批次建立

- 每次搜索采集建一个批次：`batches/YYYY-MM-DD-keyword-slug/`，含 `README.md`、`manifest.json`、`screening_log.md`、`notes/`（正文快照与图片）、`reviews/`（编题阶段写入）。不覆盖旧批次。
- 记录采集日期、关键词、结果总数、是否加载到底。

## 搜索与冻结清单

- 入口为关键词/话题搜索（如「Agent 面经」「大模型面试题」），经用户已登录浏览器操作，滚动分页。
- 按笔记 ID 去重，排除广告与推荐流；冻结本批清单。工具与登录状态随环境变化，不沿用旧 tab ID 或过期签名；新采集方式先用一个候选验证再批量。
- 遇验证码/风控如实记录并停止，不轮询猜测接口；不持久化 Cookie、令牌、私钥。

## 筛选规则

- 标题/正文初筛直接排除并记录理由（「按标题排除，未读正文」或复核结论）：非 AI/Agent 方向、纯引流卖课、明显 AI 批量生成的题目合集（无真实面试来源痕迹）、剧情/日常。
- 候选笔记读完整内容后复核：题面是否真实面试题、是否属于技术范围。公司/岗位/轮次一律视为发帖人自述，原文记录，值为空用 `unspecified`，不推断、不核实、不进学员版。

## 内容获取与画面复核

- 图文笔记：保存正文原文快照与原图到 `notes/<note_id>/`。
- 题目在图片里的，由 Agent 视觉读取图片，提取文字保存为 `notes/<note_id>/image-extract.md`，每条题面标注来源图片文件名与「画面提取」。图片不可靠读取的题不入库，记 `unreadable_image`。不引入 OCR 工具，不把画面提取记为正文原文。
- 视频笔记本阶段不处理，记 `out_of_scope_video`。

## 裸题候选表 candidates.json

批次根目录保存，是两个 Skill 的交接产物：

```json
{
  "batch_id": "2026-11-16-agent-mianjing",
  "keyword": "Agent 面经",
  "collected_at": "2026-11-16T08:00:00+08:00",
  "notes": [{"note_id": "…", "url": "…", "title": "…", "status": "retained", "reason": "", "company": "字节", "role": "Agent 开发", "round": "一面"}],
  "candidates": [{"candidate_id": "C001", "question_verbatim": "面试问：…", "extraction": "note_text", "note_id": "…", "company": "字节", "role": "Agent 开发", "round": "一面", "status": "pending", "reason": ""}]
}
```

`candidates[].status`：`pending` / `admitted` / `duplicate_of:Q001` / `rejected`，理由写 `reason`。帖内重复题合并后再进 candidates。

## manifest.json 核心字段

`note_id`、`url`、`title`、`published_at`（核实到才填）、`status`（`retained` 或具体排除/失败状态）、`reason`、`company/role/round`（教研侧）、`question_ids`（该笔记产出题目）。统计口径：可见笔记数、标题排除数、内容复核数、画面提取数、不可读数分别记录，不混用。
