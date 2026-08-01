from __future__ import annotations

import unittest

from harness.scripts.skill_contracts import evaluate_contracts


class SkillContractTests(unittest.TestCase):
    def test_positive_negative_and_description_contract(self) -> None:
        inventory = {
            "entries": [
                {"skill_id": "alpha", "has_skill_md": True, "description": "Handles alpha reports."},
                {"skill_id": "beta", "has_skill_md": True, "description": "Handles beta exports."},
            ],
            "plugin_skills": [
                {
                    "catalog_id": "plugin:gamma",
                    "description": "Handles gamma automation.",
                }
            ],
        }
        suite = {
            "schema_version": 1,
            "max_failure_percent": 0,
            "contracts": [
                {"skill_id": "alpha", "description_any": ["report"], "positive_patterns": ["alpha report"]},
                {"skill_id": "beta", "description_any": ["export"], "positive_patterns": ["beta export"]},
                {
                    "skill_id": "plugin:gamma",
                    "description_any": ["automation"],
                    "positive_patterns": ["gamma automation"],
                },
            ],
            "cases": [
                {"prompt": "Make an alpha report", "expected": ["alpha"]},
                {"prompt": "Write a poem", "expected": []},
                {"prompt": "Run gamma automation", "expected": ["plugin:gamma"]},
            ],
        }
        result = evaluate_contracts(inventory, suite)
        self.assertTrue(result["passed"])
        self.assertEqual(result["failure_percent"], 0)


if __name__ == "__main__":
    unittest.main()
