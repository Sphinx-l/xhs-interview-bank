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

    def test_rejects_non_dict_example_without_crash(self):
        bad = base_question()
        bad["technical_answer"]["example"] = "bad"
        errors = mb.validate_question(bad, self.taxonomy)
        self.assertTrue(any("example" in e for e in errors),
                        f"期望错误包含 'example'，实际 {errors}")

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


if __name__ == "__main__":
    unittest.main()
