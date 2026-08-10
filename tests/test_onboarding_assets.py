from __future__ import annotations

import re
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills/bravecow-onboarding"
VISUALS = SKILL_ROOT / "references/ui-visual-coverage.md"


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"invalid PNG header: {path}")
    return struct.unpack(">II", header[16:24])


class OnboardingAssetTests(unittest.TestCase):
    def test_every_manifest_asset_exists_and_decodes(self) -> None:
        manifest = VISUALS.read_text(encoding="utf-8")
        refs = sorted(set(re.findall(r"assets/ui/[a-z0-9_./-]+\.png", manifest)))

        self.assertGreaterEqual(len(refs), 32)
        for ref in refs:
            path = SKILL_ROOT / ref
            self.assertTrue(path.is_file(), ref)
            width, height = png_dimensions(path)
            self.assertGreaterEqual(width, 800, ref)
            self.assertGreaterEqual(height, 700, ref)

    def test_assets_are_split_by_runtime_and_raw_images_are_not_packaged(self) -> None:
        self.assertEqual(len(list((SKILL_ROOT / "assets/ui/codex").glob("*.png"))), 15)
        self.assertEqual(len(list((SKILL_ROOT / "assets/ui/zcode").glob("*.png"))), 14)
        self.assertEqual(len(list((SKILL_ROOT / "assets/ui/shared").glob("*.png"))), 3)
        raw = SKILL_ROOT / "assets/ui/raw"
        self.assertFalse(raw.exists() and any(raw.iterdir()))

    def test_manifest_preserves_real_ui_and_privacy_rules(self) -> None:
        manifest = VISUALS.read_text(encoding="utf-8")
        self.assertIn("单个粗红圈", manifest)
        self.assertIn("原始截图必须保存在课程 Skill 目录之外", manifest)
        self.assertIn("Codex 图片来自 Codex，ZCode 图片来自 ZCode", manifest)
        self.assertIn("不做封面、地图或图片轮播", manifest)

    def test_ui_location_answers_have_a_hard_visual_gate(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        manifest = VISUALS.read_text(encoding="utf-8")
        spoken = (SKILL_ROOT / "references/spoken-copy.md").read_text(encoding="utf-8")

        self.assertIn("mandatory gate", skill)
        self.assertIn("before the teaching text", skill)
        self.assertIn("A file path, clickable file link, verbal description", skill)
        self.assertIn("Markdown 图片语法直接嵌入聊天", manifest)
        self.assertIn("图片单独占一行，并放在点击说明之前", manifest)
        self.assertIn("文件存在不等于已经发给用户", manifest)
        self.assertIn("只有路径、链接或“我去查一下”都不算发图", spoken)


if __name__ == "__main__":
    unittest.main()
