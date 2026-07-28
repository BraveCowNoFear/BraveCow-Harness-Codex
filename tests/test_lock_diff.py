from __future__ import annotations

import unittest

from harness.scripts.lock_diff import diff_locks


class LockDiffTests(unittest.TestCase):
    def test_reports_added_removed_and_changed(self) -> None:
        before = {
            "schema_version": 1,
            "skills": [{"id": "a", "real_path": "a", "content_sha256": "old"}, {"id": "b", "real_path": "b"}],
            "plugins": [],
            "components": [],
        }
        after = {
            "schema_version": 2,
            "skills": [{"id": "a", "real_path": "a", "content_sha256": "new"}, {"id": "c", "real_path": "c"}],
            "plugins": [],
            "components": [],
        }
        result = diff_locks(before, after)
        self.assertEqual(result["sections"]["skills"]["added"], ["c"])
        self.assertEqual(result["sections"]["skills"]["removed"], ["b"])
        self.assertEqual(result["sections"]["skills"]["changed"], ["a"])
        self.assertEqual(result["total_changes"], 3)


if __name__ == "__main__":
    unittest.main()
