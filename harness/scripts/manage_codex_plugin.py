from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


MARKETPLACE_ID = "brave-cow-windows-tools"
PLUGIN_ID = "windows-computer-use@brave-cow-windows-tools"
MARKETPLACE_HEADER = f"marketplaces.{MARKETPLACE_ID}"
PLUGIN_HEADER = f'plugins."{PLUGIN_ID}"'
SECTION_RE = re.compile(r"^\s*\[([^]]+)]\s*(?:#.*)?$")


def read_config(path: Path) -> tuple[str, bool, str]:
    if not path.exists():
        return "", False, os.linesep
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, had_bom, newline


def find_section(lines: list[str], header: str) -> tuple[int, int] | None:
    for index, line in enumerate(lines):
        match = SECTION_RE.match(line)
        if not match or match.group(1).strip() != header:
            continue
        end = len(lines)
        for next_index in range(index + 1, len(lines)):
            if SECTION_RE.match(lines[next_index]):
                end = next_index
                break
        return index, end
    return None


def set_table_values(
    lines: list[str],
    header: str,
    values: dict[str, object],
) -> list[str]:
    result = list(lines)
    section = find_section(result, header)
    rendered = {
        key: f"{key} = {json.dumps(value, ensure_ascii=False)}" if not isinstance(value, bool)
        else f"{key} = {'true' if value else 'false'}"
        for key, value in values.items()
    }

    if section is None:
        while result and not result[-1].strip():
            result.pop()
        if result:
            result.append("")
        result.append(f"[{header}]")
        result.extend(rendered.values())
        result.append("")
        return result

    start, end = section
    found: set[str] = set()
    key_patterns = {
        key: re.compile(rf"^\s*{re.escape(key)}\s*=") for key in rendered
    }
    for index in range(start + 1, end):
        for key, pattern in key_patterns.items():
            if pattern.match(result[index]):
                result[index] = rendered[key]
                found.add(key)
                break
    insert_at = end
    for key, value in rendered.items():
        if key not in found:
            result.insert(insert_at, value)
            insert_at += 1
    return result


def atomic_write(path: Path, text: str, had_bom: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoding = "utf-8-sig" if had_bom else "utf-8"
    with tempfile.NamedTemporaryFile(
        "w", encoding=encoding, newline="", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def configure_plugin(
    config_path: Path,
    marketplace_source: Path,
    preserve_existing_source: bool = False,
    dry_run: bool = False,
) -> dict[str, object]:
    original, had_bom, newline = read_config(config_path)
    parsed = tomllib.loads(original) if original.strip() else {}
    marketplace = (parsed.get("marketplaces") or {}).get(MARKETPLACE_ID) or {}
    existing_source = str(marketplace.get("source") or "")
    existing_source_type = str(marketplace.get("source_type") or "")
    keep_existing = bool(
        preserve_existing_source
        and existing_source_type == "local"
        and existing_source
        and Path(existing_source).exists()
    )
    effective_source = Path(existing_source) if keep_existing else marketplace_source

    lines = original.splitlines()
    if not keep_existing:
        lines = set_table_values(
            lines,
            MARKETPLACE_HEADER,
            {"source_type": "local", "source": str(marketplace_source)},
        )
    lines = set_table_values(lines, PLUGIN_HEADER, {"enabled": True})
    updated = newline.join(lines).rstrip() + newline
    reparsed = tomllib.loads(updated)
    enabled = bool(
        ((reparsed.get("plugins") or {}).get(PLUGIN_ID) or {}).get("enabled") is True
    )
    if not enabled:
        raise RuntimeError(f"failed to enable {PLUGIN_ID}")

    changed = updated != original
    if changed and not dry_run:
        atomic_write(config_path, updated, had_bom)
    return {
        "status": "configured" if changed else "already-configured",
        "changed": changed,
        "dry_run": dry_run,
        "config_path": str(config_path),
        "marketplace_id": MARKETPLACE_ID,
        "plugin_id": PLUGIN_ID,
        "effective_source": str(effective_source),
        "preserved_existing_source": keep_existing,
        "enabled": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enable the Brave Cow Windows Computer Use marketplace without rewriting unrelated Codex config."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--marketplace-source", type=Path, required=True)
    parser.add_argument("--preserve-existing-source", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = configure_plugin(
        args.config,
        args.marketplace_source,
        preserve_existing_source=args.preserve_existing_source,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
