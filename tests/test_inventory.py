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
                entries = inventory.discover_plugin_entries({"sample-plugin@test-source"})
            finally:
                inventory.CODEX_PLUGIN_CACHE = original_cache

            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].cache_source, "test-source")
            self.assertEqual(entries[0].skill_ids, ["sample-skill"])
            self.assertTrue(entries[0].has_apps)
            self.assertFalse(entries[0].has_mcp)
            self.assertTrue(entries[0].enabled_by_config)
            self.assertEqual(entries[0].state, "enabled-by-config")

    def test_build_lock_deduplicates_runtime_mirrors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("---\nname: sample\nversion: 1.0.0\n---\n", encoding="utf-8")
            digest = inventory.sha256_file(skill_md)
            entries = [
                inventory.SkillEntry(
                    runtime=runtime,
                    skill_id="sample",
                    path=str(skill_dir),
                    real_path=str(skill_dir.resolve()),
                    is_link=runtime != "shared",
                    link_target=[str(skill_dir.resolve())] if runtime != "shared" else [],
                    has_skill_md=True,
                    name="sample",
                    description=None,
                    declared_version="1.0.0",
                    content_sha256=digest,
                    state="discoverable",
                )
                for runtime in ("shared", "codex")
            ]
            lock = inventory.build_lock(entries, [], "2026-01-01T00:00:00Z")
            self.assertEqual(len(lock["skills"]), 1)
            self.assertEqual(lock["skills"][0]["runtimes"], ["codex", "shared"])


if __name__ == "__main__":
    unittest.main()
