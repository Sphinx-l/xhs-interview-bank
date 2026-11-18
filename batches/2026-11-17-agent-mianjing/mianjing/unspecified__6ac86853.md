# unspecified · Agent 开发 · 面经原文（笔记 6ac86853000000001801b00e）

- 来源：[(无标题笔记)](https://www.xiaohongshu.com/explore/6ac86853000000001801b00e?xsec_token=ABW5_clKgK-wSTwyqnbk-Iit572Y0FA2H4le2dvTd9mUw=&xsec_source=pc_search&source=web_explore_feed)（小红书笔记快照，公司/岗位/轮次为发帖人自述，未核实）
- 题目 15 条：入库 4 / 判重 1 / 拒绝 5 / 待后续 5。题目顺序为原帖顺序。

## 一面（15 题）

- **C070** 自我介绍 —— ❌ 拒绝（自我介绍/项目叙述/软素质/经历）
- **C071** 介绍你做过的 AI Agent 或相关 LLM 应用项目 —— ❌ 拒绝（自我介绍/项目叙述/软素质/经历）
- **C072** AI Agent 与普通 LLM Chat 的本质区别是什么，核心组件有哪些 —— ✅ 入库 Q001
- **C073** 讲一下 ReAct (Reasoning + Acting) 范式的工作流程，Thought→Action→Observation 如何循环 —— ✅ 入库 Q002
- **C074** 意图识别在 Agent 系统里怎么做——用 LLM Router，规则分类还是微调分类器，各有什么优势 —— ⏳ 留待后续批次
- **C075** LangChain 中 Chain、Agent、Tool、Memory 各自职责，LCEL 的基本链路是怎样的 —— ⏳ 留待后续批次
- **C076** RAG 的完整流程，Query 改写、Chunk 切分策略、Embedding、向量检索、Rerank、Context 注入，说说你优化过哪些点 —— ✅ 入库 Q017
- **C077** 向量数据库选型（FAISS / Milvus / Qdrant / Chroma），你们为什么选这个，召回率怎么评估 —— ⏳ 留待后续批次
- **C078** Agent 调工具时参数解析失败或 JSON 格式不对怎么处理，如何防止无限循环调用 —— ✅ 入库 Q015
- **C079** Redis 在你 Agent 系统里的用途，缓存、分布式锁、Session 存储、消息队列，各举一例 —— ⏳ 留待后续批次
- **C080** MySQL 事务 ACID 简单说一下，隔离级别有哪些 —— ❌ 拒绝（通用ML/后端八股）
- **C081** Python 中 GIL 是什么，对多线程和多进程的影响 —— ❌ 拒绝（通用ML/后端八股）
- **C082** 说一下你遇到过的 Agent 最大 Bad Case 及你怎么解决的 —— ↪️ 判重并入 Q023
- **C083** 你对 LangGraph 或 Agent Harness 有了解么，简单说下认知 —— ⏳ 留待后续批次
- **C084** 手撕算法 LeetCode 46——全排列（Permutations），给定一个不含重复数字的数组，返回所有可能的排列 —— ❌ 拒绝（纯算法手撕题）
