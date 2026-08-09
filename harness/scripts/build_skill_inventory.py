from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import plistlib
import re
import shutil
import subprocess
import tempfile
import urllib.parse
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

try:
    from .runtime_paths import (
        CODEX_HOME,
        HARNESS_HOME,
        HOME,
        RUNTIME_SKILL_ROOTS,
    )
except ImportError:  # direct script execution
    from runtime_paths import CODEX_HOME, HARNESS_HOME, HOME, RUNTIME_SKILL_ROOTS

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


CODEX_PLUGIN_CACHE = Path(os.environ.get("CODEX_PLUGIN_CACHE", CODEX_HOME / "plugins" / "cache"))
CONFIG_PATH = CODEX_HOME / "config.toml"

ROOTS = RUNTIME_SKILL_ROOTS

DEFAULT_OUTPUT = HARNESS_HOME / "catalog" / "skill-inventory.json"
DEFAULT_LOCK_OUTPUT = HARNESS_HOME / "catalog" / "harness.lock.json"
UPSTREAM_OBSERVATIONS_PATH = HARNESS_HOME / "catalog" / "upstream-observations.json"


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
    skills_path: str
    skill_ids: list[str]
    has_apps: bool
    has_mcp: bool
    plugin_id: str
    enabled_by_config: bool
    installed_remote: bool
    remote_plugin_id: str | None
    resolved: bool
    resolution_reason: str
    state: str
    manifest_sha256: str | None
    manifest_error: str | None = None


@dataclass
class PluginSkillEntry:
    catalog_id: str
    skill_id: str
    plugin_id: str
    plugin_name: str
    plugin_version: str
    path: str
    name: str | None
    description: str | None
    declared_version: str | None
    content_sha256: str | None


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


def load_remote_install_marker(package_path: Path) -> tuple[bool, str | None]:
    marker_path = package_path.parent / ".codex-remote-plugin-install.json"
    if not marker_path.exists():
        return False, None
    try:
        marker = json.loads(read_text(marker_path))
    except (OSError, json.JSONDecodeError):
        return True, None
    remote_id = marker.get("remote_plugin_id")
    return True, str(remote_id) if remote_id else None


def version_sort_key(value: str) -> tuple[tuple[int, ...], str]:
    return tuple(int(part) for part in re.findall(r"\d+", value)), value.lower()


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
        installed_remote, remote_plugin_id = load_remote_install_marker(package_path)
        entries.append(
            PluginEntry(
                cache_source=cache_source,
                name=plugin_name,
                version=str(manifest.get("version") or fallback_version),
                path=str(package_path),
                manifest_path=str(manifest_path),
                skills_path=str(skills_path),
                skill_ids=skill_ids,
                has_apps=bool(manifest.get("apps")),
                has_mcp=bool(manifest.get("mcp")) or (package_path / "mcp").exists(),
                plugin_id=plugin_id,
                enabled_by_config=enabled_by_config,
                installed_remote=installed_remote,
                remote_plugin_id=remote_plugin_id,
                resolved=False,
                resolution_reason="unresolved",
                state="cache-only",
                manifest_sha256=sha256_file(manifest_path),
                manifest_error=manifest_error,
            )
        )

    by_name: dict[str, list[PluginEntry]] = defaultdict(list)
    for entry in entries:
        by_name[entry.name].append(entry)
    for candidates in by_name.values():
        remote_candidates = [entry for entry in candidates if entry.installed_remote]
        exact_candidates = [entry for entry in candidates if entry.enabled_by_config]
        if remote_candidates:
            winner = max(remote_candidates, key=lambda entry: version_sort_key(entry.version))
            winner.resolved = True
            winner.resolution_reason = "remote-install-marker"
            winner.state = "resolved-remote-install"
            for entry in candidates:
                if entry is winner:
                    continue
                if entry.enabled_by_config:
                    entry.state = "superseded-config-cache"
                    entry.resolution_reason = f"superseded-by:{winner.version}@{winner.cache_source}"
                elif entry.installed_remote:
                    entry.state = "superseded-remote-cache"
                    entry.resolution_reason = f"superseded-by:{winner.version}@{winner.cache_source}"
        elif exact_candidates:
            winner = max(exact_candidates, key=lambda entry: version_sort_key(entry.version))
            winner.resolved = True
            winner.resolution_reason = "exact-config-id"
            winner.state = "resolved-config"
            for entry in exact_candidates:
                if entry is not winner:
                    entry.state = "superseded-config-cache"
                    entry.resolution_reason = f"superseded-by:{winner.version}@{winner.cache_source}"
    return entries


def discover_resolved_plugin_skills(plugins: list[PluginEntry]) -> list[PluginSkillEntry]:
    entries: list[PluginSkillEntry] = []
    for plugin in plugins:
        if not plugin.resolved:
            continue
        skills_path = Path(plugin.skills_path)
        for skill_dir in iter_skill_dirs(skills_path):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            fields = parse_frontmatter_fields(read_text(skill_md))
            skill_id = skill_dir.name
            entries.append(
                PluginSkillEntry(
                    catalog_id=f"{plugin.name}:{skill_id}",
                    skill_id=skill_id,
                    plugin_id=plugin.plugin_id,
                    plugin_name=plugin.name,
                    plugin_version=plugin.version,
                    path=str(skill_dir),
                    name=fields.get("name") or None,
                    description=fields.get("description") or None,
                    declared_version=fields.get("version") or None,
                    content_sha256=sha256_file(skill_md),
                )
            )
    return sorted(entries, key=lambda entry: entry.catalog_id.lower())


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

        for runtime in ("codex", "zcode", "openclaw"):
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
        "installed_remote": sum(entry.installed_remote for entry in entries),
        "resolved": sum(entry.resolved for entry in entries),
        "resolved_skill_entries": sum(len(entry.skill_ids) for entry in entries if entry.resolved),
        "cache_only": sum(entry.state == "cache-only" for entry in entries),
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


def git_value(root: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def git_provenance(path: Path) -> dict[str, object]:
    root = find_git_root(path)
    if root is None:
        return {
            "kind": "local",
            "root": "",
            "remote_url": "",
            "branch": "",
            "upstream": "",
            "commit": "",
            "tag": "",
            "dirty": None,
            "ahead": None,
            "behind": None,
        }
    try:
        commit = git_value(root, "rev-parse", "HEAD")
        status = git_value(root, "status", "--porcelain")
        branch = git_value(root, "branch", "--show-current")
        upstream = git_value(root, "rev-parse", "--abbrev-ref", "@{upstream}")
        counts = git_value(root, "rev-list", "--left-right", "--count", "@{upstream}...HEAD") if upstream else ""
        behind = ahead = None
        if counts:
            parts = counts.split()
            if len(parts) == 2 and all(part.isdigit() for part in parts):
                behind, ahead = int(parts[0]), int(parts[1])
        return {
            "kind": "git",
            "root": str(root),
            "remote_url": git_value(root, "remote", "get-url", "origin"),
            "branch": branch,
            "upstream": upstream,
            "commit": commit,
            "tag": git_value(root, "describe", "--tags", "--exact-match", "HEAD"),
            "dirty": bool(status),
            "ahead": ahead,
            "behind": behind,
        }
    except (OSError, subprocess.TimeoutExpired):
        return {"kind": "git", "root": str(root), "commit": "", "dirty": None}


def discover_license(path: Path, git_root: Path | None) -> dict[str, str]:
    search_root = git_root or path
    candidates = []
    if search_root.exists():
        candidates.extend(sorted(search_root.glob("LICENSE*")))
        candidates.extend(sorted(search_root.glob("COPYING*")))
    for candidate in candidates:
        if candidate.is_file():
            return {
                "status": "present",
                "file": str(candidate),
                "sha256": sha256_file(candidate) or "",
            }
    return {"status": "not-declared", "file": "", "sha256": ""}


def load_verification_registry() -> dict[str, dict[str, object]]:
    path = HARNESS_HOME / "catalog" / "verification.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return {}
    records = payload.get("records", []) if isinstance(payload, dict) else []
    result: dict[str, dict[str, object]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        for key in (record.get("real_path"), record.get("id")):
            if key:
                result[str(key)] = record
    return result


def load_upstream_observations(path: Path = UPSTREAM_OBSERVATIONS_PATH) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return {}
    records = payload.get("records", []) if isinstance(payload, dict) else []
    return {
        str(record["id"]): record
        for record in records
        if isinstance(record, dict) and record.get("id")
    }


def normalized_version(value: object) -> str:
    text = str(value or "").strip()
    match = re.search(r"\d+(?:\.\d+)+(?:[-.][0-9A-Za-z.-]+)?", text)
    return match.group(0) if match else text


def observed_component_fields(record: dict[str, object] | None) -> dict[str, object]:
    record = record or {}
    return {
        "available_version": record.get("available_version"),
        "upstream": {
            key: record.get(key)
            for key in ("source_url", "source_ref", "source_kind", "integrity", "license", "observed_at", "stability")
            if record.get(key) is not None
        },
    }


def codex_cli_component(generated_at: str, observations: dict[str, dict[str, object]], verification: dict[str, dict[str, object]]) -> dict[str, object] | None:
    executable = shutil.which("codex")
    if not executable:
        return None
    try:
        probe = subprocess.run(
            [executable, "--version"], capture_output=True, text=True, timeout=8, check=False
        )
        installed_version = normalized_version((probe.stdout or probe.stderr).strip())
    except (OSError, subprocess.TimeoutExpired):
        installed_version = "unknown"
    record = observations.get("codex-cli", {})
    available_version = normalized_version(record.get("available_version"))
    executable_path = Path(executable)
    return {
        "id": "codex-cli",
        "declared_version": installed_version,
        "installed_version": installed_version,
        **observed_component_fields(record),
        "state": "drift" if available_version and installed_version != available_version else "installed",
        "source_path": str(executable_path),
        "provenance": {
            "kind": "desktop-bundled-binary",
            "path": str(executable_path),
            "sha256": sha256_file(executable_path),
        },
        "license": {
            "status": "declared-upstream" if record.get("license") else "unknown",
            "spdx": record.get("license", ""),
            "source_url": record.get("source_url", ""),
        },
        "last_verified": generated_at,
        "verification": verification.get("component:codex-cli", {"status": "not-recorded", "tests": [], "last_verified": None}),
        "update_policy": "desktop-owned; never replace the bundled binary in place",
        "rollback": {"kind": "binary-hash", "ref": sha256_file(executable_path)},
    }


def zcode_desktop_component(
    generated_at: str,
    observations: dict[str, dict[str, object]],
    verification: dict[str, dict[str, object]],
) -> dict[str, object] | None:
    candidates: list[Path] = []
    configured = os.environ.get("ZCODE_EXECUTABLE")
    if configured:
        candidates.append(Path(configured))
    if os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", HOME / "AppData" / "Local"))
        program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
        candidates.extend(
            [
                local / "Programs" / "ZCode" / "ZCode.exe",
                local / "ZCode" / "ZCode.exe",
                program_files / "ZCode" / "ZCode.exe",
            ]
        )
    else:
        candidates.extend(
            [
                Path("/Applications/ZCode.app"),
                HOME / "Applications" / "ZCode.app",
            ]
        )
    source = next((path for path in candidates if path.exists()), None)
    if source is None:
        return None

    installed_version = "unknown"
    info_plist = source / "Contents" / "Info.plist" if source.suffix == ".app" else None
    if info_plist and info_plist.exists():
        try:
            with info_plist.open("rb") as handle:
                payload = plistlib.load(handle)
            installed_version = str(
                payload.get("CFBundleShortVersionString") or payload.get("CFBundleVersion") or "unknown"
            )
        except (OSError, plistlib.InvalidFileException):
            pass

    record = observations.get("zcode-desktop", {})
    available_version = normalized_version(record.get("available_version"))
    normalized_installed = normalized_version(installed_version)
    return {
        "id": "zcode-desktop",
        "declared_version": installed_version,
        "installed_version": installed_version,
        **observed_component_fields(record),
        "state": (
            "drift"
            if available_version and normalized_installed not in {"", "unknown"} and normalized_installed != available_version
            else "installed"
        ),
        "source_path": str(source),
        "provenance": {
            "kind": "desktop-application",
            "path": str(source),
            "sha256": sha256_file(source) if source.is_file() else None,
        },
        "license": {
            "status": "declared-upstream" if record.get("license") else "unknown",
            "spdx": record.get("license", ""),
            "source_url": record.get("source_url", ""),
        },
        "last_verified": generated_at,
        "verification": verification.get(
            "component:zcode-desktop",
            {"status": "not-recorded", "tests": [], "last_verified": None},
        ),
        "update_policy": "desktop-owned; use the official ZCode installer",
        "rollback": {"kind": "desktop-version", "ref": installed_version},
    }


def openclaw_component(generated_at: str, observations: dict[str, dict[str, object]], verification: dict[str, dict[str, object]]) -> dict[str, object] | None:
    executable = shutil.which("openclaw")
    if not executable:
        return None
    executable_path = Path(executable)
    package_root = executable_path.parent / "node_modules" / "openclaw"
    package_json = package_root / "package.json"
    installed_version = "unknown"
    if package_json.exists():
        try:
            installed_version = normalized_version(json.loads(read_text(package_json)).get("version"))
        except (OSError, json.JSONDecodeError):
            pass
    record = observations.get("openclaw", {})
    available_version = normalized_version(record.get("available_version"))
    return {
        "id": "openclaw",
        "declared_version": installed_version,
        "installed_version": installed_version,
        **observed_component_fields(record),
        "state": "drift" if available_version and installed_version != available_version else "installed",
        "source_path": str(package_root if package_root.exists() else executable_path),
        "provenance": {
            "kind": "npm-package",
            "path": str(package_root if package_root.exists() else executable_path),
            "package_json_sha256": sha256_file(package_json) if package_json.exists() else None,
        },
        "license": discover_license(package_root, None) if package_root.exists() else {"status": "unknown", "file": "", "sha256": ""},
        "last_verified": generated_at,
        "verification": verification.get("component:openclaw", {"status": "not-recorded", "tests": [], "last_verified": None}),
        "update_policy": "audit release and back up config before package migration",
        "rollback": {
            "kind": "npm-version",
            "ref": installed_version,
        },
    }


def distribution_source(name: str) -> tuple[str | None, Path | None]:
    try:
        distribution = importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError:
        return None, None
    source: Path | None = None
    direct_url_text = distribution.read_text("direct_url.json")
    if direct_url_text:
        try:
            url = json.loads(direct_url_text).get("url", "")
            if str(url).startswith("file:"):
                source = Path(urllib.parse.unquote(urllib.parse.urlparse(str(url)).path.lstrip("/")))
        except json.JSONDecodeError:
            pass
    return distribution.version, source


def graphiti_installed_version(source_root: Path) -> str | None:
    site_packages = source_root / "mcp_server" / ".venv" / "Lib" / "site-packages"
    for metadata_path in sorted(site_packages.glob("graphiti_core-*.dist-info/METADATA")):
        try:
            for line in read_text(metadata_path).splitlines():
                if line.startswith("Version: "):
                    return line.split(":", 1)[1].strip()
        except OSError:
            continue
    return None


def latest_stable_tag(source_root: Path) -> str | None:
    tags = git_value(source_root, "tag", "--list", "v*").splitlines()
    stable = [tag for tag in tags if re.fullmatch(r"v?\d+\.\d+\.\d+", tag.strip())]
    return max(stable, key=version_sort_key) if stable else None


def component_declared_version(source_root: Path) -> str | None:
    version_path = source_root / "VERSION"
    if version_path.exists():
        return read_text(version_path).strip() or None
    readme_path = source_root / "README.md"
    if readme_path.exists():
        match = re.search(r"Current project version:\s*`([^`]+)`", read_text(readme_path), re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def collect_components(generated_at: str) -> list[dict[str, object]]:
    components: list[dict[str, object]] = []
    verification_registry = load_verification_registry()
    upstream_observations = load_upstream_observations()
    for component in (
        codex_cli_component(generated_at, upstream_observations, verification_registry),
        zcode_desktop_component(generated_at, upstream_observations, verification_registry),
        openclaw_component(generated_at, upstream_observations, verification_registry),
    ):
        if component:
            components.append(component)
    browser_version, browser_source = distribution_source("browser-harness")
    if browser_version:
        source = browser_source or Path("")
        provenance = git_provenance(source) if browser_source else git_provenance(Path.cwd())
        components.append(
            {
                "id": "browser-harness",
                "declared_version": browser_version,
                "installed_version": browser_version,
                "available_version": upstream_observations.get("browser-harness", {}).get("available_version") or (latest_stable_tag(source) if browser_source else None),
                "upstream": observed_component_fields(upstream_observations.get("browser-harness"))["upstream"],
                "state": "installed",
                "source_path": str(browser_source or ""),
                "provenance": provenance,
                "license": discover_license(source, find_git_root(source)) if browser_source else {"status": "unknown", "file": "", "sha256": ""},
                "last_verified": generated_at,
                "verification": verification_registry.get("component:browser-harness", {"status": "not-recorded", "tests": [], "last_verified": None}),
                "rollback": {"kind": "git-commit", "ref": provenance.get("commit") or browser_version},
            }
        )

    graphiti_root = CODEX_HOME / "memory" / "graphiti" / "graphiti"
    if graphiti_root.exists():
        declared_version = None
        pyproject = graphiti_root / "pyproject.toml"
        if pyproject.exists():
            try:
                declared_version = str(tomllib.loads(read_text(pyproject)).get("project", {}).get("version") or "") or None
            except Exception:  # noqa: BLE001
                pass
        provenance = git_provenance(graphiti_root)
        installed_version = graphiti_installed_version(graphiti_root)
        components.append(
            {
                "id": "graphiti-core",
                "declared_version": declared_version,
                "installed_version": installed_version,
                "available_version": upstream_observations.get("graphiti-core", {}).get("available_version") or latest_stable_tag(graphiti_root),
                "upstream": observed_component_fields(upstream_observations.get("graphiti-core"))["upstream"],
                "state": "drift" if declared_version and installed_version and declared_version != installed_version else "installed",
                "source_path": str(graphiti_root),
                "provenance": provenance,
                "license": discover_license(graphiti_root, graphiti_root),
                "last_verified": generated_at,
                "verification": verification_registry.get("component:graphiti-core", {"status": "not-recorded", "tests": [], "last_verified": None}),
                "update_policy": "pin-and-defer-while-provider-unhealthy",
                "rollback": {"kind": "git-commit", "ref": provenance.get("commit") or installed_version},
            }
        )

    meta_root = HARNESS_HOME / "vendor" / "meta-harness"
    if meta_root.exists():
        version = component_declared_version(meta_root)
        provenance = git_provenance(meta_root)
        components.append(
            {
                "id": "meta-harness",
                "declared_version": version,
                "installed_version": version,
                "available_version": upstream_observations.get("meta-harness", {}).get("available_version") or latest_stable_tag(meta_root),
                "upstream": observed_component_fields(upstream_observations.get("meta-harness"))["upstream"],
                "state": "installed",
                "source_path": str(meta_root),
                "provenance": provenance,
                "license": discover_license(meta_root, meta_root),
                "last_verified": generated_at,
                "verification": verification_registry.get("component:meta-harness", {"status": "not-recorded", "tests": [], "last_verified": None}),
                "rollback": {"kind": "git-commit", "ref": provenance.get("commit") or version},
            }
        )
    ecc_root = HARNESS_HOME / "vendor" / "everything-claude-code"
    if ecc_root.exists():
        base_version = component_declared_version(ecc_root)
        provenance = git_provenance(ecc_root)
        components.append(
            {
                "id": "everything-claude-code-active-slice",
                "declared_version": base_version,
                "installed_version": "v2.1.0-frontmatter-compatible",
                "available_version": upstream_observations.get("everything-claude-code-active-slice", {}).get("available_version") or latest_stable_tag(ecc_root),
                "upstream": observed_component_fields(upstream_observations.get("everything-claude-code-active-slice"))["upstream"],
                "state": "targeted-local-patch",
                "source_path": str(ecc_root),
                "active_scope": ["agent-introspection-debugging", "codebase-onboarding", "context-budget"],
                "provenance": provenance,
                "license": discover_license(ecc_root, ecc_root),
                "last_verified": generated_at,
                "verification": verification_registry.get("component:everything-claude-code-active-slice", {"status": "not-recorded", "tests": [], "last_verified": None}),
                "update_policy": "targeted-diff-only",
                "rollback": {"kind": "git-commit", "ref": provenance.get("commit") or base_version},
            }
        )
    return components


def build_lock(entries: list[SkillEntry], plugins: list[PluginEntry], generated_at: str) -> dict:
    grouped: dict[str, list[SkillEntry]] = defaultdict(list)
    for entry in entries:
        if entry.has_skill_md:
            grouped[entry.real_path].append(entry)

    skills = []
    provenance_cache: dict[str, dict[str, object]] = {}
    verification_registry = load_verification_registry()
    for real_path, refs in sorted(grouped.items(), key=lambda item: item[0].lower()):
        primary = refs[0]
        root = find_git_root(Path(real_path))
        provenance_key = str(root) if root else "local"
        if provenance_key not in provenance_cache:
            provenance_cache[provenance_key] = git_provenance(Path(real_path))
        provenance = provenance_cache[provenance_key]
        verification = verification_registry.get(real_path) or verification_registry.get(primary.skill_id) or {
            "status": "not-recorded",
            "tests": [],
            "last_verified": None,
        }
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
                "provenance": provenance,
                "license": discover_license(Path(real_path), root),
                "local_patches": {
                    "dirty": provenance.get("dirty"),
                    "commits_ahead": provenance.get("ahead"),
                },
                "verification": verification,
                "rollback": {
                    "kind": "git-commit" if provenance.get("commit") else "content-hash",
                    "ref": provenance.get("commit") or primary.content_sha256,
                },
            }
        )

    return {
        "schema_version": 2,
        "generated_at": generated_at,
        "skills": skills,
        "plugins": [
            {
                "plugin_id": entry.plugin_id,
                "name": entry.name,
                "version": entry.version,
                "state": entry.state,
                "enabled_by_config": entry.enabled_by_config,
                "installed_remote": entry.installed_remote,
                "remote_plugin_id": entry.remote_plugin_id,
                "resolved": entry.resolved,
                "resolution_reason": entry.resolution_reason,
                "cache_source": entry.cache_source,
                "manifest_sha256": entry.manifest_sha256,
                "path": entry.path,
                "last_verified": generated_at,
                "rollback": {"kind": "manifest-hash", "ref": entry.manifest_sha256},
            }
            for entry in plugins
        ],
        "components": collect_components(generated_at),
    }


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def semantic_lock_payload(payload: dict) -> dict:
    def strip_observation_times(value):
        if isinstance(value, dict):
            return {
                key: strip_observation_times(item)
                for key, item in value.items()
                if key not in {"generated_at", "last_verified"}
            }
        if isinstance(value, list):
            return [strip_observation_times(item) for item in value]
        return value

    return strip_observation_times(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local inventory of shared and runtime-specific skills.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--lock-output", type=Path, default=DEFAULT_LOCK_OUTPUT)
    args = parser.parse_args()

    entries = build_entries()
    enabled_plugin_ids = load_enabled_plugin_ids()
    plugins = discover_plugin_entries(enabled_plugin_ids)
    plugin_skills = discover_resolved_plugin_skills(plugins)
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        "generated_at": generated_at,
        "roots": {**{name: str(path) for name, path in ROOTS.items()}, "plugin_cache": str(CODEX_PLUGIN_CACHE)},
        "summary": summarize(entries),
        "plugin_summary": summarize_plugins(plugins),
        "entries": [asdict(entry) for entry in entries],
        "plugins": [asdict(entry) for entry in plugins],
        "plugin_skills": [asdict(entry) for entry in plugin_skills],
        "enabled_plugin_ids": sorted(enabled_plugin_ids),
    }
    write_text_atomic(args.output, json.dumps(payload, ensure_ascii=False, indent=2))
    lock_payload = build_lock(entries, plugins, generated_at)
    if args.lock_output.exists():
        try:
            previous_payload = json.loads(read_text(args.lock_output))
        except (OSError, json.JSONDecodeError):
            previous_payload = None
        if previous_payload is not None and semantic_lock_payload(previous_payload) != semantic_lock_payload(lock_payload):
            previous_path = args.lock_output.with_name("harness.lock.previous.json")
            write_text_atomic(previous_path, json.dumps(previous_payload, ensure_ascii=False, indent=2))
    write_text_atomic(args.lock_output, json.dumps(lock_payload, ensure_ascii=False, indent=2))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.lock_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
