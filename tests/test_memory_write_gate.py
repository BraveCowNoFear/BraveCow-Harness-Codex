from __future__ import annotations

import unittest

from harness.scripts.memory_write_gate import validate_candidate


class MemoryWriteGateTests(unittest.TestCase):
    def candidate(self) -> dict:
        return {
            "content": "Use the already logged-in Edge target and close only task-owned tabs.",
            "reusable": True,
            "source": "validated browser end-to-end test",
            "scope": "global",
            "target": "LEARNINGS.md",
            "confidence": 0.95,
            "expires_at": None,
            "conflicts": [],
        }

    def test_accepts_complete_reusable_candidate_without_writing(self) -> None:
        result = validate_candidate(self.candidate())
        self.assertEqual(result["decision"], "accept")
        self.assertFalse(result["write_performed"])

    def test_rejects_secret_and_missing_provenance(self) -> None:
        candidate = self.candidate()
        candidate["content"] = "api_key=" + "sk-" + "abcdefghijklmnopqrstuvwxyz123456"
        candidate["source"] = ""
        result = validate_candidate(candidate)
        self.assertEqual(result["decision"], "reject")
        self.assertIn("possible-secret", result["errors"])
        self.assertIn("source-required", result["errors"])

    def test_conflict_requires_review(self) -> None:
        candidate = self.candidate()
        candidate["conflicts"] = ["ACTIVE.md: browser rule"]
        result = validate_candidate(candidate)
        self.assertEqual(result["decision"], "review")


if __name__ == "__main__":
    unittest.main()
