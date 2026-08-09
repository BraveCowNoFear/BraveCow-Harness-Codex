from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

try:
    from .runtime_paths import HARNESS_HOME, HOME
except ImportError:  # direct script execution
    from runtime_paths import HARNESS_HOME, HOME


DEFAULT_INVENTORY = HARNESS_HOME / "catalog" / "skill-inventory.json"
DEFAULT_LOCK = HARNESS_HOME / "catalog" / "harness.lock.json"
DEFAULT_AUDIT = HARNESS_HOME / "reports" / "agent-harness-audit.md"

SECRET_PATTERNS = (
    re.compile(r"gh[opsu]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sanitize_text(text: str, home: Path = HOME) -> str:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise ValueError(f"refusing to export content matching secret pattern: {pattern.pattern}")
    home_text = str(home)
    variants = {home_text, home_text.replace("\\", "/")}
    sanitized = text
    for variant in sorted(variants, key=len, reverse=True):
        replacement = "%USERPROFILE%" if os.name == "nt" else "$HOME"
        sanitized = re.sub(re.escape(variant), replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def sanitize_value(value, home: Path = HOME):
    if isinstance(value, dict):
        return {str(key): sanitize_value(item, home) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_value(item, home) for item in value]
    if isinstance(value, str):
        return sanitize_text(value, home)
    return value


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_snapshot(
    inventory_path: Path,
    lock_path: Path,
    audit_path: Path,
    output_dir: Path,
    *,
    baseline_tag: str = "",
    baseline_commit: str = "",
    config_gate_path: Path | None = None,
    prompt_metrics_path: Path | None = None,
    home: Path = HOME,
) -> dict:
    inventory = json.loads(read_text(inventory_path))
    lock = json.loads(read_text(lock_path))
    audit = read_text(audit_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "skill-inventory.sanitized.json": sanitize_value(inventory, home),
        "harness.lock.sanitized.json": sanitize_value(lock, home),
    }
    for name, payload in outputs.items():
        write_json(output_dir / name, payload)

    audit_output = output_dir / "agent-harness-audit.sanitized.md"
    audit_output.write_text(sanitize_text(audit, home), encoding="utf-8")

    evidence: dict[str, object] = {}
    if config_gate_path:
        evidence["config_gate"] = sanitize_value(json.loads(read_text(config_gate_path)), home)
    if prompt_metrics_path:
        evidence["prompt_metrics"] = sanitize_value(json.loads(read_text(prompt_metrics_path)), home)

    manifest = {
        "schema_version": 1,
        "snapshot_generated_at": datetime.now(UTC).isoformat(),
        "baseline_tag": baseline_tag,
        "baseline_commit": baseline_commit,
        "source_generated_at": inventory.get("generated_at"),
        "inventory_summary": inventory.get("summary", {}),
        "plugin_summary": inventory.get("plugin_summary", {}),
        "lock_summary": {
            "schema_version": lock.get("schema_version"),
            "skills": len(lock.get("skills", [])),
            "plugins": len(lock.get("plugins", [])),
            "components": [
                {
                    key: component.get(key)
                    for key in ("id", "declared_version", "installed_version", "available_version", "state")
                }
                for component in lock.get("components", [])
            ],
        },
        "evidence": evidence,
        "sources": {
            "skill_inventory_sha256": sha256_file(inventory_path),
            "harness_lock_sha256": sha256_file(lock_path),
            "audit_sha256": sha256_file(audit_path),
        },
    }
    safe_manifest = sanitize_value(manifest, home)
    write_json(output_dir / "snapshot-manifest.json", safe_manifest)

    snapshot_files = sorted(
        path for path in output_dir.iterdir() if path.is_file() and path.name != "checksums.json"
    )
    checksums = {path.name: sha256_file(path) for path in snapshot_files}
    write_json(output_dir / "checksums.json", checksums)
    return {
        "output_dir": sanitize_text(str(output_dir), home),
        "files": sorted([*checksums, "checksums.json"]),
        "manifest": safe_manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a repository-safe local harness baseline snapshot.")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--baseline-tag", default="")
    parser.add_argument("--baseline-commit", default="")
    parser.add_argument("--config-gate", type=Path)
    parser.add_argument("--prompt-metrics", type=Path)
    args = parser.parse_args()
    result = export_snapshot(
        args.inventory,
        args.lock,
        args.audit,
        args.output_dir,
        baseline_tag=args.baseline_tag,
        baseline_commit=args.baseline_commit,
        config_gate_path=args.config_gate,
        prompt_metrics_path=args.prompt_metrics,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
