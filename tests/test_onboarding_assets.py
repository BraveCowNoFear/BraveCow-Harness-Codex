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


if __name__ == "__main__":
    unittest.main()
