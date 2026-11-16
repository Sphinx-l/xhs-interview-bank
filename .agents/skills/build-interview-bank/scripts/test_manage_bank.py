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
