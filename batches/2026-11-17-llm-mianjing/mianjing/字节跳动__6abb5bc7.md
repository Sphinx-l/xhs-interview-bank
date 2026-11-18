# 字节大模型LLM算法一面9.29

- 来源：[字节大模型LLM算法一面9.29](https://www.xiaohongshu.com/search_result/6abb5bc7000000001b02e684?xsec_token=ABWKRXWFIwDhjql6lxtQrfy3FyAr3WbuPfIjZiT7iuLnk=&xsec_source=)（小红书笔记快照，公司/岗位/轮次为发帖人自述，未核实）
- 公司：字节跳动（渠道：未标注，按帖内标记推断） ｜ 岗位：大模型算法 ｜ 轮次：一面
- 题目 13 条（题目顺序为原帖顺序）

- 1.推导 FlashAttention 的 online softmax 与反向重计算，说明其 HBM 访存复杂度和为何不改变数学结果。
- 2.证明 RoPE 点积仅依赖相对位置；解释 NTK-aware、YaRN 外推的频域缩放本质与失效场景。
- 3.比较 MHA/MQA/GQA 在 KV Cache、算术强度、并发吞吐上的差异，并给出分组数选择依据。
- 4.MoE 中 top-k 路由、负载均衡损失、专家容量与 token drop 如何共同影响训练稳定性？如何诊断路由坍缩？
- 5.推导 3D 并行下 TP、PP、DP、ZeRO 的通信量，并分析 PP bubble 与 micro-batch 的关系。
- 6.完整写出 PPO 在 RLHF 中的目标函数，解释 GAE、KL 惩罚、reward hacking 与 critic 偏差的相互作用。
- 7.从数学上讨论 DPO 与 PPO 的等价条件、偏好数据假设及 DPO 的常见失败模式。
- 8.解释 GPTQ 的 Hessian 近似与误差补偿、AWQ 的激活感知缩放、SmoothQuant 的数学变换及各自适用边界。
- 9.分析 speculative decoding 的接受率、加速比与 draft model 选择；tree attention 如何保证并行验证正确性？
- 10.比较 Ring Attention、序列并行、attention sink、位置插值在长上下文中的原理、代价与组合方式。
- 11.bf16 训练中 attention logits 溢出如何发生？softmax、LayerNorm/RMSNorm、初始化与残差缩放如何影响稳定性？
- 12.代码题：实现 GQA 推理的 KV Cache 更新与 attention 计算，要求支持 batch、变长序列和 past_key_values。
- 13.从 scaling law 出发，推导计算预算下模型参数量与训练 token 的最优配比，并讨论数据质量、重复训练的影响。
