# 题库目录

共 40 题。

| 题目 | 分类 | 难度 | TAG |
| --- | --- | --- | --- |
| [Q001 · AI Agent 与普通 LLM 对话应用的本质区别是什么？Agent 的核心组件有哪些？](agent-architecture/low/Q001.md) | AI Agent 架构设计 | 低 | `agent组成` `工具调用` `规划循环` `上下文管理` |
| [Q002 · ReAct 范式的工作流程是怎样的？工程实现中消息格式如何设计，tool_response 用什么角色传回？](agent-architecture/medium/Q002.md) | AI Agent 架构设计 | 中 | `ReAct` `消息格式` `工具调用` `Thought-Action-Observation` |
| [Q003 · ReAct 与 Plan-Execute 两种范式有什么区别？分别适合什么任务？为什么简单任务不该先做完整 Plan？](agent-architecture/medium/Q003.md) | AI Agent 架构设计 | 中 | `ReAct` `Plan-Execute` `任务规划` `范式选型` |
| [Q004 · Agent Loop 的核心流程怎么设计？什么时候停？怎么防死循环与重复调用？终止后如何校验结果？](agent-architecture/high/Q004.md) | AI Agent 架构设计 | 高 | `Agent Loop` `终止条件` `死循环检测` `结果校验` |
| [Q005 · Multi-Agent 与 Single-Agent 的本质区别是什么？多 Agent 的收益与代价如何权衡？什么时候应该退回单 Agent？](agent-architecture/high/Q005.md) | AI Agent 架构设计 | 高 | `Multi-Agent` `上下文隔离` `任务编排` `架构权衡` |
| [Q006 · Workflow 与 Agent 的本质区别是什么？什么场景应该选 Workflow（固定编排）而不是自主 Agent？](agent-architecture/medium/Q006.md) | AI Agent 架构设计 | 中 | `Workflow` `自主决策` `编排选型` `可预测性` |
| [Q007 · Agent 的记忆机制怎么分层设计？短期记忆、长期记忆和 Summary 各自存什么、何时读写？](agent-architecture/high/Q007.md) | AI Agent 架构设计 | 高 | `记忆分层` `短期记忆` `长期记忆` `摘要记忆` |
| [Q008 · Agent 的长期记忆应该如何设计？什么条件下写入、如何组织存储、如何召回与更新？用户偏好改变时怎么处理？](agent-architecture/high/Q008.md) | AI Agent 架构设计 | 高 | `长期记忆` `记忆写入` `记忆召回` `偏好更新` |
| [Q009 · 多轮对话超出模型上下文窗口时如何处理？滑动窗口和动态摘要各适合什么场景？压缩时应该保留哪些信息？](agent-architecture/medium/Q009.md) | AI Agent 架构设计 | 中 | `上下文压缩` `滑动窗口` `动态摘要` `长对话` |
| [Q010 · 上下文预算有限时，系统提示、工具 Schema、记忆、轨迹与中间结果如何做全局分配？如何量化压缩损失？](agent-architecture/high/Q010.md) | AI Agent 架构设计 | 高 | `上下文工程` `预算分配` `压缩损失` `上下文管理` |
| [Q011 · MCP（Model Context Protocol）的原理是什么？传输方式有哪些？它与 Function Calling 是什么关系、解决了什么问题？](agent-engineering/medium/Q011.md) | Agent 工程化与运行环境 | 中 | `MCP` `Function Calling` `协议设计` `工具生态` |
| [Q012 · Function Calling 的基本原理是什么？模型与程序分别负责什么？没有 MCP 之前大模型是怎么调工具的？](agent-engineering/low/Q012.md) | Agent 工程化与运行环境 | 低 | `Function Calling` `工具调用原理` `JSON Schema` `结构化输出` |
| [Q013 · 如何设计工具的描述与参数 Schema，才能提升大模型的调用准确率、减少瞎编参数？](agent-engineering/medium/Q013.md) | Agent 工程化与运行环境 | 中 | `工具Schema` `参数校验` `工具描述` `防呆设计` |
| [Q014 · 工具库有上百个工具（或几百个用户自定义 Skill）时，如何让模型快速准确地选中工具？召回率下降怎么解决？](agent-engineering/medium/Q014.md) | Agent 工程化与运行环境 | 中 | `工具检索` `两级加载` `Skill召回` `动态挂载` |
| [Q015 · 工具调用失败、超时、返回异常格式或部分成功时如何容错？重试怎么设计、如何保证幂等？高风险工具（如支付）如何兜底？](agent-engineering/high/Q015.md) | Agent 工程化与运行环境 | 高 | `工具容错` `重试幂等` `熔断降级` `结果验证` |
| [Q016 · 如何向不懂技术的人解释 RAG？什么是 Embedding，为什么文本要向量化？余弦相似度在 RAG 中起什么作用？](rag-retrieval/low/Q016.md) | RAG 检索与知识组织 | 低 | `RAG概念` `Embedding` `余弦相似度` `检索增强` |
| [Q017 · RAG 的完整流程是怎样的？从文档入库到线上检索，Query 改写、切分、召回、重排、注入各环节怎么做、优化过哪些点？](rag-retrieval/high/Q017.md) | RAG 检索与知识组织 | 高 | `RAG全链路` `Query改写` `召回重排` `上下文注入` |
| [Q018 · 为什么 RAG 检索要用 BM25 关键词 + 向量 Dense 的混合方案？只用向量不行吗？两路结果怎么合并？](rag-retrieval/medium/Q018.md) | RAG 检索与知识组织 | 中 | `混合检索` `BM25` `向量检索` `结果融合` |
| [Q019 · RRF 的全称和作用是什么？它与 Rerank 有什么区别？为什么 RAG 流程要引入父子索引？](rag-retrieval/medium/Q019.md) | RAG 检索与知识组织 | 中 | `RRF` `Rerank` `父子索引` `召回重排` |
| [Q020 · 文档为什么要切片？Chunk Size 和 Overlap 如何确定？为什么不能只用固定长度切分？递归/结构化切分好在哪里？](rag-retrieval/medium/Q020.md) | RAG 检索与知识组织 | 中 | `Chunk切分` `重叠窗口` `递归切分` `结构化切分` |
| [Q021 · Agent 系统的效果评测体系怎么设计？除了准确率还要看哪些指标？埋点怎么收集？人工标注还是线上指标？](evaluation-reliability/high/Q021.md) | Agent 评测与可靠性 | 高 | `Agent评测` `指标体系` `任务成功率` `线上指标` |
| [Q022 · Agent 的评测集怎么构建与分类？评测成本如何计算？没有用户反馈数据时怎么做抽检？](evaluation-reliability/medium/Q022.md) | Agent 评测与可靠性 | 中 | `评测集构建` `场景分层` `抽样抽检` `评测成本` |
| [Q023 · Bad case 怎么定位与归因？多 Agent 体系下如何定位是哪个环节的问题？修复后怎么验证没有影响其他 case？](evaluation-reliability/high/Q023.md) | Agent 评测与可靠性 | 高 | `Badcase闭环` `归因定位` `回归集` `修复验证` |
| [Q024 · 用 LLM 做裁判（LLM-as-judge）评估输出质量时有哪些系统性偏差？如何控制位置、长度、自增强等偏差与评测污染？](evaluation-reliability/medium/Q024.md) | Agent 评测与可靠性 | 中 | `LLM-as-judge` `位置偏差` `长度偏差` `评测校准` |
| [Q025 · Agent 的可观测性体系怎么设计？Trace/Span/决策日志如何支撑根因定位？海量日志怎么排查？](evaluation-reliability/high/Q025.md) | Agent 评测与可靠性 | 高 | `可观测性` `Trace` `决策日志` `根因定位` |
| [Q026 · Agent 长任务耗时从 5 分钟涨到 20 分钟，怎么排查延迟？不同业务场景下延迟和效果怎么取舍？](agent-performance/medium/Q026.md) | Agent 性能优化 | 中 | `延迟排查` `延迟效果取舍` `性能归因` `长任务` |
| [Q027 · 工程侧的推理加速有哪些方向？Continuous Batching 和 KV Cache 是什么？vLLM 这类框架为什么能大幅提升吞吐？](agent-performance/medium/Q027.md) | Agent 性能优化 | 中 | `推理加速` `KV Cache` `Continuous Batching` `vLLM` |
| [Q028 · Agent 的流式响应怎么实现？为什么用 SSE？流式输出下工具调用事件怎么推给前端？断线后如何恢复之前的输出？](agent-performance/high/Q028.md) | Agent 性能优化 | 高 | `SSE流式` `事件推送` `断线恢复` `工具调用事件` |
| [Q029 · 用户中途取消任务、或版本热更新时正在运行的 Agent 怎么处理？](agent-performance/medium/Q029.md) | Agent 性能优化 | 中 | `任务取消` `热更新` `检查点` `优雅终止` |
| [Q030 · 为控制延迟和成本，Agent 调用大模型有哪些优化策略？缓存、压缩、模型路由各自怎么做？代价与效果如何权衡？](agent-cost/medium/Q030.md) | Agent 成本优化 | 中 | `成本优化` `模型路由` `Prompt缓存` `成本效果权衡` |
| [Q031 · Prompt 已经调到极限了，下一步怎么办？换模型、升参数还是做 SFT？怎么决策？人工调 Prompt 和自动化调优怎么选？](model-adaptation/high/Q031.md) | 模型选型与微调 | 高 | `Prompt天花板` `SFT决策` `模型升级` `自动化调优` |
| [Q032 · 为什么有些场景下 SFT 效果不好？SFT 的失败模式有哪些、什么问题根本不该用 SFT 解决？](model-adaptation/medium/Q032.md) | 模型选型与微调 | 中 | `SFT失效场景` `数据质量` `知识注入` `泛化边界` |
| [Q033 · Agentic 模型的 CPT、SFT、RL 三阶段训练流程分别是什么？为什么 SFT 时要 mask 掉 observation tokens？](model-adaptation/high/Q033.md) | 模型选型与微调 | 高 | `Agentic训练` `三阶段流程` `observation mask` `损失掩码` |
| [Q034 · 多模态大模型的具体结构是什么样的？视觉编码器和语言模型如何衔接？](model-adaptation/medium/Q034.md) | 模型选型与微调 | 中 | `多模态架构` `视觉编码器` `模态衔接` `投影层` |
| [Q035 · Reward Model 适合解决什么问题？在 Agent 系统中如何使用？](agent-learning/medium/Q035.md) | Agent 学习与策略优化 | 中 | `Reward Model` `RLHF` `偏好学习` `任务奖励` |
| [Q036 · RAG 知识库更新有哪些难点？文档局部修改时如何做增量更新？多存储间（如 MySQL 与 ES）的数据一致性怎么保证？](data-governance/medium/Q036.md) | Agent 数据治理 | 中 | `知识库更新` `增量更新` `数据一致性` `版本管理` |
| [Q037 · Prompt 注入、工具越权、数据外泄如何在架构层做纵深防御？权限最小化、沙箱与审计如何协同？](agent-architecture/high/Q037.md) | AI Agent 架构设计 | 高 | `Prompt注入` `纵深防御` `权限最小化` `沙箱审计` |
| [Q038 · Agent 的模型幻觉怎么处理？RAG 出现过幻觉吗？幻觉在多 Agent 之间传播怎么防？](evaluation-reliability/medium/Q038.md) | Agent 评测与可靠性 | 中 | `幻觉缓解` `RAG忠实度` `跨Agent传播` `溯源` |
| [Q039 · 场景设计：用 Agent 实现一个 AI 面试程序，你会怎么设计？它有什么缺点？需要保证哪些核心指标？怎么避免每步重新规划导致路径震荡？](agent-architecture/high/Q039.md) | AI Agent 架构设计 | 高 | `场景设计` `AI面试` `面试官Agent` `路径震荡` |
| [Q040 · Coding Agent 从用户提出需求到编码、测试的完整流程怎么设计？需求澄清、Spec/技术设计/任务拆解怎么区分？各阶段产物如何客观比较与确认？](agent-engineering/high/Q040.md) | Agent 工程化与运行环境 | 高 | `Coding Agent` `需求澄清` `Spec设计` `产物评审` |
