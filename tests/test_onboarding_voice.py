from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills/bravecow-onboarding"


class OnboardingVoiceTests(unittest.TestCase):
    def test_teacher_identity_and_spoken_copy_are_runtime_contracts(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        spoken = (SKILL_ROOT / "references/spoken-copy.md").read_text(encoding="utf-8")

        self.assertIn("Teach as **勇敢牛牛**", skill)
        self.assertIn("spoken Chinese", skill)
        self.assertIn("像老师坐在旁边当场说出来", spoken)
        self.assertIn("现在做什么", spoken)
        self.assertIn("看到什么算成功", spoken)
        self.assertIn("如果读起来像说明书", spoken)

    def test_first_lesson_offers_project_and_principles_routes(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        route = (SKILL_ROOT / "references/route-builder.md").read_text(encoding="utf-8")
        personalization = (SKILL_ROOT / "references/project-personalization.md").read_text(encoding="utf-8")

        self.assertIn("带真实项目学习", skill)
        self.assertIn("暂时不定项目，只熟悉软件与背后原理", skill)
        self.assertIn("Never require a project idea before teaching", skill)
        self.assertIn("第二条路线不得继续追问项目需求", personalization)
        self.assertIn("不发问卷", route)
        self.assertIn("Do not manufacture a capstone project", skill)

    def test_normal_lessons_stay_short_and_actionable(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        lesson_loop = (SKILL_ROOT / "references/lesson-loop.md").read_text(encoding="utf-8")

        self.assertIn("at most five short sentences", skill)
        self.assertIn("one direct action", skill)
        self.assertIn("一轮只要求一个动作", lesson_loop)
        self.assertIn("先别重复点", (SKILL_ROOT / "references/spoken-copy.md").read_text(encoding="utf-8"))

    def test_launchers_request_dual_route_spoken_onboarding(self) -> None:
        paths = [
            ROOT / "harness/scripts/start_onboarding.py",
            ROOT / "harness/scripts/start_onboarding.ps1",
            ROOT / "harness/scripts/start_onboarding.sh",
            ROOT / "templates/zcode/commands/bravecow-onboarding.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)

        self.assertIn("拿真实项目边做边学", combined)
        self.assertIn("不定项目、只熟悉软件和背后原理", combined)
        self.assertIn("natural spoken", combined)
        self.assertIn("对应红圈图", combined)
        self.assertIn("matching screenshot before the click instruction", combined)
        self.assertNotIn("第一条回复先问我的专业或工作、目标和经验", combined)

    def test_course_is_adaptive_and_has_no_course_map(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        curriculum = (SKILL_ROOT / "references/curriculum.md").read_text(encoding="utf-8")
        visuals = (SKILL_ROOT / "references/ui-visual-coverage.md").read_text(encoding="utf-8")

        self.assertIn("learning-outcome pool", skill)
        self.assertIn("这不是固定课表", curriculum)
        self.assertIn("不做封面、地图或图片轮播", visuals)
        self.assertNotIn("00-course-map", visuals)
        self.assertFalse((SKILL_ROOT / "assets/ui/shared/00-course-map.png").exists())


if __name__ == "__main__":
    unittest.main()
