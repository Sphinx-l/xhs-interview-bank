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
            if not isinstance(example, dict):
                err("example 需要非空 scenario 与 observation")
            else:
                if (not _nonempty_str(example.get("scenario"))
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
