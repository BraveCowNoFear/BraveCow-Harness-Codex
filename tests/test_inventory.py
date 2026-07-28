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
            self.assertTrue(entries[0].resolved)
            self.assertEqual(entries[0].state, "resolved-config")

    def test_remote_install_marker_supersedes_legacy_config_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = Path(temp_dir)
            legacy = cache / "openai-curated" / "github" / "old"
            remote = cache / "openai-curated-remote" / "github" / "0.1.8"
            for package, version in ((legacy, "0.1.6"), (remote, "0.1.8")):
                manifest_dir = package / ".codex-plugin"
                manifest_dir.mkdir(parents=True)
                (manifest_dir / "plugin.json").write_text(
                    json.dumps({"name": "github", "version": version}), encoding="utf-8"
                )
            (remote.parent / ".codex-remote-plugin-install.json").write_text(
                json.dumps({"schema_version": 1, "remote_plugin_id": "plugin_remote_github"}),
                encoding="utf-8",
            )
            original_cache = inventory.CODEX_PLUGIN_CACHE
            try:
                inventory.CODEX_PLUGIN_CACHE = cache
                entries = inventory.discover_plugin_entries({"github@openai-curated"})
            finally:
                inventory.CODEX_PLUGIN_CACHE = original_cache

            resolved = next(item for item in entries if item.resolved)
            legacy_entry = next(item for item in entries if item.cache_source == "openai-curated")
            self.assertEqual(resolved.version, "0.1.8")
            self.assertEqual(resolved.state, "resolved-remote-install")
            self.assertEqual(resolved.remote_plugin_id, "plugin_remote_github")
            self.assertEqual(legacy_entry.state, "superseded-config-cache")

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
            self.assertEqual(lock["schema_version"], 2)
            self.assertEqual(len(lock["skills"]), 1)
            self.assertEqual(lock["skills"][0]["runtimes"], ["codex", "shared"])
            self.assertTrue(lock["skills"][0]["rollback"]["ref"])
            self.assertIn("verification", lock["skills"][0])


if __name__ == "__main__":
    unittest.main()
