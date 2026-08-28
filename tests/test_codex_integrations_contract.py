from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "harness/scripts/manage_codex_plugin.py"


class CodexIntegrationContractTests(unittest.TestCase):
    def test_external_sources_are_immutable_and_scoped(self) -> None:
        lock = json.loads(
            (ROOT / "harness/catalog/external-components.lock.json").read_text(
                encoding="utf-8"
            )
        )
        browser = lock["components"]["browser-harness"]
        self.assertEqual(browser["version"], "0.1.8")
        self.assertRegex(browser["commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(browser["runtimes"], ["codex", "zcode"])

        windows = lock["components"]["windows-computer-use"]
        self.assertEqual(windows["version"], "0.39.0")
        self.assertRegex(windows["commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(windows["platforms"], ["windows"])
        self.assertEqual(windows["runtimes"], ["codex"])
        self.assertEqual(
            windows["plugin_id"],
            "windows-computer-use@brave-cow-windows-tools",
        )

    def test_manager_preserves_an_existing_development_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            development_source = root / "development marketplace"
            pinned_source = root / "pinned marketplace"
            development_source.mkdir()
            pinned_source.mkdir()
            config = root / "config.toml"
            config.write_text(
                "service_tier = \"default\"\n\n"
                "[marketplaces.brave-cow-windows-tools]\n"
                "source_type = \"local\"\n"
                f"source = {json.dumps(str(development_source))}\n\n"
                '[plugins."windows-computer-use@brave-cow-windows-tools"]\n'
                "enabled = false\n\n"
                "[desktop]\nappearance = \"system\"\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    str(MANAGER),
                    "--config",
                    str(config),
                    "--marketplace-source",
                    str(pinned_source),
                    "--preserve-existing-source",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            parsed = tomllib.loads(config.read_text(encoding="utf-8"))
            self.assertEqual(
                parsed["marketplaces"]["brave-cow-windows-tools"]["source"],
                str(development_source),
            )
            self.assertTrue(
                parsed["plugins"]["windows-computer-use@brave-cow-windows-tools"][
                    "enabled"
                ]
            )
            self.assertEqual(parsed["desktop"]["appearance"], "system")

    def test_manager_creates_a_valid_fresh_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "marketplace"
            source.mkdir()
            config = root / "config.toml"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(MANAGER),
                    "--config",
                    str(config),
                    "--marketplace-source",
                    str(source),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            parsed = tomllib.loads(config.read_text(encoding="utf-8"))
            self.assertTrue(result["changed"])
            self.assertEqual(
                parsed["marketplaces"]["brave-cow-windows-tools"]["source"],
                str(source),
            )
            self.assertTrue(
                parsed["plugins"]["windows-computer-use@brave-cow-windows-tools"][
                    "enabled"
                ]
            )

    def test_installers_expose_safe_adoption_controls(self) -> None:
        windows_installer = (ROOT / "install.ps1").read_text(encoding="utf-8")
        mac_installer = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn("function Install-BrowserHarness", windows_installer)
        self.assertIn("function Install-CodexWindowsComputerUse", windows_installer)
        self.assertIn("SkipBrowserHarness", windows_installer)
        self.assertIn("SkipCodexWindowsComputerUse", windows_installer)
        self.assertIn("scripts\\build.ps1", windows_installer)
        self.assertIn("scripts\\validate-plugin.ps1", windows_installer)
        self.assertIn("install_browser_harness", mac_installer)
        self.assertIn("--skip-browser-harness", mac_installer)


if __name__ == "__main__":
    unittest.main()
