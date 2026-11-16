# 小红书面经 · AI/Agent 面试题库

从小红书面试经验帖提取真实被问到的 AI/Agent 方向面试题，编写并独立审核答案。参考抖音题库工作流的分层思路独立实现；题目 JSON 为唯一事实源，Markdown 均为生成物。

当前题库：**0 题**（首个关键词批次试运行后更新统计口径：可见笔记数 / 标题排除 / 内容复核 / 画面提取 / 裸题提取 / 去重弃 / 入库）。

## 工作流

关键词搜索采集 → 冻结清单 → 标题与内容筛选 → 正文/画面提取裸题 → 四维语义去重（重复题面以 sighting 登记出现轨迹）→ 答案编写（附实际查阅参考）→ 独立 Agent 审核（SHA-256 门禁）→ 单题入库 → 索引与文档同步。

- 采集与筛选：[harvest-xhs-interviews Skill](.agents/skills/harvest-xhs-interviews/SKILL.md)
- 编写与入库：[build-interview-bank Skill](.agents/skills/build-interview-bank/SKILL.md)
- 设计文档：[docs/2026-11-16-xhs-interview-bank-design.md](docs/2026-11-16-xhs-interview-bank-design.md)（第 11 节：面经情报层）

## 命令

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

- 公司/岗位/轮次等面经元数据仅存教研侧，学员版不展示；出现轨迹（occurrences）与公司索引（`question_bank/editorial/by-company.md`）同为教研侧，学员版不渲染、审计拦截泄漏。
- 原始笔记快照与图片存批次目录作证据；不持久化 Cookie/令牌；不引入云端 OCR/ASR。
- 刷题网站为后续可选阶段，当前以 Markdown 索引阅读。
