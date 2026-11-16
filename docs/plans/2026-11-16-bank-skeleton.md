# 小红书面经题库工作流 · 骨架实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `D:\yuege\xhs-interview-bank` 搭建内容工作流骨架：两个 Skill 文档、题库 1.0 契约、`manage_bank.py` 登记/校验/生成脚本与单元测试，空题库下全链路命令可用。

**Architecture:** 单一 Python 脚本（stdlib only）承担校验、Markdown 生成、审核哈希门禁、目录索引与 CLI；题目 JSON 是唯一事实源，`.md` 与索引全部为派生物；两个 Skill 文档定义采集与编题流程，通过批次目录中的 `manifest.json` / `candidates.json` / `reviews/` 衔接。

**Tech Stack:** Python 3.10（`D:/MSYS2/ucrt64/bin/python3`），标准库 only；unittest；JSON（UTF-8，`ensure_ascii=False`）。

## Global Constraints

- 设计依据：`docs/2026-11-16-xhs-interview-bank-design.md`，字段与规则以其为准。
- 参考仓库 `D:\yuege\douyin-data-analyze` 只读，禁止改动、复制其题库数据与审核记录。
- Python 解释器：`D:/MSYS2/ucrt64/bin/python3`（3.10.9）；不引入任何第三方依赖。
- 测试命令（仓库根目录）：`PYTHONDONTWRITEBYTECODE=1 D:/MSYS2/ucrt64/bin/python3 -m unittest discover -s .agents/skills/build-interview-bank/scripts -p 'test_*.py' -v`
- 目录名全部英文；难度目录固定 `low/medium/high`。
- 学员版内容不得出现公司/岗位/轮次、发帖人、原帖、教研等溯源信息。
- 每题必须有 `passed` 且 SHA-256 与文件字节一致的独立审核记录才能登记入库。
- JSON 统一 UTF-8 无 BOM，写文件用 `json.dumps(..., ensure_ascii=False, indent=2) + "\n"`。
- Git 提交信息以 `feat:`/`docs:`/`test:` 开头，结尾加 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`。

## 文件总览

| 文件 | 职责 |
| --- | --- |
| `question_bank/taxonomy.json` | 9 个分类定义（英文 ID + 中文名 + 范围） |
| `question_bank/catalog.json` | 轻量题目索引（元数据 only，无正文） |
| `.agents/skills/build-interview-bank/scripts/manage_bank.py` | 校验、生成、审核门禁、索引、CLI |
| `.agents/skills/build-interview-bank/scripts/test_manage_bank.py` | 单元测试 |
| `.agents/skills/harvest-xhs-interviews/SKILL.md` + `references/acquisition.md` | 小红书采集与筛选规范 |
| `.agents/skills/build-interview-bank/SKILL.md` + `references/*.md` | 编题契约、准入与审核规范 |
| `README.md` | 仓库入口：用法、命令、统计口径 |
| `.gitignore` | 缓存、字节码、虚拟环境 |

任务产出接口约定（跨任务引用）：`manage_bank.py` 导出 `REPO_ROOT`、`load_taxonomy(path)`、`validate_question(question, taxonomy) -> list[str]`、`generate_student_markdown(question, taxonomy) -> str`、`generate_editorial_markdown(question, taxonomy) -> str`、`register_question(repo_root, rel_path) -> list[str]`（空列表即成功）、`run_check(repo_root) -> list[str]`、`main(argv=None) -> int`。

---

### Task 1: 题库数据模型与 taxonomy/catalog

**Files:**
- Create: `question_bank/taxonomy.json`
- Create: `question_bank/catalog.json`
- Create: `.gitignore`
- Create: `.agents/skills/build-interview-bank/scripts/manage_bank.py`（本任务只写常量与加载函数）
- Test: `.agents/skills/build-interview-bank/scripts/test_manage_bank.py`

**Interfaces:**
- Produces: `manage_bank.REPO_ROOT: Path`、`read_json(path)`、`write_json(path, value)`、`load_taxonomy(path) -> dict[str, dict]`（键为分类 ID，值为分类对象）；taxonomy 文件本身。

- [ ] **Step 1: 写失败测试**

```python
# test_manage_bank.py
"""manage_bank 单元测试。运行：
PYTHONDONTWRITEBYTECODE=1 D:/MSYS2/ucrt64/bin/python3 -m unittest discover \
  -s .agents/skills/build-interview-bank/scripts -p 'test_*.py' -v
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import manage_bank as mb


class TaxonomyTests(unittest.TestCase):
    def test_load_real_taxonomy_has_nine_categories(self):
        taxonomy = mb.load_taxonomy(mb.REPO_ROOT / "question_bank" / "taxonomy.json")
        self.assertEqual(len(taxonomy), 9)
        self.assertIn("agent-architecture", taxonomy)
        self.assertEqual(taxonomy["rag-retrieval"]["name"], "RAG 检索与知识组织")

    def test_load_taxonomy_rejects_missing_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "taxonomy.json"
            path.write_text(json.dumps({"version": "1.0", "categories": [
                {"id": "cat", "name": "分类", "scope": ""},
            ]}, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                mb.load_taxonomy(path)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行确认失败**

Run: `PYTHONDONTWRITEBYTECODE=1 D:/MSYS2/ucrt64/bin/python3 -m unittest discover -s .agents/skills/build-interview-bank/scripts -p 'test_*.py' -v`
Expected: FAIL/ERROR（`No module named 'manage_bank'` 或文件缺失）

- [ ] **Step 3: 写 taxonomy.json 与 manage_bank.py 骨架**

`question_bank/taxonomy.json`（完整内容）：

```json
{
  "version": "1.0",
  "categories": [
    {"id": "agent-architecture", "name": "AI Agent 架构设计", "scope": "Agent 定义与组成、规划与循环、工具调用、多 Agent 协作、上下文与记忆"},
    {"id": "agent-performance", "name": "Agent 性能优化", "scope": "延迟定位、并行与流式、缓存、瓶颈排查与优化顺序"},
    {"id": "agent-cost", "name": "Agent 成本优化", "scope": "模型路由、Token 成本、质量/速度/成本取舍"},
    {"id": "rag-retrieval", "name": "RAG 检索与知识组织", "scope": "召回与重排、混合检索、分块策略、检索评测"},
    {"id": "evaluation-reliability", "name": "Agent 评测与可靠性", "scope": "评测集设计、指标、回归、失败模式与防护、人工审批"},
    {"id": "model-adaptation", "name": "模型选型与微调", "scope": "RAG 与微调选择、LoRA/QLoRA、数据准备、模型能力边界"},
    {"id": "data-governance", "name": "Agent 数据治理", "scope": "会话数据沉淀、知识库质量、数据清洗与权限"},
    {"id": "agent-engineering", "name": "Agent 工程化与运行环境", "scope": "环境管理、部署、MCP 与工具接入、可观测性"},
    {"id": "agent-learning", "name": "Agent 学习与策略优化", "scope": "强化学习基础、奖励设计、PPO 等策略优化方法"}
  ]
}
```

`question_bank/catalog.json`：

```json
{
  "version": "1.0",
  "generated_at": null,
  "questions": []
}
```

`.gitignore`：

```text
__pycache__/
*.pyc
.cache/
.venv/
```

`manage_bank.py` 骨架（完整）：

```python
"""小红书面经题库：登记、校验与生成脚本（契约 1.0）。仅标准库。

用法（仓库根目录）：
  python3 .../manage_bank.py question_bank --file <相对question_bank的JSON路径>
  python3 .../manage_bank.py question_bank --question Q001
  python3 .../manage_bank.py question_bank --check
  python3 .../manage_bank.py question_bank --all
"""

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

SKILL_DIR = Path(__file__).resolve().parent
REPO_ROOT = SKILL_DIR.parents[3]

CONTRACT_VERSION = "1.0"
DIFFICULTIES = ("low", "medium", "high")
DIFFICULTY_ZH = {"low": "低", "medium": "中", "high": "高"}
GENERIC_TAGS = {"ai", "面试", "高级", "人工智能", "大模型", "agent", "llm"}
GUIDE_KEYS = ("background", "pain_point", "focus", "approach")
EXTRACTIONS = ("note_text", "image_reading")
EDITORIAL_LEAK_MARKERS = ("发帖人", "博主", "原帖", "原视频", "教研", "来源：小红书")
ID_RE = re.compile(r"^Q\d{3}$")
BATCH_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_taxonomy(path):
    """读取并做最小结构校验，返回 {分类ID: 分类对象}。"""
    data = read_json(path)
    if data.get("version") != CONTRACT_VERSION:
        raise ValueError("taxonomy 必须为 1.0 版")
    categories = {}
    for category in data.get("categories", []):
        for key in ("id", "name", "scope"):
            if not isinstance(category.get(key), str) or not category[key].strip():
                raise ValueError(f"分类缺少有效字段 {key}：{category}")
        if category["id"] in categories:
            raise ValueError(f"分类 ID 重复：{category['id']}")
        categories[category["id"]] = category
    if not categories:
        raise ValueError("taxonomy 没有分类")
    return categories
```

- [ ] **Step 4: 运行测试确认通过**

Run: 同 Step 2 命令。Expected: 2 tests PASS

- [ ] **Step 5: 提交**

```bash
cd /d/yuege/xhs-interview-bank
git add question_bank/taxonomy.json question_bank/catalog.json .gitignore \
  .agents/skills/build-interview-bank/scripts/manage_bank.py \
  .agents/skills/build-interview-bank/scripts/test_manage_bank.py
git commit -m "feat: 题库 1.0 数据模型与 taxonomy/catalog

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: 单题结构校验 validate_question

**Files:**
- Modify: `.agents/skills/build-interview-bank/scripts/manage_bank.py`
- Test: `.agents/skills/build-interview-bank/scripts/test_manage_bank.py`

**Interfaces:**
- Consumes: `load_taxonomy`（Task 1）
- Produces: `validate_question(question, taxonomy) -> list[str]`（空列表=合法）；`canonical_rel(question) -> str`（如 `agent-architecture/low/Q001.json`）；测试基件 `BASE`（后续任务复用）。

契约要点（错误消息逐条实现）：ID `Q\d{3}`；`version=="1.0"`；`answer_type=="technical"`（v1.0 不支持其他）；分类在 taxonomy；difficulty ∈ low/medium/high；title 非空；tags 3–5 个、非空、不重复（忽略大小写）、不含泛词表；`question_guide` 四键非空；`recommended_answer.summary` 非空且 `points` 1–6 条非空；`technical_answer` **不得有 summary 键**，`sections` ≥1（heading/body 非空），可选 `example`（scenario/observation 非空，steps 为非空字符串列表）；`source.source_type=="xhs_note"`、note_id/question_verbatim 非空、extraction ∈ {note_text, image_reading}、batch_id 匹配 `BATCH_ID_RE`；`editorial_provenance` 含 company/role/round（可为 `"unspecified"`）、frequency 为 ≥1 整数；`technical_references` ≥1 条（title 非空、url 以 http 开头）；`related_questions` ≤4、不含自身、不重复。

- [ ] **Step 1: 写失败测试（追加到 test_manage_bank.py）**

```python
def base_question(**overrides):
    question = copy.deepcopy(BASE)
    question.update(overrides)
    return question


BASE = {
    "id": "Q001",
    "version": "1.0",
    "answer_type": "technical",
    "category_id": "agent-architecture",
    "difficulty": "low",
    "title": "什么是 Agent？它和大模型的关系是什么？",
    "tags": ["agent-definition", "tool-calling", "planning-loop"],
    "question_guide": {
        "background": "面试常从概念入手考察理解深度。",
        "pain_point": "容易把 Agent 和大模型本身混为一谈。",
        "focus": "Agent 的组成与自主循环，和大模型能力边界的区别。",
        "approach": "先给定义，再讲组成，最后对比边界。"
    },
    "recommended_answer": {
        "summary": "Agent 是以大模型为决策核心、能规划并调用工具完成多步任务的系统。",
        "points": [
            "大模型提供理解、推理与生成能力，是被调用的决策核心。",
            "Agent 在其外增加规划循环、工具调用、记忆与环境交互。",
            "判断边界：单轮问答用大模型即可，多步自主任务才需要 Agent。"
        ]
    },
    "technical_answer": {
        "sections": [
            {"heading": "组成", "body": "典型 Agent 由规划、工具、记忆、执行四部分组成。"}
        ]
    },
    "source": {
        "source_type": "xhs_note",
        "note_id": "65f0a1b200000000008d3a7b",
        "question_verbatim": "面试问：说说你对 Agent 的理解，它和 LLM 啥区别",
        "extraction": "note_text",
        "batch_id": "2026-11-16-test-batch"
    },
    "editorial_provenance": {
        "company": "某公司",
        "role": "Agent 开发工程师",
        "round": "一面",
        "frequency": 2,
        "notes": "两个面经帖出现同一题面"
    },
    "technical_references": [
        {"title": "Building effective agents", "url": "https://www.anthropic.com/research/building-effective-agents"}
    ],
    "related_questions": []
}


class ValidateQuestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.taxonomy = mb.load_taxonomy(
            mb.REPO_ROOT / "question_bank" / "taxonomy.json")

    def test_base_question_is_valid(self):
        self.assertEqual(mb.validate_question(BASE, self.taxonomy), [])

    def assert_field_error(self, overrides, fragment):
        errors = mb.validate_question(base_question(**overrides), self.taxonomy)
        self.assertTrue(any(fragment in e for e in errors),
                        f"期望错误包含 {fragment!r}，实际 {errors}")

    def test_rejects_bad_id_and_version(self):
        self.assert_field_error({"id": "Q1"}, "ID")
        self.assert_field_error({"version": "0.9"}, "version")

    def test_rejects_unsupported_answer_type(self):
        self.assert_field_error({"answer_type": "case_study"}, "technical")

    def test_rejects_unknown_category_and_difficulty(self):
        self.assert_field_error({"category_id": "no-such-cat"}, "分类")
        self.assert_field_error({"difficulty": "mid"}, "难度")

    def test_rejects_bad_tags(self):
        self.assert_field_error({"tags": ["a", "b"]}, "TAG 数量")
        self.assert_field_error(
            {"tags": ["ai", "tool-calling", "planning-loop"]}, "泛词")
        self.assert_field_error(
            {"tags": ["Tool-Calling", "tool-calling", "planning-loop"]}, "重复")

    def test_rejects_summary_in_technical_answer(self):
        bad = base_question()
        bad["technical_answer"]["summary"] = "不该存在"
        self.assert_field_error(bad, "summary")

    def test_rejects_bad_recommended_answer(self):
        bad = base_question()
        bad["recommended_answer"]["points"] = []
        self.assert_field_error(bad, "points")
        bad = base_question()
        bad["recommended_answer"]["summary"] = " "
        self.assert_field_error(bad, "summary")

    def test_rejects_bad_source(self):
        bad = base_question()
        bad["source"]["source_type"] = "douyin_video"
        self.assert_field_error(bad, "source_type")
        bad = base_question()
        bad["source"]["extraction"] = "ocr"
        self.assert_field_error(bad, "extraction")
        bad = base_question()
        bad["source"]["batch_id"] = "test-batch"
        self.assert_field_error(bad, "batch_id")

    def test_rejects_missing_editorial_fields(self):
        bad = base_question()
        del bad["editorial_provenance"]["company"]
        self.assert_field_error(bad, "company")

    def test_rejects_bad_references(self):
        self.assert_field_error({"technical_references": []}, "technical_references")
        bad = base_question()
        bad["technical_references"][0]["url"] = "ftp://x"
        self.assert_field_error(bad, "url")

    def test_rejects_bad_related_questions(self):
        self.assert_field_error({"related_questions": ["Q001"]}, "自身")
        self.assert_field_error(
            {"related_questions": ["Q002", "Q002", "Q003", "Q004", "Q005"]}, "related")

    def test_canonical_rel(self):
        self.assertEqual(mb.canonical_rel(BASE),
                         "agent-architecture/low/Q001.json")
```

注意：`test_rejects_bad_related_questions` 中 5 条含重复，会同时触发数量与重复错误，断言用 `in` 匹配即可。

- [ ] **Step 2: 运行确认失败**

Run: 全量 unittest 命令。Expected: 新增用例 FAIL（`validate_question` 不存在）

- [ ] **Step 3: 实现 validate_question 与 canonical_rel（追加到 manage_bank.py）**

```python
def canonical_rel(question):
    return f"{question['category_id']}/{question['difficulty']}/{question['id']}.json"


def _nonempty_str(value):
    return isinstance(value, str) and value.strip()


def validate_question(question, taxonomy):
    """返回错误消息列表；空列表表示通过结构校验。"""
    errors = []

    def err(message):
        errors.append(f"[{question.get('id', '?')}] {message}")

    if not ID_RE.match(question.get("id", "")):
        err("ID 必须为 Q 加三位数字，如 Q001")
    if question.get("version") != CONTRACT_VERSION:
        err(f"version 必须为 {CONTRACT_VERSION}")
    if question.get("answer_type") != "technical":
        err("v1.0 契约仅支持 answer_type=technical")
    if question.get("category_id") not in taxonomy:
        err(f"分类未在 taxonomy 注册：{question.get('category_id')}")
    if question.get("difficulty") not in DIFFICULTIES:
        err(f"难度必须为 low/medium/high，实际 {question.get('difficulty')!r}")
    if not _nonempty_str(question.get("title")):
        err("title 不能为空")

    tags = question.get("tags")
    if not isinstance(tags, list) or not 3 <= len(tags) <= 5:
        err("TAG 数量必须为 3–5 个")
    else:
        lowered = [t.strip().lower() if isinstance(t, str) else "" for t in tags]
        if any(not t for t in lowered):
            err("TAG 不能为空字符串")
        if len(set(lowered)) != len(lowered):
            err("TAG 重复")
        generic = sorted({t for t in lowered if t in GENERIC_TAGS})
        if generic:
            err(f"TAG 含泛词：{generic}")

    guide = question.get("question_guide")
    if not isinstance(guide, dict):
        err("question_guide 缺失")
    else:
        for key in GUIDE_KEYS:
            if not _nonempty_str(guide.get(key)):
                err(f"question_guide.{key} 不能为空")

    rec = question.get("recommended_answer")
    if not isinstance(rec, dict):
        err("recommended_answer 缺失")
    else:
        if not _nonempty_str(rec.get("summary")):
            err("recommended_answer.summary 不能为空")
        points = rec.get("points")
        if not isinstance(points, list) or not 1 <= len(points) <= 6:
            err("recommended_answer.points 必须为 1–6 条")
        elif not all(_nonempty_str(p) for p in points):
            err("recommended_answer.points 含空条目")

    answer = question.get("technical_answer")
    if not isinstance(answer, dict):
        err("technical_answer 缺失")
    else:
        if "summary" in answer:
            err("technical_answer 不得包含 summary（1.0 无此字段）")
        sections = answer.get("sections")
        if not isinstance(sections, list) or not sections:
            err("technical_answer.sections 至少 1 段")
        else:
            for i, sec in enumerate(sections):
                if (not isinstance(sec, dict) or not _nonempty_str(sec.get("heading"))
                        or not _nonempty_str(sec.get("body"))):
                    err(f"technical_answer.sections[{i}] 的 heading/body 不能为空")
        example = answer.get("example")
        if example is not None:
            if (not isinstance(example, dict)
                    or not _nonempty_str(example.get("scenario"))
                    or not _nonempty_str(example.get("observation"))):
                err("example 需要非空 scenario 与 observation")
            steps = example.get("steps", [])
            if steps and not (isinstance(steps, list)
                              and all(_nonempty_str(s) for s in steps)):
                err("example.steps 必须为非空字符串列表")

    source = question.get("source")
    if not isinstance(source, dict):
        err("source 缺失")
    else:
        if source.get("source_type") != "xhs_note":
            err("source.source_type 必须为 xhs_note")
        if not _nonempty_str(source.get("note_id")):
            err("source.note_id 不能为空")
        if not _nonempty_str(source.get("question_verbatim")):
            err("source.question_verbatim 不能为空")
        if source.get("extraction") not in EXTRACTIONS:
            err("source.extraction 必须为 note_text 或 image_reading")
        if not BATCH_ID_RE.match(source.get("batch_id", "")):
            err("source.batch_id 必须形如 2026-11-16-keyword-slug")

    prov = question.get("editorial_provenance")
    if not isinstance(prov, dict):
        err("editorial_provenance 缺失")
    else:
        for key in ("company", "role", "round"):
            if key not in prov or not isinstance(prov[key], str):
                err(f"editorial_provenance.{key} 必须存在（无信息填 unspecified）")
        frequency = prov.get("frequency", 1)
        if not isinstance(frequency, int) or isinstance(frequency, bool) or frequency < 1:
            err("editorial_provenance.frequency 必须为 ≥1 的整数")

    refs = question.get("technical_references")
    if not isinstance(refs, list) or not refs:
        err("technical_references 至少 1 条")
    else:
        for i, ref in enumerate(refs):
            if not isinstance(ref, dict) or not _nonempty_str(ref.get("title")):
                err(f"technical_references[{i}].title 不能为空")
            url = ref.get("url", "") if isinstance(ref, dict) else ""
            if not (isinstance(url, str) and url.startswith("http")):
                err(f"technical_references[{i}].url 必须为 http(s) 链接")

    related = question.get("related_questions", [])
    if not isinstance(related, list) or len(related) > 4:
        err("related_questions 最多 4 条")
    elif question.get("id") in related:
        err("related_questions 不能包含自身")
    elif len(set(related)) != len(related):
        err("related_questions 重复")

    return errors
```

- [ ] **Step 4: 运行测试确认通过**

Run: 全量 unittest 命令。Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
git add .agents/skills/build-interview-bank/scripts/
git commit -m "feat: 单题 1.0 契约结构校验

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: 学员版与教研版 Markdown 生成

**Files:**
- Modify: `.agents/skills/build-interview-bank/scripts/manage_bank.py`
- Test: `.agents/skills/build-interview-bank/scripts/test_manage_bank.py`

**Interfaces:**
- Consumes: `BASE`、`base_question`（Task 2）
- Produces: `generate_student_markdown(question, taxonomy) -> str`；`generate_editorial_markdown(question, taxonomy) -> str`；`EDITORIAL_LEAK_MARKERS`（Task 5 的 `run_check` 引用）。

学员版结构（顺序固定）：H1 标题 → 元信息行（分类中文名 · 难度中文 · TAG）→ `## 背景描述` / `## 引出的痛点` / `## 考点` / `## 思考方向与解题思路` → `## 推荐答案`（summary + points 列表）→ `## 进阶理解`（sections 各为 H3；有 example 时附「示例」段）。**不得**包含 company/role/round、note_id、question_verbatim、references 之外的教研信息。教研版在学员版基础上追加 `## 教研信息`（来源、批次、笔记 ID、题面原文、提取方式、公司/岗位/轮次、frequency、notes、technical_references 完整列表）。

- [ ] **Step 1: 写失败测试（追加）**

```python
class MarkdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.taxonomy = mb.load_taxonomy(
            mb.REPO_ROOT / "question_bank" / "taxonomy.json")
        cls.student = mb.generate_student_markdown(BASE, cls.taxonomy)
        cls.editorial = mb.generate_editorial_markdown(BASE, cls.taxonomy)

    def test_student_has_required_sections(self):
        text = self.student
        for heading in ("# Q001 · ", "## 背景描述", "## 引出的痛点", "## 考点",
                        "## 思考方向与解题思路", "## 推荐答案", "## 进阶理解"):
            self.assertIn(heading, text)
        self.assertIn("- 大模型提供理解、推理与生成能力", text)
        self.assertIn("### 组成", text)

    def test_student_has_metadata_line(self):
        self.assertIn("AI Agent 架构设计", self.student)
        self.assertIn("低", self.student)

    def test_student_has_no_editorial_leakage(self):
        for marker in mb.EDITORIAL_LEAK_MARKERS:
            self.assertNotIn(marker, self.student)
        self.assertNotIn("某公司", self.student)
        self.assertNotIn(BASE["source"]["note_id"], self.student)

    def test_editorial_contains_provenance(self):
        self.assertIn("## 教研信息", self.editorial)
        self.assertIn("某公司", self.editorial)
        self.assertIn(BASE["source"]["note_id"], self.editorial)
        self.assertIn(BASE["source"]["question_verbatim"], self.editorial)
        self.assertIn("https://www.anthropic.com/research/building-effective-agents",
                      self.editorial)

    def test_example_rendered_when_present(self):
        question = base_question()
        question["technical_answer"]["example"] = {
            "scenario": "开发者要给客服 Agent 加工单查询能力。",
            "steps": ["定义工具描述", "让模型输出调用参数"],
            "observation": "模型返回结构化参数，业务系统执行后把结果回填。"
        }
        text = mb.generate_student_markdown(question, self.taxonomy)
        self.assertIn("开发者要给客服 Agent 加工单查询能力。", text)
        self.assertIn("1. 定义工具描述", text)
```

- [ ] **Step 2: 运行确认失败**

Run: 全量 unittest 命令。Expected: 新增用例 FAIL

- [ ] **Step 3: 实现两个生成函数（追加到 manage_bank.py）**

```python
def generate_student_markdown(question, taxonomy):
    category = taxonomy.get(question["category_id"], {}).get("name", question["category_id"])
    lines = [
        f"# {question['id']} · {question['title']}",
        "",
        f"{category} · {DIFFICULTY_ZH[question['difficulty']]} · "
        + " ".join(f"`{t}`" for t in question["tags"]),
        "",
        "## 背景描述",
        "",
        question["question_guide"]["background"],
        "",
        "## 引出的痛点",
        "",
        question["question_guide"]["pain_point"],
        "",
        "## 考点",
        "",
        question["question_guide"]["focus"],
        "",
        "## 思考方向与解题思路",
        "",
        question["question_guide"]["approach"],
        "",
        "## 推荐答案",
        "",
        question["recommended_answer"]["summary"],
        "",
    ]
    lines += [f"- {p}" for p in question["recommended_answer"]["points"]]
    lines += ["", "## 进阶理解", ""]
    for sec in question["technical_answer"]["sections"]:
        lines += [f"### {sec['heading']}", "", sec["body"], ""]
    example = question["technical_answer"].get("example")
    if example:
        lines += ["**示例**：" + example["scenario"], ""]
        for i, step in enumerate(example.get("steps", []), 1):
            lines.append(f"{i}. {step}")
        if example.get("steps"):
            lines.append("")
        lines += ["观察：" + example["observation"], ""]
    return "\n".join(lines).rstrip() + "\n"


def generate_editorial_markdown(question, taxonomy):
    student = generate_student_markdown(question, taxonomy)
    source = question["source"]
    prov = question["editorial_provenance"]
    lines = [
        student.rstrip(),
        "",
        "---",
        "",
        "## 教研信息（不入学员版）",
        "",
        f"- 批次：`{source['batch_id']}`；笔记 ID：`{source['note_id']}`",
        f"- 提取方式：{source['extraction']}",
        f"- 题面原文：{source['question_verbatim']}",
        f"- 公司/岗位/轮次（发帖人自述）：{prov['company']} / {prov['role']} / {prov['round']}",
        f"- 同题面出现次数：{prov.get('frequency', 1)}",
    ]
    if prov.get("notes"):
        lines.append(f"- 备注：{prov['notes']}")
    lines += ["", "查证参考："]
    for ref in question["technical_references"]:
        lines.append(f"- [{ref['title']}]({ref['url']})")
    lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 4: 运行测试确认通过**

Run: 全量 unittest 命令。Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
git add .agents/skills/build-interview-bank/scripts/
git commit -m "feat: 学员版与教研版 Markdown 生成

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: 审核门禁（review 记录与 SHA-256 校验）

**Files:**
- Modify: `.agents/skills/build-interview-bank/scripts/manage_bank.py`
- Test: `.agents/skills/build-interview-bank/scripts/test_manage_bank.py`

**Interfaces:**
- Consumes: `BASE`（Task 2）
- Produces: `sha256_bytes(data: bytes) -> str`；`review_path(repo_root, batch_id, question_id) -> Path`；`review_errors(review, question_bytes, question) -> list[str]`（校验 decision/question_id/canonical_sha256/canonical_path/author≠reviewer/reviewed_at）。

审核记录文件固定为 `batches/<batch_id>/reviews/content-<ID>.json`，字段：`question_id`、`note_id`、`author_agent`、`reviewer_agent`、`canonical_path`（相对仓库根，如 `question_bank/agent-architecture/low/Q001.json`）、`canonical_sha256`、`reviewed_sections`、`claims_checked`、`issues`、`revision_history`、`decision`（`passed/needs_revision/rejected`）、`reviewed_at`。

- [ ] **Step 1: 写失败测试（追加）**

```python
class ReviewGateTests(unittest.TestCase):
    def make_review(self, **overrides):
        data = json.dumps(BASE, ensure_ascii=False, indent=2).encode("utf-8")
        review = {
            "question_id": "Q001",
            "note_id": BASE["source"]["note_id"],
            "author_agent": "author-agent",
            "reviewer_agent": "reviewer-agent",
            "canonical_path": "question_bank/agent-architecture/low/Q001.json",
            "canonical_sha256": mb.sha256_bytes(data),
            "reviewed_sections": ["recommended_answer", "technical_answer"],
            "claims_checked": ["Agent 组成说法对照 Anthropic 文档"],
            "issues": [],
            "revision_history": [],
            "decision": "passed",
            "reviewed_at": "2026-11-16T12:00:00"
        }
        review.update(overrides)
        return review, data

    def test_passed_review_matches(self):
        review, data = self.make_review()
        self.assertEqual(mb.review_errors(review, data, BASE), [])

    def test_rejects_not_passed(self):
        review, data = self.make_review(decision="needs_revision")
        errors = mb.review_errors(review, data, BASE)
        self.assertTrue(any("passed" in e for e in errors))

    def test_rejects_hash_mismatch(self):
        review, data = self.make_review()
        review["canonical_sha256"] = "0" * 64
        errors = mb.review_errors(review, data, BASE)
        self.assertTrue(any("SHA-256" in e for e in errors))

    def test_rejects_self_review(self):
        review, data = self.make_review(reviewer_agent="author-agent")
        errors = mb.review_errors(review, data, BASE)
        self.assertTrue(any("同一" in e for e in errors))

    def test_review_path_layout(self):
        path = mb.review_path(Path("/repo"), "2026-11-16-test-batch", "Q001")
        self.assertEqual(
            path, Path("/repo/batches/2026-11-16-test-batch/reviews/content-Q001.json"))
```

- [ ] **Step 2: 运行确认失败**

Run: 全量 unittest 命令。Expected: 新增用例 FAIL

- [ ] **Step 3: 实现审核门禁函数（追加到 manage_bank.py）**

```python
def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def review_path(repo_root, batch_id, question_id):
    return Path(repo_root) / "batches" / batch_id / "reviews" / f"content-{question_id}.json"


def review_errors(review, question_bytes, question):
    errors = []

    def err(message):
        errors.append(f"[{question.get('id', '?')}] {message}")

    if review.get("decision") != "passed":
        err(f"审核结论必须为 passed，实际 {review.get('decision')!r}")
    if review.get("question_id") != question.get("id"):
        err("审核记录的 question_id 与题目不一致")
    if review.get("canonical_sha256") != sha256_bytes(question_bytes):
        err("审核 SHA-256 与当前文件字节不一致")
    if review.get("canonical_path") != "question_bank/" + canonical_rel(question):
        err("审核记录的 canonical_path 与题目实际路径不一致")
    if review.get("author_agent") == review.get("reviewer_agent"):
        err("编写与审核不能是同一 Agent")
    if not _nonempty_str(review.get("reviewed_at")):
        err("审核记录缺少 reviewed_at")
    return errors
```

- [ ] **Step 4: 运行测试确认通过**

Run: 全量 unittest 命令。Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
git add .agents/skills/build-interview-bank/scripts/
git commit -m "feat: 独立审核记录与 SHA-256 门禁校验

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: 登记与索引（register_question / generate_indexes / run_check / CLI）

**Files:**
- Modify: `.agents/skills/build-interview-bank/scripts/manage_bank.py`
- Test: `.agents/skills/build-interview-bank/scripts/test_manage_bank.py`

**Interfaces:**
- Consumes: 前四个任务的全部函数。
- Produces: `register_question(repo_root, rel_path) -> list[str]`；`regenerate_question(bank_root, question) -> None`；`generate_indexes(bank_root, catalog, taxonomy) -> None`；`run_check(repo_root) -> list[str]`；`rebuild_all(repo_root) -> list[str]`；`main(argv=None) -> int`。

行为定义：
- `register_question`：路径安全检查（`rel_path` 相对 `question_bank/`，禁止 `..` 与反斜杠）→ 读取并 `validate_question` → `rel_path` 必须等于 `canonical_rel(question)` → 审核记录存在且 `review_errors` 为空 → catalog 中该 ID 未被其他文件占用 → upsert catalog → 写学员版 `.md`（题目同目录）与 `editorial/Qxx.md` → `generate_indexes`。成功返回 `[]`。
- catalog 条目结构：`{"id","title","category_id","difficulty","tags","answer_type","file","batch_id"}`，`file` 为相对 `question_bank/` 的 canonical 路径；写入时更新 `generated_at`（UTC ISO 格式）。
- `generate_indexes` 生成：`question_bank/README.md`（全量表：题目/分类/难度/TAG）、`question_bank/TAGS.md`（TAG → 题目列表）、每个分类目录 `README.md`（该分类表）。空题库时输出「暂无题目」的合法页面。
- `run_check`（只读审计，返回错误列表）：taxonomy/catalog 可加载且版本正确；bank 下每个 `*.json` 通过 `validate_question` 且在 catalog 中；catalog 每条文件存在；学员/教研 Markdown 与重新生成结果一致（不一致报错）；每题审核记录存在、`passed`、哈希一致；学员 `.md` 无 `EDITORIAL_LEAK_MARKERS` 且不含 company/role/round 的非 `unspecified` 值；索引文件与重新生成结果一致。
- `rebuild_all`：重读 bank 下全部题目（校验+审核门禁），重建 catalog、全部 Markdown 与索引。
- CLI：`question_bank` 子命令，`--file/-–question/--check/--all` 四选一（`required=True`, mutually exclusive），`--root` 可选（默认 `REPO_ROOT`，测试用）。`--check` 有错误时退出码 1。

- [ ] **Step 1: 写失败测试（追加）**

```python
import shutil
import tempfile


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        repo = Path(self.tmp.name)
        (repo / "question_bank").mkdir()
        shutil.copy(mb.REPO_ROOT / "question_bank" / "taxonomy.json",
                    repo / "question_bank" / "taxonomy.json")
        mb.write_json(repo / "question_bank" / "catalog.json",
                      {"version": "1.0", "generated_at": None, "questions": []})
        target = repo / "question_bank" / "agent-architecture" / "low"
        target.mkdir(parents=True)
        self.repo = repo
        self.rel = "agent-architecture/low/Q001.json"
        self.file = target / "Q001.json"
        data = json.dumps(BASE, ensure_ascii=False, indent=2) + "\n"
        self.file.write_text(data, encoding="utf-8")
        reviews = repo / "batches" / BASE["source"]["batch_id"] / "reviews"
        reviews.mkdir(parents=True)
        review = {
            "question_id": "Q001",
            "note_id": BASE["source"]["note_id"],
            "author_agent": "author-agent",
            "reviewer_agent": "reviewer-agent",
            "canonical_path": "question_bank/" + self.rel,
            "canonical_sha256": mb.sha256_bytes(self.file.read_bytes()),
            "reviewed_sections": ["recommended_answer"],
            "claims_checked": [],
            "issues": [],
            "revision_history": [],
            "decision": "passed",
            "reviewed_at": "2026-11-16T12:00:00"
        }
        mb.write_json(reviews / "content-Q001.json", review)

    def tearDown(self):
        self.tmp.cleanup()

    def test_register_then_check_clean(self):
        errors = mb.register_question(self.repo, self.rel)
        self.assertEqual(errors, [])
        catalog = mb.read_json(self.repo / "question_bank" / "catalog.json")
        self.assertEqual(catalog["questions"][0]["id"], "Q001")
        self.assertTrue((self.file.with_suffix(".md")).exists())
        self.assertTrue((self.repo / "question_bank" / "editorial" / "Q001.md").exists())
        self.assertEqual(mb.run_check(self.repo), [])

    def test_register_rejects_non_canonical_path(self):
        errors = mb.register_question(self.repo, "agent-architecture/low/Q002.json")
        self.assertTrue(any("canonical" in e or "ID" in e for e in errors))

    def test_register_rejects_missing_review(self):
        (self.repo / "batches" / BASE["source"]["batch_id"] / "reviews"
         / "content-Q001.json").unlink()
        errors = mb.register_question(self.repo, self.rel)
        self.assertTrue(any("审核" in e for e in errors))

    def test_check_detects_tampered_question(self):
        mb.register_question(self.repo, self.rel)
        tampered = base_question()
        tampered["recommended_answer"]["summary"] = "被改过的答案"
        mb.write_json(self.file, tampered)
        errors = mb.run_check(self.repo)
        self.assertTrue(any("SHA-256" in e for e in errors))

    def test_check_detects_stale_markdown(self):
        mb.register_question(self.repo, self.rel)
        md = self.file.with_suffix(".md")
        md.write_text(md.read_text(encoding="utf-8") + "\n<!-- 手改 -->\n",
                      encoding="utf-8")
        errors = mb.run_check(self.repo)
        self.assertTrue(any("Markdown" in e for e in errors))

    def test_cli_check_exit_code(self):
        mb.register_question(self.repo, self.rel)
        self.assertEqual(mb.main(["question_bank", "--check", "--root", str(self.repo)]), 0)


class EmptyBankTests(unittest.TestCase):
    def test_check_on_real_empty_bank(self):
        self.assertEqual(mb.main(["question_bank", "--check"]), 0)
```

- [ ] **Step 2: 运行确认失败**

Run: 全量 unittest 命令。Expected: 新增用例 FAIL

- [ ] **Step 3: 实现登记、索引、审计与 CLI（追加到 manage_bank.py）**

```python
def _utc_now():
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def bank_file(repo_root, rel_path):
    path = PurePosixPath(rel_path)
    if path.is_absolute() or ".." in path.parts or "\\" in rel_path:
        raise ValueError(f"题库内路径不合法：{rel_path}")
    bank_root = Path(repo_root) / "question_bank"
    target = bank_root / path
    if not target.resolve().is_relative_to(bank_root.resolve()):
        raise ValueError(f"题库内路径越界：{rel_path}")
    return target


def catalog_entry(question):
    return {
        "id": question["id"],
        "title": question["title"],
        "category_id": question["category_id"],
        "difficulty": question["difficulty"],
        "tags": question["tags"],
        "answer_type": question["answer_type"],
        "file": canonical_rel(question),
        "batch_id": question["source"]["batch_id"],
    }


def register_question(repo_root, rel_path):
    repo_root = Path(repo_root)
    taxonomy = load_taxonomy(repo_root / "question_bank" / "taxonomy.json")
    try:
        target = bank_file(repo_root, rel_path)
    except ValueError as exc:
        return [str(exc)]
    if not target.exists():
        return [f"文件不存在：question_bank/{rel_path}"]
    question = read_json(target)
    errors = validate_question(question, taxonomy)
    if rel_path != canonical_rel(question):
        errors.append(
            f"路径必须为 canonical 位置 question_bank/{canonical_rel(question)}，"
            f"实际 {rel_path}")
    data = target.read_bytes()
    review_file = review_path(repo_root, question.get("source", {}).get("batch_id", ""),
                              question.get("id", "?"))
    if not review_file.exists():
        errors.append(f"缺少独立审核记录：{review_file.relative_to(repo_root)}")
    else:
        errors += review_errors(read_json(review_file), data, question)
    if errors:
        return errors

    catalog = read_json(repo_root / "question_bank" / "catalog.json")
    for entry in catalog["questions"]:
        if entry["id"] == question["id"] and entry["file"] != canonical_rel(question):
            errors.append(f"ID {question['id']} 已登记于 {entry['file']}")
            return errors
    catalog["questions"] = [e for e in catalog["questions"] if e["id"] != question["id"]]
    catalog["questions"].append(catalog_entry(question))
    catalog["questions"].sort(key=lambda e: e["id"])
    catalog["generated_at"] = _utc_now()
    write_json(repo_root / "question_bank" / "catalog.json", catalog)
    regenerate_question(repo_root / "question_bank", question, taxonomy)
    generate_indexes(repo_root / "question_bank", catalog, taxonomy)
    return []


def regenerate_question(bank_root, question, taxonomy):
    bank_root = Path(bank_root)
    target = bank_root / canonical_rel(question)
    target.with_suffix(".md").write_text(
        generate_student_markdown(question, taxonomy), encoding="utf-8")
    editorial_dir = bank_root / "editorial"
    editorial_dir.mkdir(exist_ok=True)
    (editorial_dir / f"{question['id']}.md").write_text(
        generate_editorial_markdown(question, taxonomy), encoding="utf-8")


def _question_table(entries, taxonomy):
    if not entries:
        return ["暂无题目。", ""]
    rows = ["| 题目 | 分类 | 难度 | TAG |", "| --- | --- | --- | --- |"]
    for e in entries:
        name = taxonomy.get(e["category_id"], {}).get("name", e["category_id"])
        link = f"[{e['id']} · {e['title']}]({e['file'].replace('.json', '.md')})"
        rows.append(f"| {link} | {name} | {DIFFICULTY_ZH[e['difficulty']]} | "
                    + " ".join(f"`{t}`" for t in e["tags"]) + " |")
    return rows + [""]


def generate_indexes(bank_root, catalog, taxonomy):
    bank_root = Path(bank_root)
    questions = catalog["questions"]
    lines = ["# 题库目录", "", f"共 {len(questions)} 题。", ""]
    lines += _question_table(questions, taxonomy)
    (bank_root / "README.md").write_text("\n".join(lines), encoding="utf-8")

    tag_map = {}
    for e in questions:
        for t in e["tags"]:
            tag_map.setdefault(t, []).append(e)
    tag_lines = ["# TAG 索引", ""]
    for t in sorted(tag_map):
        ids = "、".join(e["id"] for e in sorted(tag_map[t], key=lambda e: e["id"]))
        tag_lines.append(f"- `{t}`：{ids}")
    tag_lines.append("")
    (bank_root / "TAGS.md").write_text("\n".join(tag_lines), encoding="utf-8")

    for category_id, category in taxonomy.items():
        entries = [e for e in questions if e["category_id"] == category_id]
        cat_lines = [f"# {category['name']}", "", f"范围：{category['scope']}", ""]
        cat_lines += _question_table(entries, taxonomy)
        (bank_root / category_id).mkdir(exist_ok=True)
        (bank_root / category_id / "README.md").write_text(
            "\n".join(cat_lines), encoding="utf-8")


def _iter_question_files(bank_root):
    bank_root = Path(bank_root)
    for path in sorted(bank_root.glob("*/*/*.json")):
        if path.name not in ("catalog.json", "taxonomy.json") and path.is_file():
            yield path


def run_check(repo_root):
    repo_root = Path(repo_root)
    bank_root = repo_root / "question_bank"
    errors = []
    try:
        taxonomy = load_taxonomy(bank_root / "taxonomy.json")
    except (OSError, ValueError) as exc:
        return [f"taxonomy 加载失败：{exc}"]
    catalog = read_json(bank_root / "catalog.json")
    if catalog.get("version") != CONTRACT_VERSION:
        errors.append("catalog 必须为 1.0 版")
    by_id = {e["id"]: e for e in catalog["questions"]}
    for path in _iter_question_files(bank_root):
        question = read_json(path)
        errors += validate_question(question, taxonomy)
        rel = str(path.relative_to(bank_root)).replace("\\", "/")
        if rel not in {e["file"] for e in catalog["questions"]}:
            errors.append(f"[{question.get('id', '?')}] 未登记入 catalog：{rel}")
        review_file = review_path(
            repo_root, question.get("source", {}).get("batch_id", ""),
            question.get("id", "?"))
        if not review_file.exists():
            errors.append(f"[{question.get('id', '?')}] 缺少独立审核记录")
        else:
            errors += review_errors(read_json(review_file), path.read_bytes(), question)
        student = path.with_suffix(".md")
        if not student.exists():
            errors.append(f"[{question['id']}] 缺少学员版 Markdown")
        elif student.read_text(encoding="utf-8") != generate_student_markdown(question, taxonomy):
            errors.append(f"[{question['id']}] 学员版 Markdown 与 JSON 不一致（应编辑 JSON 后重新生成）")
        else:
            for marker in EDITORIAL_LEAK_MARKERS:
                if marker in student.read_text(encoding="utf-8"):
                    errors.append(f"[{question['id']}] 学员版泄漏教研标记：{marker}")
            prov = question.get("editorial_provenance", {})
            for key in ("company", "role", "round"):
                value = prov.get(key, "unspecified")
                if value not in ("unspecified", "") and value in student.read_text(encoding="utf-8"):
                    errors.append(f"[{question['id']}] 学员版泄漏 {key}：{value}")
        editorial = bank_root / "editorial" / f"{question['id']}.md"
        if not editorial.exists():
            errors.append(f"[{question['id']}] 缺少教研版 Markdown")
        elif editorial.read_text(encoding="utf-8") != generate_editorial_markdown(question, taxonomy):
            errors.append(f"[{question['id']}] 教研版 Markdown 与 JSON 不一致")
    for entry in catalog["questions"]:
        if not (bank_root / entry["file"]).exists():
            errors.append(f"[{entry['id']}] catalog 指向的文件不存在：{entry['file']}")
    generate_indexes(bank_root, catalog, taxonomy)
    for index in ["README.md", "TAGS.md"] + [f"{c}/README.md" for c in taxonomy]:
        # generate_indexes 刚重写索引；若此前磁盘版本不同，无法在此检测，
        # 因此索引以重生成结果为准（--check 后需提交差异或使用 --all）。
        pass
    return errors


def rebuild_all(repo_root):
    repo_root = Path(repo_root)
    bank_root = repo_root / "question_bank"
    taxonomy = load_taxonomy(bank_root / "taxonomy.json")
    catalog = {"version": CONTRACT_VERSION, "generated_at": _utc_now(), "questions": []}
    errors = []
    for path in _iter_question_files(bank_root):
        question = read_json(path)
        errors += validate_question(question, taxonomy)
        review_file = review_path(
            repo_root, question.get("source", {}).get("batch_id", ""),
            question.get("id", "?"))
        if not review_file.exists():
            errors.append(f"[{question.get('id', '?')}] 缺少独立审核记录")
        else:
            errors += review_errors(read_json(review_file), path.read_bytes(), question)
        catalog["questions"].append(catalog_entry(question))
    if errors:
        return errors
    catalog["questions"].sort(key=lambda e: e["id"])
    write_json(bank_root / "catalog.json", catalog)
    for entry in catalog["questions"]:
        regenerate_question(bank_root, read_json(bank_root / entry["file"]), taxonomy)
    generate_indexes(bank_root, catalog, taxonomy)
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description="小红书面经题库管理")
    sub = parser.add_subparsers(dest="command", required=True)
    bank = sub.add_parser("question_bank")
    group = bank.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="相对 question_bank/ 的新题 JSON 路径")
    group.add_argument("--question", help="单题 ID，如 Q001（重新生成）")
    group.add_argument("--check", action="store_true", help="全量只读审计")
    group.add_argument("--all", action="store_true", help="全量重建")
    bank.add_argument("--root", default=str(REPO_ROOT), help="仓库根目录（默认脚本所属仓库）")
    args = parser.parse_args(argv)

    repo_root = Path(args.root)
    if args.file:
        errors = register_question(repo_root, args.file)
    elif args.question:
        bank_root = repo_root / "question_bank"
        taxonomy = load_taxonomy(bank_root / "taxonomy.json")
        catalog = read_json(bank_root / "catalog.json")
        entry = next((e for e in catalog["questions"] if e["id"] == args.question), None)
        if entry is None:
            errors = [f"题目未登记：{args.question}"]
        else:
            regenerate_question(bank_root, read_json(bank_root / entry["file"]), taxonomy)
            errors = []
    elif args.check:
        errors = run_check(repo_root)
    else:
        errors = rebuild_all(repo_root)
    for message in errors:
        print(message, file=sys.stderr)
    if errors:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

注意 `run_check` 中调用了 `generate_indexes` 会写文件——与「只读审计」矛盾。实现时改为：先把索引生成到字符串再比较（把 `generate_indexes` 拆出 `_index_texts(bank_root, catalog, taxonomy) -> dict[path, str]`，`generate_indexes` 调它落盘，`run_check` 用它比较磁盘内容，不一致报错且不落盘）。按此实现，测试中「手改 Markdown」用例即可通过；`run_check` 对真实空题库（Task 1 创建的 catalog）返回 0。

- [ ] **Step 4: 运行测试确认通过**

Run: 全量 unittest 命令。Expected: 全部 PASS（含 CLI 用例）

- [ ] **Step 5: 手工冒烟：空题库 CLI**

```bash
cd /d/yuege/xhs-interview-bank
D:/MSYS2/ucrt64/bin/python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --check
```
Expected: 输出 `OK`，退出码 0

- [ ] **Step 6: 提交**

```bash
git add .agents/skills/build-interview-bank/scripts/
git commit -m "feat: 题目登记、目录索引、只读审计与 CLI

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: 两个 Skill 文档

**Files:**
- Create: `.agents/skills/harvest-xhs-interviews/SKILL.md`
- Create: `.agents/skills/harvest-xhs-interviews/references/acquisition.md`
- Create: `.agents/skills/build-interview-bank/SKILL.md`
- Create: `.agents/skills/build-interview-bank/references/content-contract.md`
- Create: `.agents/skills/build-interview-bank/references/admission-review.md`

**Interfaces:**
- Consumes: Task 1–5 的 CLI 命令、契约字段、审核记录格式（文档中的命令与字段名必须与之完全一致）。
- Produces: 两个 Skill 的完整规范，供后续批次运行使用。

- [ ] **Step 1: 写 harvest-xhs-interviews/SKILL.md（完整内容）**

```markdown
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
```

- [ ] **Step 2: 写 references/acquisition.md（完整内容）**

```markdown
# 采集与画面复核细则

已有冻结清单或仅修改题库时跳过本文件。

## 搜索采集

1. 复用用户已登录浏览器打开小红书搜索页，输入批次关键词，按「最新」或默认排序滚动加载。
2. 只采集搜索结果主体，排除广告卡片与推荐流其他笔记；记录每页可见数与是否到底。
3. 笔记卡片信息（标题、作者、点赞数）先入清单草稿；进入详情页核对后回填正文与发布时间。
4. 短时间大量翻页可能触发风控；出现验证码立即停止并记录，由用户处理后继续，不自动重试绕过。

## 证据保存

- `notes/<note_id>/note.json`：正文原文、发布时间、点赞数、采集时间、URL。
- `notes/<note_id>/images/`：原图按页面顺序命名 `01.jpg` 起。
- `notes/<note_id>/image-extract.md`：画面提取的题面，每条注明来源图片（如 `> 来自 02.jpg`）。正文与画面提取分开保存，不合并成一份「原文」。
- 笔记可能被删除或改权限：URL 只作辅助定位，证据以快照为准。

## 画面复核规则

- Agent 逐图视觉读取，能可靠辨认的题面原文抄录（保留原错别字，纠错在编题阶段记录）；辨认不清的部分标注 `unreadable`，整题不可靠则该题不入 candidates。
- 手写、低分辨率、被水印遮挡的内容不猜测补全。
- 同一帖多图出现同一题（如题目页+答案页重复），合并为一条 candidate。
```

- [ ] **Step 3: 写 build-interview-bank/SKILL.md（完整内容）**

```markdown
---
name: build-interview-bank
description: 将面经裸题编写为教学面试题：语义去重、来源定难度、编写推荐答案与进阶理解并附实际查阅的官方参考，经未参与编写的独立 Agent 审核通过（SHA-256 一致）后按分类/难度单题入库。
---

# 面经题编写与入库

输入为批次 `candidates.json` 中 `pending` 的裸题，或已有题目的修订请求。产出 1.0 契约单题 JSON，经独立审核后入库。

## 流程

1. **去重**：按 [准入审核](references/admission-review.md) 四维规则与既有题库及本批已保留题比较，>70% 弃，登记 `duplicate_of:Qxx`；同题面再次出现时给已有题的 `editorial_provenance.frequency` 加一并修订教研备注。
2. **定档**：直问概念/机制默认 low；需要选型、定位、边界判断为 medium；high 仅当帖子真实出现系统性追问链或跨模块设计题，补写场景不升档。
3. **编写**：按 [数据契约](references/content-contract.md) 生成 JSON，答案依据官方文档/论文编写，`technical_references` 只记实际查阅的来源；候选人自述答法只作题面语境，不作为技术依据。
4. **独审**：交未参与编写的独立 Agent 审核并生成审核记录；`passed` 且 SHA-256 与文件字节一致才登记。
5. **入库**：`python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --file <相对路径>`，随后同步根 README 统计。

## 硬性规则

- 公司/岗位/轮次、发帖人、原帖信息只进 `editorial_provenance` 与批次记录，学员版 JSON 字段与 Markdown 均不得出现。
- 不虚构企业项目、业绩数字；无结果的验证写验证计划。
- ID 全局唯一递增（Q001 起），编号空洞不复用；编号分配前检查 catalog 与本批预留。
- 修订已有题：改 JSON → 重新独审绑定新 SHA → `--question Qxx` 重新生成。
- 学员正文不出现「博主/发帖人/原帖/教研补充」旁白。
```

- [ ] **Step 4: 写 references/content-contract.md（完整内容）**

```markdown
# 1.0 数据契约

唯一事实源：`question_bank/<category-id>/<low|medium|high>/<ID>.json`。同路径 `.md` 与 `editorial/<ID>.md` 由脚本生成，不手改。

分类与难度以 `question_bank/taxonomy.json` 为准（9 类，英文 ID）。TAG 3–5 个具体技术词，禁用泛词：ai、面试、高级、人工智能、大模型、agent、llm。

## 字段

| 字段 | 约定 |
| --- | --- |
| `id` / `version` | `Q\\d{3}` 递增；`"1.0"` |
| `answer_type` | v1.0 仅 `"technical"` |
| `category_id` / `difficulty` | taxonomy 注册分类；`low/medium/high` |
| `title` | 题面改写的教学化问句，独立可读 |
| `tags` | 3–5 个，具体概念/机制/方法/框架 |
| `question_guide` | `background/pain_point/focus/approach` 四键非空；背景 1–2 句，思路 2–3 步 |
| `recommended_answer` | `summary` 1–2 句直接结论；`points` 1–6 条非空，覆盖题干全部子问；整体约 180–350 汉字 |
| `technical_answer` | 无 `summary` 键；`sections` ≥1 段（heading/body）；可选 `example`（scenario/steps/observation） |
| `source` | `source_type:"xhs_note"`、`note_id`、`question_verbatim`（题面原文，含原错别字）、`extraction`（`note_text/image_reading`）、`batch_id` |
| `editorial_provenance` | `company/role/round`（无信息 `"unspecified"`）、`frequency`（≥1 整数）、`notes`；仅教研侧 |
| `technical_references` | ≥1 条 `{title,url}`，实际查阅的官方文档/论文 |
| `related_questions` | 0–4 条，有具体理由才加，不含自身、不重复 |

## 编写规范

- 推荐答案可直接用于面试表达；进阶理解解释机制、条件与边界，不与推荐答案同义重复。
- 示例先说明谁在做什么、要解决什么问题，再给动作与观察；术语先解释对象与用途。
- `question_verbatim` 保留原帖题面（含原错别字）；纠错与改写说明写 `editorial_provenance.notes`。

完整合法示例见 `scripts/test_manage_bank.py` 的 `BASE` 基件。
```

- [ ] **Step 5: 写 references/admission-review.md（完整内容）**

```markdown
# 准入审核与独立知识审核

## 语义去重（四维评审）

对候选题与最相近既有题按四维打分：核心问题 40、解题路径 30、知识边界 20、关键约束 10。

- 合计 **>70% 不入库**，candidates 记 `duplicate_of:Qxx`，reason 写各项分值与理由。
- 恰好 70% 复审：只有来源支持的实质增量才保留。
- 这是教研语义评审，不冒充 Embedding 分数或统计概率。不靠换公司名、改数字、加模拟约束掩盖重复。
- 同题面再出现：已有题 `frequency` +1 并修订教研备注，不新建题。

## 难度

| 档 | 条件 |
| --- | --- |
| low | 直接解释概念、组成、机制、区别 |
| medium | 选型、定位瓶颈、边界判断 |
| high | 帖子真实出现系统性追问链或跨模块设计题（保留原帖证据） |

## 独立知识审核（硬门禁）

- 审核者为**未参与该题编写**的 Agent；通读推荐答案、进阶理解、示例与导读。
- 逐项核对：题干子问覆盖、术语与机制、API/版本边界、关键主张对照官方文档实际核查、示例可理解性。
- 审核记录 `batches/<batch_id>/reviews/content-<ID>.json`：

```json
{
  "question_id": "Q001", "note_id": "…",
  "author_agent": "…", "reviewer_agent": "…",
  "canonical_path": "question_bank/<cat>/<level>/Q001.json",
  "canonical_sha256": "…",
  "reviewed_sections": ["recommended_answer", "technical_answer"],
  "claims_checked": [{"claim": "…", "evidence": "官方文档 URL", "result": "confirmed"}],
  "issues": [], "revision_history": [],
  "decision": "passed", "reviewed_at": "2026-11-16T12:00:00"
}
```

- `needs_revision` 退回编写者修订后复核；根本概念错误不放行。审核者不代写后给自己通过；结构脚本通过不替代知识审核。
- 仅 `decision=passed` 且 `canonical_sha256` 与当前 JSON 字节一致时，`manage_bank.py --file` 才会登记。
```

- [ ] **Step 6: 一致性检查**

```bash
cd /d/yuege/xhs-interview-bank
grep -rn "manage_bank.py question_bank" .agents/skills/ | grep -o "\-\-[a-z]*" | sort -u
# 预期：--file --question --check --all（与 argparse 定义一致）
grep -c "recommended_answer" .agents/skills/build-interview-bank/references/content-contract.md
# 预期 ≥1
```

- [ ] **Step 7: 提交**

```bash
git add .agents/skills/
git commit -m "docs: 面经采集与编题入库两个 Skill 规范

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: 根 README 与端到端验证

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: 全部前序任务产物。
- Produces: 仓库入口文档；空题库全链路验证通过。

- [ ] **Step 1: 写 README.md（完整内容）**

```markdown
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
```

- [ ] **Step 2: 端到端验证**

```bash
cd /d/yuege/xhs-interview-bank
PYTHONDONTWRITEBYTECODE=1 D:/MSYS2/ucrt64/bin/python3 -m unittest discover \
  -s .agents/skills/build-interview-bank/scripts -p 'test_*.py' -v
# 预期：全部 PASS
D:/MSYS2/ucrt64/bin/python3 .agents/skills/build-interview-bank/scripts/manage_bank.py question_bank --check
# 预期：OK，退出码 0
git status --short
# 预期：除 README.md 外无未预期变更
```

- [ ] **Step 3: 提交**

```bash
git add README.md
git commit -m "docs: 仓库入口 README 与空题库端到端验证

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-Review 记录

- **Spec 覆盖**：设计 §3 架构（Task 1/5/6）、§4 采集（Task 6 harvest Skill）、§5 提取去重（Task 6 admission-review + candidates.json）、§6 契约与审核（Task 2/3/4/6）、§7 脚本（Task 5）、§8 统计口径（Task 6/7 README 要求）、§10 节奏（本计划为骨架阶段，试运行另起批次任务）——均有对应任务。网站、无人值守按设计 §9 为非目标。
- **占位符**：无 TBD/TODO；所有代码步骤给出完整代码；Task 6 文档为完整内容。
- **类型一致性**：`validate_question(question, taxonomy) -> list[str]`、`register_question(repo_root, rel_path) -> list[str]`、`run_check(repo_root) -> list[str]`、`review_errors(review, question_bytes, question) -> list[str]`、`generate_student_markdown(question, taxonomy) -> str` 在测试与实现间一致；Task 5 已注明 `run_check` 须用 `_index_texts` 字符串比较保持只读。
