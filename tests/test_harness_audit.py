from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from harness.scripts import harness_audit
from harness.scripts.harness_audit import classify_automation, collect_automations


class HarnessAutomationAuditTests(unittest.TestCase):
    def test_managed_external_vendor_sources_are_not_quarantine_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vendor_dir = Path(temp_dir)
            (vendor_dir / "windows-computer-use").mkdir()
            (vendor_dir / "unknown-source").mkdir()
            original_vendor_dir = harness_audit.VENDOR_DIR
            try:
                harness_audit.VENDOR_DIR = vendor_dir
                missing = harness_audit.collect_unmanifested_vendor_dirs(
                    {"components": {"windows-computer-use": {"kind": "plugin"}}}
                )
            finally:
                harness_audit.VENDOR_DIR = original_vendor_dir

        self.assertEqual(missing, ["unknown-source"])

    def test_known_harness_automations_have_explicit_roles(self) -> None:
        monthly = classify_automation("bravecow-harness")
        global_rag = classify_automation("memory-tidy")

        self.assertTrue(monthly["harness_component"])
        self.assertEqual(monthly["role"], "continuous-technology-evolution")
        self.assertTrue(global_rag["harness_component"])
        self.assertEqual(global_rag["role"], "durable-memory-maintenance")

    def test_collection_reports_metadata_without_exposing_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            automation = root / "memory-tidy"
            automation.mkdir()
            (automation / "automation.toml").write_text(
                'name = "Global memory sync"\n'
                'status = "ACTIVE"\n'
                'prompt = "private prompt with secret-sentinel"\n',
                encoding="utf-8",
            )

            result = collect_automations(root)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "memory-tidy")
        self.assertEqual(result[0]["status"], "ACTIVE")
        self.assertTrue(result[0]["harness_component"])
        self.assertNotIn("prompt", result[0])
        self.assertNotIn("secret-sentinel", repr(result))

    def test_unknown_index_is_external(self) -> None:
        result = classify_automation("project-index", "Sync workspace Markdown into a private index")

        self.assertFalse(result["harness_component"])
        self.assertEqual(result["boundary"], "external")

    def test_unrelated_automation_remains_external(self) -> None:
        result = classify_automation("email-briefing", "Summarize recent email")

        self.assertFalse(result["harness_component"])
        self.assertEqual(result["boundary"], "external")


if __name__ == "__main__":
    unittest.main()
