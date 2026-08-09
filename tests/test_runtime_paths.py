from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimePathTests(unittest.TestCase):
    def test_environment_overrides_are_shared_across_runtimes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            environment = os.environ.copy()
            environment.update(
                {
                    "BRAVECOW_HOME": str(base / "shared"),
                    "CODEX_HOME": str(base / "codex"),
                    "ZCODE_HOME": str(base / "zcode"),
                    "SHARED_SKILLS_HOME": str(base / "skills"),
                }
            )
            script = (
                "import json,sys; "
                f"sys.path.insert(0, {str(ROOT / 'harness/scripts')!r}); "
                "import runtime_paths as r; "
                "print(json.dumps({'harness': str(r.HARNESS_HOME), 'memory': str(r.MEMORY_HOME), "
                "'codex': str(r.RUNTIME_SKILL_ROOTS['codex']), 'zcode': str(r.RUNTIME_SKILL_ROOTS['zcode'])}))"
            )
            completed = subprocess.run([sys.executable, "-c", script], env=environment, capture_output=True, text=True, check=True)
            payload = json.loads(completed.stdout)
            self.assertEqual(Path(payload["harness"]), base / "shared/harness")
            self.assertEqual(Path(payload["memory"]), base / "shared/memories")
            self.assertEqual(Path(payload["codex"]), base / "codex/skills")
            self.assertEqual(Path(payload["zcode"]), base / "zcode/skills")


if __name__ == "__main__":
    unittest.main()
