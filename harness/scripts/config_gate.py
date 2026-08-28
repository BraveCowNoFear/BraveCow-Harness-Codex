from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

try:
    from .runtime_paths import CODEX_HOME
except ImportError:  # direct script execution
    from runtime_paths import CODEX_HOME

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


DEFAULT_CONFIG = CODEX_HOME / "config.toml"


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def concise_diagnostic(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    preferred = [
        line
        for line in lines
        if any(token in line.lower() for token in ("error", "unknown variant", "expected", "failed"))
    ]
    selected = preferred[:2] or lines[:2]
    value = " | ".join(selected)
    value = re.sub(r"[A-Za-z]:\\[^\s:]+", "<local-path>", value)
    return value[:600]


def codex_executable_candidates(parsed: dict, config_path: Path = DEFAULT_CONFIG) -> list[Path]:
    candidates: list[Path] = []

    configured_executable = os.environ.get("CODEX_EXECUTABLE")
    if configured_executable:
        candidates.append(Path(configured_executable))

    node_repl_env = (
        ((parsed.get("mcp_servers") or {}).get("node_repl") or {}).get("env") or {}
    )
    configured_cli = node_repl_env.get("CODEX_CLI_PATH")
    if configured_cli:
        candidates.append(Path(str(configured_cli)))

    if os.name == "nt":
        local_app_data = Path(
            os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
        )
        codex_bin = local_app_data / "OpenAI" / "Codex" / "bin"
        if codex_bin.exists():
            candidates.extend(
                sorted(
                    codex_bin.glob("*/codex.exe"),
                    key=lambda path: path.stat().st_mtime,
                    reverse=True,
                )
            )
            candidates.append(codex_bin / "codex.exe")

    discovered = shutil.which("codex")
    if discovered:
        candidates.append(Path(discovered))

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = os.path.normcase(os.path.abspath(str(candidate)))
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def resolve_codex_executable(
    parsed: dict,
    config_path: Path = DEFAULT_CONFIG,
    env: dict[str, str] | None = None,
) -> str | None:
    probe_env = (env or os.environ.copy()).copy()
    probe_env["CODEX_HOME"] = str(config_path.parent)
    for candidate in codex_executable_candidates(parsed, config_path):
        if not candidate.exists():
            continue
        try:
            probe = subprocess.run(
                [str(candidate), "--version"],
                capture_output=True,
                text=True,
                timeout=8,
                env=probe_env,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode == 0:
            return str(candidate)
    return None


def check_config(config_path: Path = DEFAULT_CONFIG, run_runtime: bool = True) -> dict:
    result: dict[str, object] = {
        "config_path": str(config_path),
        "syntax": "absent",
        "runtime": "not-run",
        "overall": "absent",
        "diagnostic": "",
        "codex_version": "unknown",
    }
    if not config_path.exists():
        return result

    try:
        parsed = tomllib.loads(read_text(config_path))
    except Exception as exc:  # noqa: BLE001
        result.update(syntax="fail", overall="fail", diagnostic=str(exc)[:600])
        return result

    result["syntax"] = "pass"
    result["overall"] = "pass"
    result["service_tier"] = parsed.get("service_tier", "unset")
    result["enabled_plugin_ids"] = sorted(
        plugin_id
        for plugin_id, payload in (parsed.get("plugins") or {}).items()
        if isinstance(payload, dict) and payload.get("enabled") is True
    )

    if not run_runtime:
        return result

    env = os.environ.copy()
    env["CODEX_HOME"] = str(config_path.parent)
    codex = resolve_codex_executable(parsed, config_path, env)
    if not codex:
        result.update(runtime="unavailable", overall="partial", diagnostic="codex executable not found")
        return result

    try:
        version = subprocess.run(
            [codex, "--version"],
            capture_output=True,
            text=True,
            timeout=8,
            env=env,
            check=False,
        )
        result["codex_version"] = (version.stdout or version.stderr).strip()[:120] or "unknown"
        probe = subprocess.run(
            [codex, "features", "list"],
            capture_output=True,
            text=True,
            timeout=12,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        result.update(runtime="timeout", overall="partial", diagnostic="codex semantic probe timed out")
        return result
    except OSError as exc:
        result.update(runtime="error", overall="partial", diagnostic=str(exc)[:600])
        return result

    if probe.returncode == 0:
        result["runtime"] = "pass"
        return result

    diagnostic = concise_diagnostic((probe.stderr or "") + "\n" + (probe.stdout or ""))
    if parsed.get("service_tier") == "priority" and "unknown variant `priority`" in diagnostic.lower():
        try:
            compatibility_probe = subprocess.run(
                [codex, "-c", 'service_tier="fast"', "features", "list"],
                capture_output=True,
                text=True,
                timeout=12,
                env=env,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            compatibility_probe = None
        if compatibility_probe is not None and compatibility_probe.returncode == 0:
            result.update(
                runtime="pass-legacy-fast-alias",
                overall="pass",
                compatibility_service_tier="fast",
                diagnostic=(
                    "bundled CLI schema lags the current official config schema; "
                    "remaining config validated with legacy service_tier=fast alias"
                ),
            )
            return result
    status = "runtime-schema-mismatch" if "unknown variant" in diagnostic.lower() else "runtime-fail"
    result.update(runtime=status, overall="fail", diagnostic=diagnostic)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Codex config syntax and runtime semantics without editing it.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--no-runtime", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-fail", action="store_true", help="Always exit zero; useful for audit/report generation.")
    args = parser.parse_args()

    result = check_config(args.config, run_runtime=not args.no_runtime)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    if args.no_fail:
        return 0
    return 0 if result["overall"] in {"pass", "absent"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
