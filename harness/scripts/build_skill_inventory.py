from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


HOME = Path.home()
CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))
AGENTS_HOME = Path(os.environ.get("AGENTS_HOME", HOME / ".agents"))
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", HOME / ".openclaw"))
SHARED_SKILLS_HOME = Path(os.environ.get("SHARED_SKILLS_HOME", AGENTS_HOME / "skills"))
CODEX_PLUGIN_CACHE = Path(os.environ.get("CODEX_PLUGIN_CACHE", CODEX_HOME / "plugins" / "cache"))
CONFIG_PATH = CODEX_HOME / "config.toml"

ROOTS = {
    "shared": SHARED_SKILLS_HOME,
    "codex": CODEX_HOME / "skills",
    "openclaw": OPENCLAW_HOME / "skills",
}

DEFAULT_OUTPUT = CODEX_HOME / "harness" / "catalog" / "skill-inventory.json"
DEFAULT_LOCK_OUTPUT = CODEX_HOME / "harness" / "catalog" / "harness.lock.json"


@dataclass
class SkillEntry:
    runtime: str
    skill_id: str
    path: str
    real_path: str
    is_link: bool
    link_target: list[str]
    has_skill_md: bool
    name: str | None
    description: str | None
    declared_version: str | None
    content_sha256: str | None
    state: str


@dataclass
class PluginEntry:
    cache_source: str
    name: str
    version: str
    path: str
    manifest_path: str
    skill_ids: list[str]
    has_apps: bool
    has_mcp: bool
    plugin_id: str
    enabled_by_config: bool
    state: str
    manifest_sha256: str | None
    manifest_error: str | None = None


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def parse_frontmatter_fields(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    in_frontmatter = False
    frontmatter: list[str] = []
    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if in_frontmatter:
            frontmatter.append(line)

    fields: dict[str, str] = {}
    index = 0
    while index < len(frontmatter):
        line = frontmatter[index]
        if line.startswith((" ", "\t")) or ":" not in line:
            index += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if value in {"|", ">"}:
            block_lines: list[str] = []
            index += 1
            while index < len(frontmatter):
                next_line = frontmatter[index]
                if next_line and not next_line.startswith((" ", "\t")) and ":" in next_line:
                    break
                stripped = next_line.strip()
                if stripped:
                    block_lines.append(stripped)
                index += 1
            fields[key] = " ".join(block_lines)
            continue
        fields[key] = value
        index += 1
    return fields


def parse_frontmatter(text: str) -> tuple[str | None, str | None]:
    fields = parse_frontmatter_fields(text)
    return fields.get("name") or None, fields.get("description") or None


def load_enabled_plugin_ids() -> set[str]:
    if not CONFIG_PATH.exists():
        return set()
    try:
        config = tomllib.loads(read_text(CONFIG_PATH))
    except Exception:  # noqa: BLE001
        return set()
    return {
        plugin_id
        for plugin_id, payload in (config.get("plugins") or {}).items()
        if isinstance(payload, dict) and payload.get("enabled") is True
    }


def iter_skill_dirs(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return sorted([path for path in root.iterdir() if path.is_dir()], key=lambda p: p.name.lower())


def discover_plugin_entries(enabled_plugin_ids: set[str] | None = None) -> list[PluginEntry]:
    if not CODEX_PLUGIN_CACHE.exists():
        return []

    enabled_plugin_ids = enabled_plugin_ids or set()
    entries: list[PluginEntry] = []
    seen_packages: set[str] = set()
    for manifest_path in sorted(CODEX_PLUGIN_CACHE.rglob("plugin.json")):
        if manifest_path.parent.name != ".codex-plugin":
            continue
        package_path = manifest_path.parent.parent
        real_package_path = os.path.realpath(package_path)
        if real_package_path in seen_packages:
            continue
        seen_packages.add(real_package_path)

        try:
            manifest = json.loads(read_text(manifest_path))
            manifest_error = None
        except (OSError, json.JSONDecodeError) as exc:
            manifest = {}
            manifest_error = str(exc)

        relative_parts = package_path.relative_to(CODEX_PLUGIN_CACHE).parts
        cache_source = relative_parts[0] if relative_parts else "unknown"
        fallback_name = relative_parts[1] if len(relative_parts) > 1 else package_path.name
        fallback_version = relative_parts[2] if len(relative_parts) > 2 else "unknown"
        skills_value = manifest.get("skills", "./skills/")
        skills_path = package_path / str(skills_value)
        skill_ids = [path.name for path in iter_skill_dirs(skills_path) if (path / "SKILL.md").exists()]

        plugin_name = str(manifest.get("name") or fallback_name)
        plugin_id = f"{plugin_name}@{cache_source}"
        enabled_by_config = plugin_id in enabled_plugin_ids
        entries.append(
            PluginEntry(
                cache_source=cache_source,
                name=plugin_name,
                version=str(manifest.get("version") or fallback_version),
                path=str(package_path),
                manifest_path=str(manifest_path),
                skill_ids=skill_ids,
                has_apps=bool(manifest.get("apps")),
                has_mcp=bool(manifest.get("mcp")) or (package_path / "mcp").exists(),
                plugin_id=plugin_id,
                enabled_by_config=enabled_by_config,
                state="enabled-by-config" if enabled_by_config else "cache-only",
                manifest_sha256=sha256_file(manifest_path),
                manifest_error=manifest_error,
            )
        )
    return entries


def build_entries() -> list[SkillEntry]:
    entries: list[SkillEntry] = []
    for runtime, root in ROOTS.items():
        for skill_dir in iter_skill_dirs(root):
            skill_md = skill_dir / "SKILL.md"
            name = None
            description = None
            declared_version = None
            if skill_md.exists():
                skill_text = read_text(skill_md)
                fields = parse_frontmatter_fields(skill_text)
                name = fields.get("name") or None
                description = fields.get("description") or None
                declared_version = fields.get("version") or None
            path_str = str(skill_dir)
            real_path = os.path.realpath(path_str)
            is_link = skill_dir.is_symlink() or real_path != path_str
            entries.append(
                SkillEntry(
                    runtime=runtime,
                    skill_id=skill_dir.name,
                    path=path_str,
                    real_path=real_path,
                    is_link=is_link,
                    link_target=[real_path] if is_link else [],
                    has_skill_md=skill_md.exists(),
                    name=name,
                    description=description,
                    declared_version=declared_version,
                    content_sha256=sha256_file(skill_md) if skill_md.exists() else None,
                    state="discoverable" if skill_md.exists() else "container-only",
                )
            )
    return entries


def summarize(entries: list[SkillEntry]) -> dict:
    by_runtime = defaultdict(int)
    shared_entries = [entry for entry in entries if entry.runtime == "shared" and entry.has_skill_md]
    shared_by_id = {entry.skill_id: entry for entry in shared_entries}
    missing_links = defaultdict(list)
    shared_mirrors: dict[str, dict[str, object]] = {}
    shadowed_shared_skills: dict[str, list[dict[str, str | bool]]] = defaultdict(list)

    for entry in entries:
        by_runtime[entry.runtime] += 1

    for shared_entry in shared_entries:
        mirror_refs: list[dict[str, object]] = []
        for entry in [item for item in entries if item.skill_id == shared_entry.skill_id]:
            if entry.real_path != shared_entry.real_path:
                continue
            mirror_refs.append(
                {
                    "runtime": entry.runtime,
                    "path": entry.path,
                    "real_path": entry.real_path,
                    "is_link": entry.is_link,
                }
            )

        if len(mirror_refs) > 1:
            shared_mirrors[shared_entry.skill_id] = {
                "shared_path": shared_entry.real_path,
                "refs": sorted(mirror_refs, key=lambda ref: str(ref["runtime"])),
            }

        for runtime in ("codex", "openclaw"):
            if not ROOTS[runtime].exists():
                continue
            if not any(
                entry.runtime == runtime
                and entry.skill_id == shared_entry.skill_id
                and entry.real_path == shared_entry.real_path
                for entry in entries
            ):
                missing_links[runtime].append(shared_entry.skill_id)

    for entry in entries:
        if entry.runtime == "shared":
            continue
        shared_entry = shared_by_id.get(entry.skill_id)
        if shared_entry is None or entry.real_path == shared_entry.real_path:
            continue
        shadowed_shared_skills[entry.runtime].append(
            {
                "skill_id": entry.skill_id,
                "path": entry.path,
                "real_path": entry.real_path,
                "is_link": entry.is_link,
                "shared_path": shared_entry.path,
                "shared_real_path": shared_entry.real_path,
            }
        )

    return {
        "counts": dict(by_runtime),
        "valid_counts": {
            runtime: sum(entry.runtime == runtime and entry.has_skill_md for entry in entries)
            for runtime in ROOTS
        },
        "unique_discoverable_real_paths": len(
            {entry.real_path for entry in entries if entry.has_skill_md}
        ),
        "declared_version_count": sum(bool(entry.declared_version) for entry in entries if entry.has_skill_md),
        "missing_shared_links": {runtime: sorted(ids) for runtime, ids in missing_links.items()},
        "shared_mirrors": dict(sorted(shared_mirrors.items())),
        "shadowed_shared_skills": {
            runtime: sorted(items, key=lambda item: str(item["skill_id"]).lower())
            for runtime, items in shadowed_shared_skills.items()
        },
    }


def summarize_plugins(entries: list[PluginEntry]) -> dict:
    sources = defaultdict(int)
    for entry in entries:
        sources[entry.cache_source] += 1
    return {
        "packages": len(entries),
        "skills": sum(len(entry.skill_ids) for entry in entries),
        "with_apps": sum(entry.has_apps for entry in entries),
        "with_mcp": sum(entry.has_mcp for entry in entries),
        "invalid_manifests": sum(entry.manifest_error is not None for entry in entries),
        "enabled_by_config": sum(entry.enabled_by_config for entry in entries),
        "cache_only": sum(not entry.enabled_by_config for entry in entries),
        "sources": dict(sorted(sources.items())),
    }


def find_git_root(path: Path) -> Path | None:
    current = path.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def git_provenance(path: Path) -> dict[str, object]:
    root = find_git_root(path)
    if root is None:
        return {"kind": "local", "root": "", "commit": "", "dirty": None}
    try:
        commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout.strip()
        return {"kind": "git", "root": str(root), "commit": commit, "dirty": bool(status)}
    except (OSError, subprocess.TimeoutExpired):
        return {"kind": "git", "root": str(root), "commit": "", "dirty": None}


def build_lock(entries: list[SkillEntry], plugins: list[PluginEntry], generated_at: str) -> dict:
    grouped: dict[str, list[SkillEntry]] = defaultdict(list)
    for entry in entries:
        if entry.has_skill_md:
            grouped[entry.real_path].append(entry)

    skills = []
    provenance_cache: dict[str, dict[str, object]] = {}
    for real_path, refs in sorted(grouped.items(), key=lambda item: item[0].lower()):
        primary = refs[0]
        root = find_git_root(Path(real_path))
        provenance_key = str(root) if root else "local"
        if provenance_key not in provenance_cache:
            provenance_cache[provenance_key] = git_provenance(Path(real_path))
        skills.append(
            {
                "id": primary.skill_id,
                "name": primary.name,
                "version": primary.declared_version,
                "content_sha256": primary.content_sha256,
                "state": "discoverable",
                "runtimes": sorted({ref.runtime for ref in refs}),
                "paths": sorted({ref.path for ref in refs}),
                "real_path": real_path,
                "provenance": provenance_cache[provenance_key],
            }
        )

    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "skills": skills,
        "plugins": [
            {
                "plugin_id": entry.plugin_id,
                "name": entry.name,
                "version": entry.version,
                "state": entry.state,
                "enabled_by_config": entry.enabled_by_config,
                "cache_source": entry.cache_source,
                "manifest_sha256": entry.manifest_sha256,
                "path": entry.path,
            }
            for entry in plugins
        ],
    }


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local inventory of shared and runtime-specific skills.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--lock-output", type=Path, default=DEFAULT_LOCK_OUTPUT)
    args = parser.parse_args()

    entries = build_entries()
    enabled_plugin_ids = load_enabled_plugin_ids()
    plugins = discover_plugin_entries(enabled_plugin_ids)
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        "generated_at": generated_at,
        "roots": {**{name: str(path) for name, path in ROOTS.items()}, "plugin_cache": str(CODEX_PLUGIN_CACHE)},
        "summary": summarize(entries),
        "plugin_summary": summarize_plugins(plugins),
        "entries": [asdict(entry) for entry in entries],
        "plugins": [asdict(entry) for entry in plugins],
        "enabled_plugin_ids": sorted(enabled_plugin_ids),
    }
    write_text_atomic(args.output, json.dumps(payload, ensure_ascii=False, indent=2))
    write_text_atomic(
        args.lock_output,
        json.dumps(build_lock(entries, plugins, generated_at), ensure_ascii=False, indent=2),
    )
    print(f"Wrote {args.output}")
    print(f"Wrote {args.lock_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
