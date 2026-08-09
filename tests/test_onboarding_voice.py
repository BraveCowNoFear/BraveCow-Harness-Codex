from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OnboardingVoiceTests(unittest.TestCase):
    def test_teacher_identity_and_tone_are_part_of_the_runtime_contract(self) -> None:
        skill = (ROOT / "skills/bravecow-onboarding/SKILL.md").read_text(encoding="utf-8")
        zcode_command = (ROOT / "templates/zcode/commands/bravecow-onboarding.md").read_text(encoding="utf-8")
        python_launcher = (ROOT / "harness/scripts/start_onboarding.py").read_text(encoding="utf-8")
        powershell_launcher = (ROOT / "harness/scripts/start_onboarding.ps1").read_text(encoding="utf-8")
        shell_launcher = (ROOT / "harness/scripts/start_onboarding.sh").read_text(encoding="utf-8")

        self.assertIn("Always teach as **勇敢牛牛**", skill)
        self.assertIn("patient teacher", skill)
        self.assertIn("without sounding childish", zcode_command)
        self.assertIn("勇敢牛牛", python_launcher)
        self.assertIn("teacher named by the skill", powershell_launcher)
        self.assertIn("勇敢牛牛", shell_launcher)


if __name__ == "__main__":
    unittest.main()
