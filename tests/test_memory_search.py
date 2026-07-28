from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from harness.scripts import memory_search


class MemorySearchTests(unittest.TestCase):
    def test_query_normalization_drops_router_words(self) -> None:
        normalized = memory_search.normalize_query("what changed before browser lifecycle rule")
        self.assertNotIn('"what"', normalized)
        self.assertNotIn('"before"', normalized)
        self.assertIn('"browser"', normalized)

    def test_incremental_chinese_fts_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            memories = root / "memories"
            memories.mkdir()
            db = root / "index.sqlite3"
            (memories / "ACTIVE.md").write_text(
                "# ACTIVE\n\n## 浏览器规则\n复用已登录的 Edge，不关闭用户普通窗口。\n",
                encoding="utf-8",
            )

            first = memory_search.update_index(memories, db)
            second = memory_search.update_index(memories, db)
            hits = memory_search.search("复用已登录的 Edge", db)

            self.assertEqual(first["updated"], 1)
            self.assertEqual(second["updated"], 0)
            self.assertEqual(second["unchanged"], 1)
            self.assertTrue(hits)
            self.assertEqual(hits[0].source, "ACTIVE.md")

    def test_removed_file_is_pruned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            memories = root / "memories"
            memories.mkdir()
            db = root / "index.sqlite3"
            path = memories / "LEARNINGS.md"
            path.write_text("# Learnings\n\nGraphiti is optional.\n", encoding="utf-8")
            memory_search.update_index(memories, db)
            path.unlink()
            result = memory_search.update_index(memories, db)
            self.assertEqual(result["removed"], 1)
            self.assertEqual(memory_search.search("Graphiti", db), [])


if __name__ == "__main__":
    unittest.main()
