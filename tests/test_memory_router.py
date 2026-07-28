from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.scripts import memory_router


class MemoryRouterTests(unittest.TestCase):
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

    def test_graph_failure_falls_back_well_under_five_seconds(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_dir, db = self.make_memory(Path(temp_dir))
            started = time.perf_counter()
            with patch.object(memory_router, "graphiti_ports_ready", return_value=False):
                payload = memory_router.route_memory("what changed before browser setup", memory_dir, db)
            elapsed = time.perf_counter() - started
            self.assertEqual(payload["decision"]["requested"], "graph")
            self.assertEqual(payload["decision"]["resolved"], "fts")
            self.assertTrue(payload["decision"]["degraded"])
            self.assertLess(elapsed, 5)

    def test_semantic_query_uses_local_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_dir, db = self.make_memory(Path(temp_dir))
            payload = memory_router.route_memory("why is browser lifecycle useful", memory_dir, db)
            self.assertEqual(payload["decision"]["requested"], "semantic")
            self.assertEqual(payload["decision"]["resolved"], "fts")


if __name__ == "__main__":
    unittest.main()
