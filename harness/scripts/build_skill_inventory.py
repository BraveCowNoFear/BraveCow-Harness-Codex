from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


HOME = Path.home()
CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))
AGENTS_HOME = Path(os.environ.get("AGENTS_HOME", HOME / ".agents"))
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", HOME / ".openclaw"))
SHARED_SKILLS_HOME = Path(os.environ.get("SHARED_SKILLS_HOME", AGENTS_HOME / "skills"))

ROOTS = {
    "shared": SHARED_SKILLS_HOME,
    "codex": CODEX_HOME / "skills",
    "openclaw": OPENCLAW_HOME / "skills",
}

DEFAULT_OUTPUT = CODEX_HOME / "harness" / "catalog" / "skill-inventory.json"


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


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_frontmatter(text: str) -> tuple[str | None, str | None]:
    if not text.startswith("---"):
        return None, None
    lines = text.splitlines()
    name = None
    description = None
    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if not in_frontmatter or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key == "name":
            name = value or None
        elif key == "description":
            description = value or None
    return name, description


def iter_skill_dirs(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return sorted([path for path in root.iterdir() if path.is_dir()], key=lambda p: p.name.lower())


def build_entries() -> list[SkillEntry]:
    entries: list[SkillEntry] = []
    for runtime, root in ROOTS.items():
        for skill_dir in iter_skill_dirs(root):
            skill_md = skill_dir / "SKILL.md"
            name = None
            description = None
            if skill_md.exists():
                name, description = parse_frontmatter(read_text(skill_md))
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
        "missing_shared_links": {runtime: sorted(ids) for runtime, ids in missing_links.items()},
        "shared_mirrors": dict(sorted(shared_mirrors.items())),
        "shadowed_shared_skills": {
            runtime: sorted(items, key=lambda item: str(item["skill_id"]).lower())
            for runtime, items in shadowed_shared_skills.items()
        },
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
    args = parser.parse_args()

    entries = build_entries()
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "roots": {name: str(path) for name, path in ROOTS.items()},
        "summary": summarize(entries),
        "entries": [asdict(entry) for entry in entries],
    }
    write_text_atomic(args.output, json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
