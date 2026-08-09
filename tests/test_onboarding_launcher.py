from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OnboardingLauncherTests(unittest.TestCase):
    def test_codex_app_server_creates_thread_and_turn(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            receipt = temp / "last-launch.json"
            command = [
                sys.executable,
                str(ROOT / "harness/scripts/start_onboarding.py"),
                "--executable",
                sys.executable,
                "--executable-arg",
                str(ROOT / "tests/fake_codex_app_server.py"),
                "--workspace",
                str(temp),
                "--skill-path",
                str(ROOT / "skills/bravecow-onboarding/SKILL.md"),
                "--receipt",
                str(receipt),
                "--timeout",
                "10",
            ]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=20)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "started")
            self.assertEqual(payload["thread_id"], "thread-test-123")
            self.assertEqual(payload["turn_id"], "turn-test-456")


if __name__ == "__main__":
    unittest.main()
