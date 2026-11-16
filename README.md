# 小红书面经 · AI/Agent 面试题库

从小红书面试经验帖提取真实被问到的 AI/Agent 方向面试题，编写并独立审核答案。参考抖音题库工作流的分层思路独立实现；题目 JSON 为唯一事实源，Markdown 均为生成物。

当前题库：**0 题**（首个关键词批次试运行后更新统计口径：可见笔记数 / 标题排除 / 内容复核 / 画面提取 / 裸题提取 / 去重弃 / 入库）。

## 工作流

关键词搜索采集 → 冻结清单 → 标题与内容筛选 → 正文/画面提取裸题 → 四维语义去重 → 答案编写（附实际查阅参考）→ 独立 Agent 审核（SHA-256 门禁）→ 单题入库 → 索引与文档同步。

- 采集与筛选：[harvest-xhs-interviews Skill](.agents/skills/harvest-xhs-interviews/SKILL.md)
- 编写与入库：[build-interview-bank Skill](.agents/skills/build-interview-bank/SKILL.md)
- 设计文档：[docs/2026-11-16-xhs-interview-bank-design.md](docs/2026-11-16-xhs-interview-bank-design.md)

## 命令

```sh
# 测试（仓库根目录）
PYTHONDONTWRITEBYTECODE=1 D:/MSYS2/ucrt64/bin/python3 -m unittest discover \
  -s .agents/skills/build-interview-bank/scripts -p 'test_*.py' -v
# 新题登记（须已通过独立审核）
D:/MSYS2/ucrt64/bin/python3 .agents/skills/build-interview-bank/scripts/manage_bank.py \
  question_bank --file agent-architecture/low/Q001.json
# 单题重新生成 / 全量只读审计 / 全量重建
… manage_bank.py question_bank --question Q001
… manage_bank.py question_bank --check
… manage_bank.py question_bank --all
```

## 边界

- 公司/岗位/轮次等面经元数据仅存教研侧，学员版不展示。
- 原始笔记快照与图片存批次目录作证据；不持久化 Cookie/令牌；不引入云端 OCR/ASR。
- 刷题网站为后续可选阶段，当前以 Markdown 索引阅读。
