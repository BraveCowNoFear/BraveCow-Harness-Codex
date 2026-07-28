from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from harness.scripts import config_gate


class ConfigGateTests(unittest.TestCase):
    def test_valid_toml_without_runtime_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.toml"
            path.write_text('service_tier = "default"\n', encoding="utf-8")
            result = config_gate.check_config(path, run_runtime=False)
            self.assertEqual(result["syntax"], "pass")
            self.assertEqual(result["overall"], "pass")
            self.assertEqual(result["service_tier"], "default")

    def test_invalid_toml_fails_syntax_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.toml"
            path.write_text('service_tier = "unterminated\n', encoding="utf-8")
            result = config_gate.check_config(path, run_runtime=False)
            self.assertEqual(result["syntax"], "fail")
            self.assertEqual(result["overall"], "fail")


if __name__ == "__main__":
    unittest.main()
