from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from harness.scripts import build_skill_inventory as inventory

class InventoryTests(unittest.TestCase):
    def test_multiline_frontmatter_description(self) -> None:
        name, description = inventory.parse_frontmatter(
            "---\nname: example\ndescription: |\n  First line.\n  Second line.\n---\n"
        )
        self.assertEqual(name, "example")
        self.assertEqual(description, "First line. Second line.")

    def test_discovers_cached_plugin_and_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = Path(temp_dir)
            package = cache / "test-source" / "sample-plugin" / "1.2.3"
            manifest_dir = package / ".codex-plugin"
            skill_dir = package / "skills" / "sample-skill"
            manifest_dir.mkdir(parents=True)
            skill_dir.mkdir(parents=True)
            (manifest_dir / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "sample-plugin",
                        "version": "1.2.3",
                        "skills": "./skills/",
                        "apps": "./.app.json",
                    }
                ),
                encoding="utf-8",
            )
            (skill_dir / "SKILL.md").write_text("---\nname: sample-skill\n---\n", encoding="utf-8")

            original_cache = inventory.CODEX_PLUGIN_CACHE
            try:
                inventory.CODEX_PLUGIN_CACHE = cache
                entries = inventory.discover_plugin_entries()
            finally:
                inventory.CODEX_PLUGIN_CACHE = original_cache

            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].cache_source, "test-source")
            self.assertEqual(entries[0].skill_ids, ["sample-skill"])
            self.assertTrue(entries[0].has_apps)
            self.assertFalse(entries[0].has_mcp)


if __name__ == "__main__":
    unittest.main()
