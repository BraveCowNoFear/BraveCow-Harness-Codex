from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .runtime_paths import HARNESS_HOME
except ImportError:  # direct script execution
    from runtime_paths import HARNESS_HOME


DEFAULT_BEFORE = HARNESS_HOME / "catalog" / "harness.lock.previous.json"
DEFAULT_AFTER = HARNESS_HOME / "catalog" / "harness.lock.json"


def identity(section: str, item: dict) -> str:
    if section == "skills":
        return str(item.get("real_path") or item.get("id"))
    if section == "plugins":
        return f"{item.get('name')}@{item.get('cache_source')}"
    return str(item.get("id"))


def compact(item: dict) -> dict:
    keep = {
        "skills": ("id", "version", "content_sha256", "state", "provenance", "rollback", "verification"),
        "plugins": ("name", "version", "state", "resolved", "manifest_sha256", "rollback"),
        "components": ("id", "declared_version", "installed_version", "available_version", "state", "provenance", "rollback", "verification"),
    }
    return {key: item.get(key) for key in keep.get(str(item.get("_section")), ())}


def diff_locks(before: dict, after: dict) -> dict:
    result: dict[str, object] = {
        "before_schema": before.get("schema_version"),
        "after_schema": after.get("schema_version"),
        "sections": {},
    }
    total_changes = 0
    for section in ("skills", "plugins", "components"):
        old = {identity(section, item): item for item in before.get(section, [])}
        new = {identity(section, item): item for item in after.get(section, [])}
        added = sorted(new.keys() - old.keys())
        removed = sorted(old.keys() - new.keys())
        changed = []
        for key in sorted(old.keys() & new.keys()):
            old_item = {**old[key], "_section": section}
            new_item = {**new[key], "_section": section}
            if compact(old_item) != compact(new_item):
                changed.append(key)
        result["sections"][section] = {"added": added, "removed": removed, "changed": changed}
        total_changes += len(added) + len(removed) + len(changed)
    result["total_changes"] = total_changes
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff two observed harness locks without updating anything.")
    parser.add_argument("--before", type=Path, default=DEFAULT_BEFORE)
    parser.add_argument("--after", type=Path, default=DEFAULT_AFTER)
    args = parser.parse_args()
    if not args.before.exists() or not args.after.exists():
        print(json.dumps({"status": "not-enough-snapshots", "before": str(args.before), "after": str(args.after)}, indent=2))
        return 0
    result = diff_locks(
        json.loads(args.before.read_text(encoding="utf-8-sig")),
        json.loads(args.after.read_text(encoding="utf-8-sig")),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
