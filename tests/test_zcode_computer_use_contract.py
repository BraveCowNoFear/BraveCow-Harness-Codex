from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ZCodeComputerUseContractTests(unittest.TestCase):
    def test_external_source_is_immutable_and_scoped(self) -> None:
        lock = json.loads(
            (ROOT / "harness/catalog/external-components.lock.json").read_text(encoding="utf-8")
        )
        component = lock["components"]["desktop-control-for-windows"]
        self.assertEqual(
            component["repository"],
            "https://github.com/BraveCowNoFear/desktop-control-for-windows.git",
        )
        self.assertRegex(component["commit"], re.compile(r"^[0-9a-f]{40}$"))
        self.assertEqual(component["platforms"], ["windows"])
        self.assertEqual(component["runtimes"], ["zcode"])

    def test_zcode_adapter_and_installer_contract(self) -> None:
        adapter = (
            ROOT / "templates/zcode/skills/bravecow-windows-computer-use/SKILL.md"
        ).read_text(encoding="utf-8")
        interface = (
            ROOT / "templates/zcode/skills/bravecow-windows-computer-use/agents/openai.yaml"
        ).read_text(encoding="utf-8")
        installer = (ROOT / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("name: bravecow-windows-computer-use", adapter)
        self.assertIn("does not require ZCode to provide a delegation", adapter)
        self.assertIn("$bravecow-windows-computer-use", interface)
        self.assertNotIn("$desktop-control-for-windows", interface)
        self.assertIn("function Install-ZCodeComputerUse", installer)
        self.assertIn("SkipZCodeComputerUse", installer)
        self.assertIn("ZCodeComputerUseSource", installer)
        self.assertIn("zcode-computer-use-install.json", installer)

    def test_course_uses_a_safe_real_plugin_example(self) -> None:
        lesson = (
            ROOT / "skills/bravecow-onboarding/references/zcode-computer-use-plugin.md"
        ).read_text(encoding="utf-8")
        self.assertIn("BraveCowNoFear/desktop-control-for-windows", lesson)
        self.assertIn("Windows + ZCode", lesson)
        self.assertIn("macOS + ZCode", lesson)
        self.assertIn("--help", lesson)
        self.assertNotIn("status --windows", lesson)
        self.assertIn("不在新手课中自动截图", lesson)


if __name__ == "__main__":
    unittest.main()
