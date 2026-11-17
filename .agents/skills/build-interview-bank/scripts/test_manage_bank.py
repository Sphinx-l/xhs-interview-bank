# test_manage_bank.py
"""manage_bank 单元测试。运行：
PYTHONDONTWRITEBYTECODE=1 D:/MSYS2/ucrt64/bin/python3 -m unittest discover \
  -s .agents/skills/build-interview-bank/scripts -p 'test_*.py' -v
"""
import copy
import json
import shutil
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
        # 新政策：真题来源行允许携带公司/岗位/轮次（发帖人自述），其余正文仍不得泄漏。
        body = "\n".join(
            ln for ln in self.student.splitlines() if not ln.startswith("> 真题来源")
        )
        for marker in mb.EDITORIAL_LEAK_MARKERS:
            self.assertNotIn(marker, body)
        self.assertNotIn("某公司", body)
        self.assertNotIn(BASE["source"]["note_id"], self.student)
        # 来源行应包含公司与免责标注
        self.assertIn("真题来源：某公司", self.student)
        self.assertIn("发帖人自述", self.student)

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
        shutil.copy(self.file, self.file.with_name("Q002.json"))
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

    def test_check_reports_corrupt_catalog_without_crash(self):
        mb.register_question(self.repo, self.rel)
        (self.repo / "question_bank" / "catalog.json").write_text(
            "{ 不是合法 JSON", encoding="utf-8")
        errors = mb.run_check(self.repo)
        self.assertTrue(any("catalog" in e for e in errors),
                        f"期望错误包含 'catalog'，实际 {errors}")

    def test_check_reports_invalid_fields_with_stale_md_without_crash(self):
        bad = base_question(id="Q002", title="", difficulty="mid")
        mb.write_json(self.repo / "question_bank" / "agent-architecture" / "low"
                      / "Q002.json", bad)
        (self.repo / "question_bank" / "agent-architecture" / "low"
         / "Q002.md").write_text("# 旧的学员版\n", encoding="utf-8")
        errors = mb.run_check(self.repo)
        self.assertTrue(any("Q002" in e for e in errors))
        self.assertTrue(any("title" in e for e in errors))

    def test_index_readmes_use_dir_relative_links(self):
        mb.register_question(self.repo, self.rel)
        root_readme = (self.repo / "question_bank" / "README.md").read_text(
            encoding="utf-8")
        self.assertIn("(agent-architecture/low/Q001.md)", root_readme)
        cat_readme = (self.repo / "question_bank" / "agent-architecture" / "README.md"
                      ).read_text(encoding="utf-8")
        self.assertIn("(low/Q001.md)", cat_readme)
        self.assertNotIn("(agent-architecture/low/Q001.md)", cat_readme)

    def test_question_cli_refuses_tampered_file(self):
        mb.register_question(self.repo, self.rel)
        tampered = base_question()
        tampered["recommended_answer"]["summary"] = "被改过的答案"
        mb.write_json(self.file, tampered)
        self.assertEqual(
            mb.main(["question_bank", "--question", "Q001", "--root", str(self.repo)]),
            1)


class EmptyBankTests(unittest.TestCase):
    def test_check_on_real_empty_bank(self):
        self.assertEqual(mb.main(["question_bank", "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
