from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

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

    def test_priority_uses_legacy_fast_alias_for_stale_bundled_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.toml"
            path.write_text('service_tier = "priority"\n', encoding="utf-8")
            responses = [
                SimpleNamespace(returncode=0, stdout="codex-cli 0.130.0-alpha.5\n", stderr=""),
                SimpleNamespace(
                    returncode=1,
                    stdout="",
                    stderr="unknown variant `priority`, expected `fast` or `flex`",
                ),
                SimpleNamespace(returncode=0, stdout="features\n", stderr=""),
            ]
            with patch.object(config_gate.shutil, "which", return_value="codex"), patch.object(
                config_gate.subprocess, "run", side_effect=responses
            ) as run:
                result = config_gate.check_config(path, run_runtime=True)

            self.assertEqual(result["overall"], "pass")
            self.assertEqual(result["runtime"], "pass-legacy-fast-alias")
            self.assertEqual(result["compatibility_service_tier"], "fast")
            self.assertIn('service_tier="fast"', run.call_args_list[-1].args[0])


if __name__ == "__main__":
    unittest.main()
