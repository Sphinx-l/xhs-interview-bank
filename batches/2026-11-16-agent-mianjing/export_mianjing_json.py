# -*- coding: utf-8 -*-
"""导出面经数据为 douyin-data-analyze qi 分支面经 tab 的静态 JSON。

数据源：本批次 candidates.json（1014 条候选）+ manifest.json（帖子元数据）。
口径：仅 retained 帖（48 篇），排除复核撤回 3 帖；题目按帖组织、帖内按 chain_order；
status 转学员侧徽标语义（保留候选 / 与库内题重复 / 未入库）。
输出：--out 指定路径（默认写 douyin-data-analyze/web/public/data/mianjing.json）。
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

BATCH_DIR = Path(__file__).parent

BADGE = {
    "pending": "保留候选",
    "duplicate_of": "与库内题重复",
    "rejected": "未入库",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=r"C:\Users\ljq\Desktop\coco\douyin-data-analyze\web\public\data\mianjing.json",
    )
    args = parser.parse_args()

    with open(BATCH_DIR / "manifest.json", encoding="utf-8") as f:
        manifest = {n["note_id"]: n for n in json.load(f)["notes"]}

    with open(BATCH_DIR / "candidates.json", encoding="utf-8") as f:
        candidates = json.load(f)["candidates"]

    posts = {}
    for cand in candidates:
        note_id = cand["note_id"]
        meta = manifest.get(note_id)
        if meta is None or meta.get("status") != "retained":
            continue  # 复核撤回帖不进学员侧
        post = posts.setdefault(
            note_id,
            {
                "noteId": note_id,
                "title": meta.get("title") or "(无标题)",
                "company": cand.get("company") or "unspecified",
                "role": cand.get("role") or "unspecified",
                "round": cand.get("round") or "unspecified",
                "questions": [],
            },
        )
        post["questions"].append(
            {
                "order": cand["chain_order"],
                "text": cand["question_verbatim"],
                "status": cand["status"],
                "badge": BADGE[cand["status"]],
            }
        )

    post_list = sorted(
        posts.values(),
        key=lambda p: (p["company"] != "unspecified", p["company"], p["noteId"]),
    )
    for post in post_list:
        post["questions"].sort(key=lambda q: q["order"])
        post["questionCount"] = len(post["questions"])

    all_questions = [q for p in post_list for q in p["questions"]]
    companies = Counter(p["company"] for p in post_list)
    payload = {
        "source": "xhs-interview-bank · 批次 2026-11-16-agent-mianjing",
        "generatedAt": "2026-11-18",
        "notice": "公司/岗位/轮次均为发帖人自述，未核实；题目为面经原文逐题转录（含未入库题）。",
        "stats": {
            "postCount": len(post_list),
            "questionCount": len(all_questions),
            "statusCounts": dict(Counter(q["status"] for q in all_questions)),
            "companyCounts": dict(sorted(companies.items(), key=lambda kv: -kv[1])),
        },
        "posts": post_list,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("posts:", len(post_list), "questions:", len(all_questions))
    print("status:", dict(Counter(q["status"] for q in all_questions)))
    print("written:", out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
