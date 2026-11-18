# 画面提取 · 某厂 Agent 一面面经（无标题帖）

> 来源：note 6ac86853000000001801b00e（无标题，正文自称「某厂Agent一面面经」；作者：努力学习LLM应用开发中，赞 37）
> 提取方式：远程视觉模型逐图转写（用户 2026-11-17 批准），保留原文编号与表述，未核对原文错别字。
> 正文原文与画面提取分开保存；以下为图片内容，按图片文件顺序。本帖共 2 张图片（正文称共 15 题，其中第 8 题跨 2 张图）。

## 来自 01.webp

某厂 Agent 面经

1、自我介绍

2、介绍你做过的 AI Agent 或相关 LLM 应用项目

3、AI Agent 与普通 LLM Chat 的本质区别是什么，核心组件有哪些

4、讲一下 ReAct (Reasoning + Acting) 范式的工作流程，Thought→Action→Observation 如何循环

5、意图识别在 Agent 系统里怎么做 —— 用 LLM Router，规则分类还是微调分类器，各有什么优势

6、LangChain 中 Chain、Agent、Tool、Memory 各自职责，LCEL 的基本链路是怎样的

7、RAG 的完整流程，Query 改写、Chunk 切分策略、Embedding、向量检索、Rerank、Context 注入，说说你优化过哪些点

8、向量数据库选型（FAISS / Milvus〔不清〕

## 来自 02.webp

8、向量数据库选型（FAISS / Milvus / Qdrant / Chroma），你们为什么选这个，召回率怎么评估
9、Agent 调工具时参数解析失败或 JSON 格式不对怎么处理，如何防止无限循环调用
10、Redis 在你 Agent 系统里的用途，缓存、分布式锁、Session 存储、消息队列，各举一例
11、MySQL 事务 ACID 简单说一下，隔离级别有哪些
12、Python 中 GIL 是什么，对多线程和多进程的影响
13、说一下你遇到过的 Agent 最大 Bad Case 及你怎么解决的
14、你对 LangGraph 或 Agent Harness 有了解么，简单说下认知
15、手撕算法 LeetCode 46—— 全排列（Permutations），给定一个不含重复数字的〔不清〕数组，返回所有可能的排列
