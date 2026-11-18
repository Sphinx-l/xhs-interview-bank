# 小红书面经 · AI/Agent 真题采集

从小红书/牛客/掘金采集真实被问到的 AI/Agent 方向面试题。**主产物按公司/岗位/轮次组织的完整面经**（保留原帖题目顺序与完整性），当前阶段只采集问题，不编写答案（2026-11-18 确认的方向）。

## 面经入口（按公司）

- 批次一 [2026-11-17-agent-mianjing](batches/2026-11-17-agent-mianjing/README.md)（小红书）：23 篇面经 → [公司索引](batches/2026-11-17-agent-mianjing/mianjing/README.md)
- 批次二 [2026-11-17-llm-mianjing](batches/2026-11-17-llm-mianjing/README.md)（小红书）：974 张卡片 / 617 篇复核 / **160 篇题源**（正文题面 76 + 图片题面 84 待画面提取）/ 928 条裸题 → [公司索引](batches/2026-11-17-llm-mianjing/mianjing/README.md)（28 家公司 66 篇已出，图片型与待补采陆续补齐）
- 批次三 [2026-11-18-niuke-agent-mianjing](batches/2026-11-18-niuke-agent-mianjing/README.md)（牛客）：68 张卡片 / 57 篇复核 / **48 篇题源** / 1599 行题目 → [公司索引](batches/2026-11-18-niuke-agent-mianjing/mianjing/README.md)（30 家公司）
- 批次四 [2026-11-18-niuke-shezhao](batches/2026-11-18-niuke-shezhao/README.md)（牛客·定向社招）：**10 篇社招题源** / 338 行题目 → [公司索引](batches/2026-11-18-niuke-shezhao/mianjing/README.md)（蚂蚁/抖音/淘天/快手/深信服/懂车帝等 10 家）

> 2026-11-18 起渠道维度（社招/校招/实习）为必录字段，**采集优先级：社招 > 校招 > 实习**。

## 工作流

**采集（进行中）**：关键词搜索采集 → 冻结清单 → 标题与内容筛选（仅 Agent/大模型开发技术方向）→ 正文/画面提取题目 → 按公司/岗位/轮次整理完整面经（mianjing/）。

- 采集与筛选（小红书）：[harvest-xhs-interviews Skill](.agents/skills/harvest-xhs-interviews/SKILL.md)
- 采集与筛选（牛客）：[harvest-niuke-interviews Skill](.agents/skills/harvest-niuke-interviews/SKILL.md)
- 采集与筛选（掘金）：[harvest-juejin-interviews Skill](.agents/skills/harvest-juejin-interviews/SKILL.md)

**编题入库（暂停，答案阶段恢复时启用）**：四维语义去重（重复题面以 sighting 登记出现轨迹 occurrences）→ 答案编写（附实际查阅参考）→ 独立 Agent 审核（SHA-256 门禁）→ 单题入库 → 索引与文档同步。工具：[build-interview-bank Skill](.agents/skills/build-interview-bank/SKILL.md)；设计文档：[docs/2026-11-16-xhs-interview-bank-design.md](docs/2026-11-16-xhs-interview-bank-design.md)（第 11 节：面经情报层）。

## 遗留：考点/难度题库（暂停维护）

早期按 9 类目 × 三档难度建过 40 题题库（含独立审核答案与 1.1 情报层的 occurrences 出现轨迹），入口 [question_bank/README.md](question_bank/README.md)，教研侧另有按公司视图 [question_bank/editorial/by-company.md](question_bank/editorial/by-company.md)。按新方向不再按考点/难度扩充；40 题答案后续迁移到对应公司面经下，迁移时间待定。

## 命令（暂停的题库工具，题库存档/审计仍可用）

环境要求：任意 **Python ≥ 3.9**（仅标准库，无需安装第三方依赖）。命令示例统一写 `python`：Windows 命令行若 `python` 不可用可改用官方启动器 `py`，macOS/Linux 用 `python3`。

```sh
# 测试（仓库根目录；PYTHONDONTWRITEBYTECODE=1 前缀可选，用于不产生 __pycache__）
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover \
  -s .agents/skills/build-interview-bank/scripts -p 'test_*.py' -v
# 新题登记（须已通过独立审核）
python .agents/skills/build-interview-bank/scripts/manage_bank.py \
  question_bank --file agent-architecture/low/Q001.json
# 重复题面登记出现（教研侧 occurrences，脚本校验并重绑审核哈希）
… manage_bank.py question_bank --sighting Q001 --batch 2026-11-20-agent-mianjing \
  --note <note_id> --company 字节 --role "Agent 开发" --round 一面
# 单题重新生成 / 全量只读审计 / 全量重建
… manage_bank.py question_bank --question Q001
… manage_bank.py question_bank --check
… manage_bank.py question_bank --all
```

## 边界

- 公司/岗位/轮次一律为发帖人自述、未核实；发帖人身份仅存采集侧记录。
- 原始笔记快照与图片存批次目录作证据；不持久化 Cookie/令牌；不引入云端 OCR/ASR。
- 仅采集 Agent/大模型开发技术方向面经，AI 产品经理/运营等非技术岗不采（2026-11-18 规则）。
- 刷题网站为后续可选阶段，当前以 Markdown 索引阅读。
