from __future__ import annotations

import tempfile
import sqlite3
import time
import unittest
from unittest.mock import patch
from pathlib import Path

from harness.scripts import memory_router


class MemoryRouterTests(unittest.TestCase):
    def test_locked_index_has_bounded_degradation_latency(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory, db = self.make_memory(Path(temp_dir))
            memory_router.route_memory("browser", memory, db)
            connection = sqlite3.connect(db)
            try:
                connection.execute("BEGIN IMMEDIATE")
                (memory / "NEW.md").write_text("# New\nbrowser new rule", encoding="utf-8")
                started = time.perf_counter()
                result = memory_router.route_memory("browser", memory, db)
                self.assertLess(time.perf_counter() - started, 1.5)
                self.assertEqual(result["decision"]["resolved"], "markdown-scan")
                self.assertTrue(result["evidence"])
            finally:
                connection.rollback()
                connection.close()

    def test_invalid_encoding_degrades_without_polluting_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory, db = self.make_memory(Path(temp_dir))
            (memory / "BAD.md").write_bytes(b"browser\xff")
            result = memory_router.route_memory("browser", memory, db)
            self.assertEqual(result["decision"]["resolved"], "markdown-scan")
            self.assertEqual(result["index"]["error_type"], "UnicodeDecodeError")
            self.assertEqual(result["index"]["fallback"]["skipped_files"], 1)

    def test_direct_does_not_open_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory, db = self.make_memory(Path(temp_dir))
            with patch.object(memory_router, "update_index", side_effect=AssertionError("must not index")):
                result = memory_router.route_memory("browser", memory, db, source="ACTIVE.md")
            self.assertEqual(result["index"]["status"], "skipped-direct")
            self.assertFalse(db.exists())

    def test_corrupt_index_degrades_without_replacing_database(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory, db = self.make_memory(Path(temp_dir))
            db.write_bytes(b"corrupt-index-sentinel")
            result = memory_router.route_memory("browser", memory, db, max_chars=40)
            self.assertEqual(result["decision"]["resolved"], "markdown-scan")
            self.assertTrue(result["evidence"])
            self.assertLessEqual(result["evidence_chars"], 40)
            self.assertEqual(db.read_bytes(), b"corrupt-index-sentinel")

    def test_short_chinese_fallback_and_empty_query(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory, db = self.make_memory(Path(temp_dir))
            (memory / "ZH.md").write_text("# 规则\n记忆来自 Markdown。", encoding="utf-8")
            result = memory_router.route_memory("记忆", memory, db)
            self.assertEqual(result["decision"]["resolved"], "markdown-scan")
            self.assertEqual(result["evidence"][0]["source"], "ZH.md")
            self.assertEqual(memory_router.route_memory("", memory, db)["evidence"], [])

    def test_missing_memory_root_preserves_database(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory, db = self.make_memory(Path(temp_dir))
            memory_router.route_memory("browser", memory, db)
            from harness.scripts.memory_search import search, update_index
            with self.assertRaises(FileNotFoundError):
                update_index(memory / "absent", db)
            self.assertTrue(search("browser", db))

    def test_fallback_skips_invalid_utf8_and_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            memory, db = self.make_memory(root)
            (memory / "BAD.md").write_bytes(b"browser\xff")
            (root / "OUTSIDE.md").write_text("secret", encoding="utf-8")
            self.assertEqual(memory_router.direct_evidence(memory, "../OUTSIDE.md", 100), [])
            hits, stats = memory_router.markdown_fallback("browser", memory, 6, 100)
            self.assertEqual(stats["skipped_files"], 1)
            self.assertEqual([h["source"] for h in hits], ["ACTIVE.md"])

    def make_memory(self, root: Path) -> tuple[Path, Path]:
        memory_dir = root / "memories"
        memory_dir.mkdir()
        (memory_dir / "ACTIVE.md").write_text(
            "# ACTIVE\n\nBrowser lifecycle requires closing only task-owned tabs.\n", encoding="utf-8"
        )
        return memory_dir, root / "memory.sqlite3"

    def test_direct_source_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_dir, db = self.make_memory(Path(temp_dir))
            payload = memory_router.route_memory(
                "browser", memory_dir, db, source="ACTIVE.md", max_chars=32
            )
            self.assertEqual(payload["decision"]["resolved"], "direct")
            self.assertLessEqual(payload["evidence_chars"], 32)

    def test_temporal_query_uses_local_evidence_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_dir, db = self.make_memory(Path(temp_dir))
            started = time.perf_counter()
            payload = memory_router.route_memory("what changed before browser setup", memory_dir, db)
            elapsed = time.perf_counter() - started
            self.assertEqual(payload["decision"]["requested"], "fts")
            self.assertEqual(payload["decision"]["resolved"], "fts")
            self.assertFalse(payload["decision"]["degraded"])
            self.assertTrue(payload["evidence"])
            self.assertLess(elapsed, 5)

    def test_semantic_query_uses_local_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_dir, db = self.make_memory(Path(temp_dir))
            payload = memory_router.route_memory("why is browser lifecycle useful", memory_dir, db)
            self.assertEqual(payload["decision"]["requested"], "semantic")
            self.assertEqual(payload["decision"]["resolved"], "fts")


if __name__ == "__main__":
    unittest.main()
