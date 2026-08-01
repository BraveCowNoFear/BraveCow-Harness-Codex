from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from harness.scripts.export_runtime_snapshot import export_snapshot, sanitize_text


class ExportRuntimeSnapshotTests(unittest.TestCase):
    def test_exports_sanitized_snapshot_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fake_home = root / "user-home"
            inventory = root / "inventory.json"
            lock = root / "lock.json"
            audit = root / "audit.md"
            output = root / "snapshot"
            inventory.write_text(
                json.dumps(
                    {
                        "generated_at": "2026-08-01T00:00:00Z",
                        "summary": {"valid_counts": {"codex": 2}},
                        "plugin_summary": {"packages": 1},
                        "entries": [{"real_path": str(fake_home / ".agents" / "skills" / "demo")}],
                    }
                ),
                encoding="utf-8",
            )
            lock.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "skills": [{"id": "demo"}],
                        "plugins": [],
                        "components": [{"id": "demo", "state": "installed"}],
                    }
                ),
                encoding="utf-8",
            )
            audit.write_text(f"Audit path: {fake_home / '.codex'}\n", encoding="utf-8")

            result = export_snapshot(inventory, lock, audit, output, home=fake_home)

            exported = (output / "skill-inventory.sanitized.json").read_text(encoding="utf-8")
            self.assertIn("%USERPROFILE%", exported)
            self.assertNotIn(str(fake_home), exported)
            self.assertEqual(result["manifest"]["lock_summary"]["skills"], 1)
            self.assertTrue((output / "checksums.json").exists())

    def test_secret_pattern_stops_export(self) -> None:
        secret = "gh" + "o_" + "abcdefghijklmnopqrstuvwxyz123456"
        with self.assertRaises(ValueError):
            sanitize_text(secret)


if __name__ == "__main__":
    unittest.main()
