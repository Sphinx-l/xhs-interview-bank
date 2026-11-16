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
