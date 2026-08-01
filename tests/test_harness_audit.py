from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from harness.scripts.harness_audit import classify_automation, collect_automations


class HarnessAutomationAuditTests(unittest.TestCase):
    def test_known_harness_automations_have_explicit_roles(self) -> None:
        monthly = classify_automation("bravecow-harness")
        global_rag = classify_automation("session-log-graphiti-sync")

        self.assertTrue(monthly["harness_component"])
        self.assertEqual(monthly["role"], "continuous-technology-evolution")
        self.assertTrue(global_rag["harness_component"])
        self.assertEqual(global_rag["role"], "global-memory-rag-index")

    def test_collection_reports_metadata_without_exposing_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            automation = root / "session-log-graphiti-sync"
            automation.mkdir()
            (automation / "automation.toml").write_text(
                'name = "Global memory sync"\n'
                'status = "ACTIVE"\n'
                'prompt = "private prompt with secret-sentinel"\n',
                encoding="utf-8",
            )

            result = collect_automations(root)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "session-log-graphiti-sync")
        self.assertEqual(result[0]["status"], "ACTIVE")
        self.assertTrue(result[0]["harness_component"])
        self.assertNotIn("prompt", result[0])
        self.assertNotIn("secret-sentinel", repr(result))

    def test_workspace_graphiti_index_is_a_managed_extension(self) -> None:
        result = classify_automation("project-index", "Sync workspace Markdown into Graphiti RAG group_id")

        self.assertTrue(result["harness_component"])
        self.assertEqual(result["boundary"], "managed-extension")

    def test_unrelated_automation_remains_external(self) -> None:
        result = classify_automation("email-briefing", "Summarize recent email")

        self.assertFalse(result["harness_component"])
        self.assertEqual(result["boundary"], "external")


if __name__ == "__main__":
    unittest.main()
