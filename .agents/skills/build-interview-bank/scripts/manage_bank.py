"""小红书面经题库：登记、校验与生成脚本（契约 1.1）。仅标准库，任意 Python ≥ 3.9。

用法（仓库根目录，python 可按环境换成 py / python3）：
  python .../manage_bank.py question_bank --file <相对question_bank的JSON路径>
  python .../manage_bank.py question_bank --question Q001
  python .../manage_bank.py question_bank --check
  python .../manage_bank.py question_bank --all
  python .../manage_bank.py question_bank --sighting Q001 --batch <批次ID> \
      --note <笔记ID> [--recall <口述ID>] [--company X] [--role Y] [--round Z] [--seen-at YYYY-MM-DD]
"""

import argparse
import datetime as _dt
import hashlib
import json
import posixpath
import re
import sys
from pathlib import Path, PurePosixPath

SKILL_DIR = Path(__file__).resolve().parent
REPO_ROOT = SKILL_DIR.parents[3]

CONTRACT_VERSION = "1.1"
DIFFICULTIES = ("low", "medium", "high")
DIFFICULTY_ZH = {"low": "低", "medium": "中", "high": "高"}
GENERIC_TAGS = {"ai", "面试", "高级", "人工智能", "大模型", "agent", "llm"}
GUIDE_KEYS = ("background", "pain_point", "focus", "approach")
SOURCE_TYPES = ("xhs_note", "student_recall")
XHS_EXTRACTIONS = ("note_text", "image_reading")
RECALL_EXTRACTION = "oral_recall"
OCCURRENCE_KEYS = ("batch_id", "company", "role", "round", "seen_at")
EDITORIAL_LEAK_MARKERS = ("发帖人", "博主", "原帖", "原视频", "教研", "来源：小红书")
ID_RE = re.compile(r"^Q\d{3}$")
BATCH_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_taxonomy(path):
    """读取并做最小结构校验，返回 {分类ID: 分类对象}。"""
    data = read_json(path)
    if data.get("version") != CONTRACT_VERSION:
        raise ValueError(f"taxonomy 必须为 {CONTRACT_VERSION} 版")
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
    return (f"{question.get('category_id', '?')}/"
            f"{question.get('difficulty', '?')}/{question.get('id', '?')}.json")


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
    source_type = source.get("source_type") if isinstance(source, dict) else None
    if not isinstance(source, dict):
        err("source 缺失")
    else:
        if source_type not in SOURCE_TYPES:
            err("source.source_type 必须为 xhs_note 或 student_recall")
        if source_type == "student_recall":
            if not _nonempty_str(source.get("recall_id")):
                err("student_recall 来源必须提供 recall_id")
            if _nonempty_str(source.get("note_id")):
                err("student_recall 来源不得填写 note_id")
            if source.get("extraction") != RECALL_EXTRACTION:
                err("student_recall 的 source.extraction 必须为 oral_recall")
        elif source_type == "xhs_note":
            if not _nonempty_str(source.get("note_id")):
                err("source.note_id 不能为空")
            if source.get("extraction") not in XHS_EXTRACTIONS:
                err("source.extraction 必须为 note_text 或 image_reading")
        if not _nonempty_str(source.get("question_verbatim")):
            err("source.question_verbatim 不能为空")
        if not BATCH_ID_RE.match(source.get("batch_id", "")):
            err("source.batch_id 必须形如 2026-11-16-keyword-slug")

    prov = question.get("editorial_provenance")
    if not isinstance(prov, dict):
        err("editorial_provenance 缺失")
    else:
        for key in ("company", "role", "round"):
            if key not in prov or not isinstance(prov[key], str):
                err(f"editorial_provenance.{key} 必须存在（无信息填 unspecified）")
        occurrences = prov.get("occurrences")
        if not isinstance(occurrences, list) or not occurrences:
            err("editorial_provenance.occurrences 至少 1 条（首条为入库来源）")
        else:
            origin_key = ("recall_id" if source_type == "student_recall" else "note_id")
            seen_pairs = set()
            for i, occ in enumerate(occurrences):
                if not isinstance(occ, dict):
                    err(f"occurrences[{i}] 必须为对象")
                    continue
                for key in OCCURRENCE_KEYS:
                    if not _nonempty_str(occ.get(key)):
                        err(f"occurrences[{i}].{key} 不能为空（无信息填 unspecified）")
                if not _nonempty_str(occ.get(origin_key)):
                    err(f"occurrences[{i}].{origin_key} 不能为空")
                if not DATE_RE.match(occ.get("seen_at", "")):
                    err(f"occurrences[{i}].seen_at 必须为 YYYY-MM-DD")
                if not BATCH_ID_RE.match(occ.get("batch_id", "")):
                    err(f"occurrences[{i}].batch_id 必须形如 2026-11-16-keyword-slug")
                pair = (occ.get("batch_id", ""), occ.get(origin_key, ""))
                if pair in seen_pairs:
                    err(f"occurrences[{i}] 重复：{pair[0]}/{pair[1]} 已登记")
                seen_pairs.add(pair)
        frequency = prov.get("frequency")
        if frequency is not None:
            if not isinstance(frequency, int) or isinstance(frequency, bool):
                err("editorial_provenance.frequency 必须为整数")
            elif isinstance(occurrences, list) and occurrences \
                    and frequency != len(occurrences):
                err(f"frequency 必须等于 occurrences 条数（当前 {len(occurrences)} 条）")
        chain = prov.get("follow_up_chain")
        if chain is not None:
            if (not isinstance(chain, list) or not chain
                    or any(not isinstance(c, str) or not ID_RE.match(c) for c in chain)):
                err("follow_up_chain 必须为 Qxxx ID 的非空列表")
            else:
                if question.get("id") not in chain:
                    err("follow_up_chain 必须包含自身 ID")
                if len(set(chain)) != len(chain):
                    err("follow_up_chain 重复")

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
    occurrences = prov.get("occurrences")
    if not isinstance(occurrences, list):
        occurrences = []
    frequency = len(occurrences) or prov.get("frequency", 1)
    dates = sorted(str(o.get("seen_at")) for o in occurrences
                   if isinstance(o, dict) and o.get("seen_at"))
    span = f"（首见 {dates[0]}，最近 {dates[-1]}）" if dates else ""
    origin_id = source.get("recall_id") or source.get("note_id", "")
    lines = [
        student.rstrip(),
        "",
        "---",
        "",
        "## 教研信息（不入学员版）",
        "",
        f"- 批次：`{source['batch_id']}`；来源 ID：`{origin_id}`（{source.get('extraction', '?')}）",
        f"- 题面原文：{source['question_verbatim']}",
        f"- 公司/岗位/轮次（发帖人自述）：{prov['company']} / {prov['role']} / {prov['round']}",
        f"- 同题面出现次数：{frequency}{span}",
    ]
    if occurrences:
        lines.append("- 出现轨迹（自述信息，教研侧）：")
        for occ in occurrences:
            oid = occ.get("recall_id") or occ.get("note_id", "?")
            lines.append(f"  - {occ.get('seen_at', '?')} · {occ.get('company', '?')}"
                         f" / {occ.get('role', '?')} / {occ.get('round', '?')}"
                         f" · `{occ.get('batch_id', '?')}` · `{oid}`")
    if prov.get("follow_up_chain"):
        lines.append("- 同场追问链：" + " → ".join(prov["follow_up_chain"]))
    if prov.get("notes"):
        lines.append(f"- 备注：{prov['notes']}")
    lines += ["", "查证参考："]
    for ref in question["technical_references"]:
        lines.append(f"- [{ref['title']}]({ref['url']})")
    lines.append("")
    return "\n".join(lines)


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
    source = question.get("source") if isinstance(question.get("source"), dict) else {}
    prov = question.get("editorial_provenance")
    if not isinstance(prov, dict):
        prov = {}
    occurrences = prov.get("occurrences")
    if not isinstance(occurrences, list):
        occurrences = []
    dates = sorted(str(o.get("seen_at")) for o in occurrences
                   if isinstance(o, dict) and o.get("seen_at"))
    origin_key = "recall_id" if source.get("source_type") == "student_recall" else "note_id"
    return {
        "id": question.get("id"),
        "title": question.get("title"),
        "category_id": question.get("category_id"),
        "difficulty": question.get("difficulty"),
        "tags": question.get("tags"),
        "answer_type": question.get("answer_type"),
        "file": canonical_rel(question),
        "batch_id": source.get("batch_id"),
        "origin_id": source.get(origin_key),
        "first_seen": dates[0] if dates else None,
        "last_seen": dates[-1] if dates else None,
        "frequency": len(occurrences),
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


def _question_table(entries, taxonomy, index_dir=""):
    """index_dir 为索引文件所在目录（相对 bank 根的 POSIX 路径，根为空串），
    链接据此换算为相对该索引文件的路径。"""
    if not entries:
        return ["暂无题目。", ""]
    rows = ["| 题目 | 分类 | 难度 | TAG |", "| --- | --- | --- | --- |"]
    for e in entries:
        name = taxonomy.get(e["category_id"], {}).get("name", e["category_id"])
        md_path = e["file"].replace(".json", ".md")
        link_path = posixpath.relpath(md_path, index_dir or ".")
        link = f"[{e['id']} · {e['title']}]({link_path})"
        rows.append(f"| {link} | {name} | {DIFFICULTY_ZH[e['difficulty']]} | "
                    + " ".join(f"`{t}`" for t in e["tags"]) + " |")
    return rows + [""]


def _by_company_text(bank_root, catalog):
    """公司 × 题目索引（教研侧）。从各题 occurrences 聚合；文件缺失时跳过（另行报错）。"""
    bank_root = Path(bank_root)
    by_company = {}
    for entry in catalog["questions"]:
        path = bank_root / entry.get("file", "")
        if not path.exists():
            continue
        question = read_json(path)
        prov = question.get("editorial_provenance")
        if not isinstance(prov, dict):
            continue
        for occ in prov.get("occurrences", []):
            if not isinstance(occ, dict):
                continue
            company = occ.get("company")
            if not _nonempty_str(company) or company == "unspecified":
                continue
            by_company.setdefault(company, []).append({
                "id": question.get("id", "?"),
                "title": question.get("title", ""),
                "role": occ.get("role", "unspecified"),
                "round": occ.get("round", "unspecified"),
                "seen_at": str(occ.get("seen_at", "")),
                "md": entry.get("file", "").replace(".json", ".md"),
            })
    lines = ["# 公司 × 题目索引（教研侧）", "",
             "由各题 `editorial_provenance.occurrences` 聚合生成，仅教研侧使用，不入学员版。",
             "公司名为发帖人/学员自述，不做事实核实。", ""]
    if not by_company:
        lines += ["暂无公司署名的出现记录。", ""]
    for company in sorted(by_company):
        sightings = sorted(by_company[company],
                           key=lambda s: (s["seen_at"], s["id"]), reverse=True)
        lines += [f"## {company}", "",
                  "| 题目 | 轮次 | 岗位 | 最近出现 |", "| --- | --- | --- | --- |"]
        seen_ids = set()
        for s in sightings:
            if s["id"] in seen_ids:
                continue
            seen_ids.add(s["id"])
            link_path = posixpath.relpath(s["md"], "editorial")
            lines.append(f"| [{s['id']} · {s['title']}]({link_path}) "
                         f"| {s['round']} | {s['role']} | {s['seen_at']} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _index_texts(bank_root, catalog, taxonomy):
    """计算全部索引文件的精确内容；返回 {绝对路径: 文本}，不写盘。"""
    bank_root = Path(bank_root)
    questions = catalog["questions"]
    texts = {}
    lines = ["# 题库目录", "", f"共 {len(questions)} 题。", ""]
    lines += _question_table(questions, taxonomy)
    texts[bank_root / "README.md"] = "\n".join(lines)

    tag_map = {}
    for e in questions:
        for t in e["tags"]:
            tag_map.setdefault(t, []).append(e)
    tag_lines = ["# TAG 索引", ""]
    for t in sorted(tag_map):
        ids = "、".join(e["id"] for e in sorted(tag_map[t], key=lambda e: e["id"]))
        tag_lines.append(f"- `{t}`：{ids}")
    tag_lines.append("")
    texts[bank_root / "TAGS.md"] = "\n".join(tag_lines)

    for category_id, category in taxonomy.items():
        entries = [e for e in questions if e["category_id"] == category_id]
        cat_lines = [f"# {category['name']}", "", f"范围：{category['scope']}", ""]
        cat_lines += _question_table(entries, taxonomy, index_dir=category_id)
        texts[bank_root / category_id / "README.md"] = "\n".join(cat_lines)

    texts[bank_root / "editorial" / "by-company.md"] = _by_company_text(bank_root, catalog)
    return texts


def generate_indexes(bank_root, catalog, taxonomy):
    for path, text in _index_texts(bank_root, catalog, taxonomy).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


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
    try:
        catalog = read_json(bank_root / "catalog.json")
    except (OSError, ValueError) as exc:
        return [f"catalog 加载失败：{exc}"]
    if catalog.get("version") != CONTRACT_VERSION:
        errors.append(f"catalog 必须为 {CONTRACT_VERSION} 版")
    for path in _iter_question_files(bank_root):
        question = read_json(path)
        question_id = question.get("id", "?")
        validation_errors = validate_question(question, taxonomy)
        errors += validation_errors
        rel = str(path.relative_to(bank_root)).replace("\\", "/")
        if rel not in {e["file"] for e in catalog["questions"]}:
            errors.append(f"[{question_id}] 未登记入 catalog：{rel}")
        stored = next((e for e in catalog["questions"] if e.get("id") == question_id), None)
        if stored is not None and stored != catalog_entry(question):
            errors.append(f"[{question_id}] catalog 条目与题目文件不一致"
                          f"（重新 --file 登记或 --all 重建）")
        review_file = review_path(
            repo_root, question.get("source", {}).get("batch_id", "")
            if isinstance(question.get("source"), dict) else "",
            question_id)
        if not review_file.exists():
            errors.append(f"[{question_id}] 缺少独立审核记录")
        else:
            errors += review_errors(read_json(review_file), path.read_bytes(), question)
        if validation_errors:
            # 结构校验未过：派生 Markdown 的比对会因缺字段崩溃，跳过并继续审计其余题目。
            continue
        student = path.with_suffix(".md")
        if not student.exists():
            errors.append(f"[{question_id}] 缺少学员版 Markdown")
        else:
            student_text = student.read_text(encoding="utf-8")
            if student_text != generate_student_markdown(question, taxonomy):
                errors.append(f"[{question_id}] 学员版 Markdown 与 JSON 不一致（应编辑 JSON 后重新生成）")
            else:
                for marker in EDITORIAL_LEAK_MARKERS:
                    if marker in student_text:
                        errors.append(f"[{question_id}] 学员版泄漏教研标记：{marker}")
                prov = question.get("editorial_provenance", {})
                for key in ("company", "role", "round"):
                    value = prov.get(key, "unspecified")
                    if value not in ("unspecified", "") and value in student_text:
                        errors.append(f"[{question_id}] 学员版泄漏 {key}：{value}")
                for occ in prov.get("occurrences", []):
                    value = occ.get("company", "") if isinstance(occ, dict) else ""
                    if value not in ("unspecified", "") and value in student_text:
                        errors.append(f"[{question_id}] 学员版泄漏 occurrences 公司：{value}")
        editorial = bank_root / "editorial" / f"{question_id}.md"
        if not editorial.exists():
            errors.append(f"[{question_id}] 缺少教研版 Markdown")
        elif editorial.read_text(encoding="utf-8") != generate_editorial_markdown(question, taxonomy):
            errors.append(f"[{question_id}] 教研版 Markdown 与 JSON 不一致")
    for entry in catalog["questions"]:
        if not (bank_root / entry["file"]).exists():
            errors.append(f"[{entry['id']}] catalog 指向的文件不存在：{entry['file']}")

    # 只读比较索引；不在此处写盘。
    for path, text in _index_texts(bank_root, catalog, taxonomy).items():
        rel = path.relative_to(bank_root).as_posix()
        if not path.exists():
            errors.append(f"[索引] {rel} 缺失")
        elif path.read_text(encoding="utf-8") != text:
            errors.append(f"[索引] {rel} 与当前题库不一致")
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


def register_sighting(repo_root, question_id, batch_id, origin_id,
                      company="unspecified", role="unspecified",
                      round_="unspecified", seen_at=None):
    """为已入库题目登记一次新的出现（去重命中时调用）。

    门禁约定：登记前先验证审核哈希与当前文件一致；本次修改仅追加
    editorial_provenance.occurrences 与派生 frequency，知识内容不动，
    由脚本重绑审核哈希并写入 revision_history 备查。
    """
    repo_root = Path(repo_root)
    bank_root = repo_root / "question_bank"
    if not ID_RE.match(question_id or ""):
        return [f"题目 ID 不合法：{question_id!r}"]
    if not BATCH_ID_RE.match(batch_id or ""):
        return [f"batch_id 必须形如 2026-11-16-keyword-slug，实际 {batch_id!r}"]
    if not _nonempty_str(origin_id):
        return ["来源 ID（--note 或 --recall）不能为空"]
    seen_at = seen_at or batch_id[:10]
    if not DATE_RE.match(seen_at):
        return [f"seen_at 必须为 YYYY-MM-DD，实际 {seen_at!r}"]
    catalog = read_json(bank_root / "catalog.json")
    entry = next((e for e in catalog["questions"] if e.get("id") == question_id), None)
    if entry is None:
        return [f"题目未登记：{question_id}（sighting 只作用于已入库题目）"]
    question_path = bank_root / entry["file"]
    question = read_json(question_path)
    source = question.get("source") if isinstance(question.get("source"), dict) else {}
    origin_key = "recall_id" if source.get("source_type") == "student_recall" else "note_id"

    review_file = review_path(repo_root, source.get("batch_id", ""), question_id)
    if not review_file.exists():
        return [f"缺少独立审核记录：{review_file.relative_to(repo_root)}"]
    gate = review_errors(read_json(review_file), question_path.read_bytes(), question)
    if gate:
        return [f"登记前门禁未过（题目或审核记录已被改动），拒绝 sighting：{gate}"]

    prov = question.setdefault("editorial_provenance", {})
    occurrences = prov.setdefault("occurrences", [])
    for occ in occurrences:
        if isinstance(occ, dict) and occ.get("batch_id") == batch_id \
                and occ.get(origin_key) == origin_id:
            return [f"该出现已登记：{batch_id}/{origin_id}"]
    occurrences.append({
        "batch_id": batch_id,
        origin_key: origin_id,
        "company": company or "unspecified",
        "role": role or "unspecified",
        "round": round_ or "unspecified",
        "seen_at": seen_at,
    })
    prov["frequency"] = len(occurrences)

    taxonomy = load_taxonomy(bank_root / "taxonomy.json")
    errors = validate_question(question, taxonomy)
    if errors:
        return errors

    write_json(question_path, question)
    review = read_json(review_file)
    review["canonical_sha256"] = sha256_bytes(question_path.read_bytes())
    review.setdefault("revision_history", []).append({
        "at": _utc_now(),
        "note": (f"sighting 登记 {batch_id}/{origin_id}：仅追加"
                 f" editorial_provenance.occurrences 与派生 frequency，知识内容未改动"),
    })
    write_json(review_file, review)

    for i, e in enumerate(catalog["questions"]):
        if e.get("id") == question_id:
            catalog["questions"][i] = catalog_entry(question)
    catalog["generated_at"] = _utc_now()
    write_json(bank_root / "catalog.json", catalog)
    regenerate_question(bank_root, question, taxonomy)
    generate_indexes(bank_root, catalog, taxonomy)
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description="小红书面经题库管理")
    sub = parser.add_subparsers(dest="command", required=True)
    bank = sub.add_parser("question_bank")
    group = bank.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="相对 question_bank/ 的新题 JSON 路径")
    group.add_argument("--question", help="单题 ID，如 Q001（重新生成）")
    group.add_argument("--sighting", metavar="QID",
                       help="为已入库题目登记一次新的出现（教研侧 occurrences）")
    group.add_argument("--check", action="store_true", help="全量只读审计")
    group.add_argument("--all", action="store_true", help="全量重建")
    bank.add_argument("--root", default=str(REPO_ROOT), help="仓库根目录（默认脚本所属仓库）")
    bank.add_argument("--batch", help="sighting：出现所在批次 ID")
    bank.add_argument("--note", help="sighting：来源笔记 ID（xhs_note 题目）")
    bank.add_argument("--recall", help="sighting：学员口述来源 ID（student_recall 题目）")
    bank.add_argument("--company", default="unspecified", help="sighting：公司（自述）")
    bank.add_argument("--role", default="unspecified", help="sighting：岗位（自述）")
    bank.add_argument("--round", dest="round_", default="unspecified", help="sighting：轮次（自述）")
    bank.add_argument("--seen-at", dest="seen_at", default=None,
                      help="sighting：出现日期 YYYY-MM-DD（默认取批次 ID 前缀）")
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
            question_path = bank_root / entry["file"]
            question = read_json(question_path)
            source = question.get("source", {}) if isinstance(question.get("source"), dict) else {}
            review_file = review_path(repo_root, source.get("batch_id", ""),
                                      question.get("id", args.question))
            if not review_file.exists():
                errors = [f"[{args.question}] 缺少独立审核记录："
                          f"{review_file.relative_to(repo_root)}"]
            else:
                # 与登记同一道门禁：审核未过或 SHA 不匹配时拒绝重新生成。
                errors = review_errors(read_json(review_file),
                                       question_path.read_bytes(), question)
            if not errors:
                regenerate_question(bank_root, question, taxonomy)
    elif args.sighting:
        if bool(args.note) == bool(args.recall):
            errors = ["sighting 需要 --note 或 --recall 二选一"]
        else:
            errors = register_sighting(
                repo_root, args.sighting, args.batch or "",
                args.note or args.recall or "",
                company=args.company, role=args.role,
                round_=args.round_, seen_at=args.seen_at)
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
