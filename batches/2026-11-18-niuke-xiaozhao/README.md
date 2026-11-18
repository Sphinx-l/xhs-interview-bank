# 批次 2026-11-18-niuke-xiaozhao（校招定向）

牛客网**校招定向**采集批次。关键词：「Agent 秋招 面经」。全部题源按帖内 #秋招面试记录# 等标记归为校招。

## 统计

| 口径 | 数量 |
|---|---|
| 冻结卡片 | 19（与既有 6 批次按 post_id 去重后新卡 12） |
| 标题排除 | 4（杂谈×3、浪潮 C++ 非方向×1） |
| 内容复核 | 8 |
| **保留题源（全部校招）** | **7 篇 / 131 行题目** |
| 跨源判重 | 1（7b1b40fd 字节 TikTok Agent 一面与批次二 6a7dc3af 题面逐条同文，同一场面试的牛客帖，题面不重复收录） |

## 题源亮点

- **蚂蚁 AI-Agent 开发秋招一面**：26 行（Markdown 记忆 vs RAG / Agent Teams vs Workflow / Harness / Skill 懒加载 / Temperature=0 仍有差异）
- **小红书 Agent 开发一面/二面**（同公司两场）：OpenManus 框架选型 / LangGraph 对比 / 多 Agent 资源争抢与上下文隔离 / Prompt Injection 防范 / Planner-Executor-Critic vs ReAct / 广告投放自我迭代场景题
- **虾皮 Agent 开发一面**：19 行（ReAct 流程 / Tool Message 设计 / 父子索引 / BM25+向量+Rerank / Agentic CFT / Observation Token Mask）
- **字节 Agent 全三轮**：DeepSeek harness 与 pi 区别 / Claude Code 上下文压缩 / computer use 原理 / 企业级 Agent 判定
- 百度 agent 三面（25 分钟 4 题）、字节 agent 一面（双非本，疑 KPI 面）——题面真实偏少，索引注明

## 目录

- `mianjing/` — **主产物**：7 篇校招面经 + [按公司索引](mianjing/README.md)
- `manifest.json` — 12 篇卡片状态（含 1 条 cross_source_repost 指向批次二）
- `cards_frozen.json` / `_tabbit/` — 冻结清单与采集详情快照
