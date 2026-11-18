# 画面提取 · 6a677c95000000001302f0fb

（淘天 AI Agent 一面；16 题全部带发帖人自答；图片带「AI起点/AI超点/AI creating」等水印，疑似 AI 辅助生成/课程营销向内容，真实性自述降权处理）

> 来自 01.webp（题目总览，无自答）

1. 多阶段RAG，BM25 加向量混合检索——两种结果怎么合并的？实际提升在哪？
2. PDF 扫描件、OCR、表格结构化这些，踩过坑没？
3. 识别准确率能做到多少？
4. State 和 Checkpoint 怎么搞的？多个 agent 一块跑，状态不会互相覆盖吗？
5. State 全局管理怎么做的？
6. Choice 接口包成 MCP 工具，标准接口怎么设计？兼容性有问题吗？
7. 现场举一个你项目里的 MCP 工具例子，入参出参怎么定义的
8. 没有 MCP 之前，大模型调工具是怎么个流程？
9. MCP 有什么坑或者短板？
10. MCP 返回结果能不能流式？
11. 你项目是多 Agent 主子架构吗？
12. 一次会话 token 大概多少？有没有爆过上下文窗口？
13. 用的什么模型？Qwen 是吧，哪个版本？
14. 子任务挂了，比如数据抓回来空的，工作流怎么重试或降级？
15. FastAPI 加 SSE 做流式，LangGraph 图状态机里怎么抓到每个节点的结果实时推前端？
16. 为什么选 LangGraph 不直接用 LangChain？

> 来自 02.webp（题 1–3 自答）

一、用 RRF（倒数排名融合）把两路结果按排名加权合并，不是直接加分数。两路各自排 Top N，每篇文档的 RRF 分数是 1/(排名+k)，k 取 60，两路分数加和排序。BM25 抓关键词（错误码、API 名），向量抓语义（同义词、换说法），互补。提升：召回率比单路高 10%-15%，口语化提问尤其明显；上下文更全，幻觉减少。

二、扫描件质量和表格结构是两个大坑。扫描件：模糊、倾斜、阴影、水印，OCR 识别率直接腰斩；中英文混排容易被拆成单字母或阅读顺序搞反；双栏排版按行读会串行。表格：合并单元格最头疼，解析工具常把一个合并格拆成多个空格；嵌套表格 Unstructured 和 Camelot 都处理不好；无边框表格根本识别不出是表格。

三、看文档质量。清晰印刷体 PDF 的 OCR 准确率 95%-99%；扫描件 80%-95%，模糊歪斜能掉到 70% 以下；手写体 70%-85%。表格结构还原：简单表格 90%+，带合并单元格的复杂表格可能只有 70%-80%。实际项目里做后处理：正则校验关键字段格式，置信度低的片段标出供人工复核。

> 来自 03.webp（题 4–5 自答）

四、LangGraph 基于 Pregel BSP 模型，同一 super-step 内可并行跑多个节点，不互相覆盖是因为所有节点读同一份 state 快照，更新先缓存，super-step 结束时靠 reducer 合并写入。Checkpoint 用 SqliteSaver 或 PostgresSaver 持久化，每个 super-step 后自动存快照，出错回滚到上一个检查点。节点不直接原地改 state，只返回增量更新，字段 reducer 控制合并策略。不同 thread_id 之间 state 天然隔离。

五、定义一个 TypedDict 作为全局 state schema，所有节点共享，各自写自己负责的字段。每个节点函数接收完整 state，返回一个 dict 作为增量更新，框架自动合并。多 Agent 场景下通过 key 前缀或命名空间隔离各自字段（如搜索 Agent 只写 search_results）。节点之间通过 state 传数据而不是函数参数，图的结构才清晰。

> 来自 04.webp（题 6–7 自答）

六、MCP 工具定义三要素：name、description、inputSchema。兼容性问题的关键是不同厂商 function call 格式不一致（OpenAI 用 tools 数组加 tool_choice，Anthropic 用 tool_use 块）。包成 MCP 之后，服务端只暴露 tools/list 和 tools/call 接口，客户端负责把 MCP 工具描述翻译成各模型原生格式，换模型不需要改服务端代码。坑：某些模型对 JSON Schema 嵌套对象支持不好，需要把复杂参数拍平成一维。

七、以「订单查询」工具为例。入参：order_id（字符串，必填）、fields（字符串数组，可选）。出参：统一 JSON 对象（order_status、amount、created_at、items 列表）。inputSchema 用 JSON Schema 定义 properties 与 required。

> 来自 05.webp（题 8–10 自答）

八、MCP 之前：模型输出 function call JSON → 业务代码解析 → 调函数 → 结果拼回 prompt → 再调模型。痛点：每家厂商格式不一样，换模型解析逻辑全要改。MCP 把工具定义和调用协议跟模型解耦。

九、MCP 的坑：部署复杂（每个 server 独立进程）、传输受限（stdio 只能本地，SSE 单向推送）、认证不统一、流式弱、Token 消耗大（tools/list 全量工具描述每次都带）。

十、基础 stdio 下工具结果需完整返回；新版 Streamable HTTP 可推送进度通知，但工具最终返回的 content 仍是完整 JSON，不像大模型逐 token 流式。进度事件流和业务结果流式是两回事。

> 来自 06.webp（题 11–13 自答）

十一、是，主管分派模式：Supervisor 管调度（拆解任务/分派/检查/打回重做），下设搜索 Agent（RAG 检索+联网）、代码 Agent（写代码/沙箱/调试）、分析 Agent（数据分析/报告）。约束同级 Agent 不直接通信，所有交互经 Supervisor 中转，方便管控和审计。

十二、常规对话 15K-30K token，多轮工具调用 40K-50K。Qwen2.5-72B 窗口 128K 没爆过。预防：超过 30 轮对话做摘要压缩，RAG 检索结果重排只留 Top 3。

十三、Qwen2.5-72B-Instruct，阿里云 API 调用。选型理由：同规模推理能力好、中文与工具调用表现好、成本效果平衡、128K 长上下文。

> 来自 07.webp（题 14–15 自答）

十四、LangGraph 条件边实现失败路由，重试靠循环边（指数退避，最多 3 次），降级靠 fallback 节点。降级三档：缓存 → 默认值/兜底回复 → 关键任务转人工审核队列并告警。流程编排在图里，不是散落的 if-else。

十五、用 astream_events 捕获节点事件（on_chain_start/end、on_tool_start/end），FastAPI 端经 asyncio 队列转 SSE 推前端，展示「正在检索知识库」等进度。需过滤中间结果噪音。

> 来自 08.webp（题 16 自答，末图）

十六、LangChain 是线性链，Agent 工作流是循环图。LangChain：Chain 链式 A→B→C 定死、条件分支费劲、链间手动传参、无检查点；LangGraph：有向图支持循环分支、条件边路由、内置共享 state、每步自动存快照支持回滚重放。Agent 实际工作流是环形的——调工具、看结果、不够继续调、够了才输出。

（说明：16 题带完整自答，主题：混合检索 RRF/OCR 表格坑/LangGraph State-Checkpoint-Pregel/MCP 设计与短板/主子多 Agent/token 预算/重试降级/SSE 流式/LangGraph vs LangChain。自答技术细节具体（RRF k=60、Qwen2.5-72B、astream_events），但图片多处营销水印 + 排版高度模板化，单场面试真实性存疑，编题时按「疑似营销/教学整理」降权，优先采信题目本身而非自答。）
