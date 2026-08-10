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

        self.assertIn("Teach as **勇敢牛牛**", skill)
        self.assertIn("technically honest", skill)
        self.assertIn("adaptive course", zcode_command)
        self.assertIn("勇敢牛牛", python_launcher)
        self.assertIn("teacher named by the skill", powershell_launcher)
        self.assertIn("勇敢牛牛", shell_launcher)

    def test_normal_lessons_have_a_concise_language_budget(self) -> None:
        skill = (ROOT / "skills/bravecow-onboarding/SKILL.md").read_text(encoding="utf-8")
        zcode_command = (ROOT / "templates/zcode/commands/bravecow-onboarding.md").read_text(encoding="utf-8")
        python_launcher = (ROOT / "harness/scripts/start_onboarding.py").read_text(encoding="utf-8")

        self.assertIn("at most five short sentences", skill)
        self.assertIn("Use one example and one question", skill)
        self.assertIn("Give the short answer first", skill)
        self.assertIn("provide a sample answer unless", skill)
        self.assertIn("Keep it concise", zcode_command)
        self.assertNotIn("use everyday or business examples", python_launcher)

    def test_course_is_generated_from_the_learner_profile(self) -> None:
        skill = (ROOT / "skills/bravecow-onboarding/SKILL.md").read_text(encoding="utf-8")
        curriculum = (ROOT / "skills/bravecow-onboarding/references/curriculum.md").read_text(encoding="utf-8")
        python_launcher = (ROOT / "harness/scripts/start_onboarding.py").read_text(encoding="utf-8")

        self.assertIn("ask what the learner studies or does", skill)
        self.assertIn("Build a working learner profile", skill)
        self.assertIn("not a fixed syllabus", skill)
        self.assertIn("use accurate engineering language", skill)
        self.assertIn("must never replace it", skill)
        self.assertNotIn("Follow the 12 lessons", skill)
        self.assertNotIn("Use only general-life or business examples", skill)
        self.assertIn("这不是固定课表", curriculum)
        self.assertIn("底层机制", curriculum)
        self.assertIn("专业或工作、目标和经验", python_launcher)


if __name__ == "__main__":
    unittest.main()
