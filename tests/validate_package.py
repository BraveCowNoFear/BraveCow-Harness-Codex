from __future__ import annotations

import py_compile
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "VERSION",
    "README.md",
    "README.zh-CN.md",
    "install.ps1",
    "install.sh",
    "requirements-dev.txt",
    "harness/README.md",
    "docs/automation-subsystems.md",
    "docs/onboarding.md",
    ".github/workflows/ci.yml",
    "harness/scripts/build_skill_inventory.py",
    "harness/scripts/harness_audit.py",
    "harness/scripts/config_gate.py",
    "harness/scripts/memory_search.py",
    "harness/scripts/memory_router.py",
    "harness/scripts/lock_diff.py",
    "harness/scripts/memory_write_gate.py",
    "harness/scripts/skill_contracts.py",
    "harness/scripts/export_runtime_snapshot.py",
    "harness/scripts/measure_prompt_baseline.py",
    "harness/catalog/skill-contracts.example.json",
    "harness/catalog/verification.example.json",
    "harness/catalog/upstream-observations.example.json",
    "harness/scripts/vendor_skill.py",
    "harness/scripts/runtime_paths.py",
    "harness/scripts/start_onboarding.py",
    "harness/scripts/start_onboarding.ps1",
    "harness/scripts/start_onboarding.sh",
    "skills/agent-harness-introspect/SKILL.md",
    "skills/bravecow-onboarding/SKILL.md",
    "skills/bravecow-onboarding/references/curriculum.md",
    "skills/bravecow-onboarding/references/video-distillation-BV1dFTv6yEcZ.md",
    "skills/bravecow-onboarding/assets/community-book-fair.md",
    "templates/zcode/commands/bravecow-onboarding.md",
    "templates/AGENTS.snippet.md",
    "templates/memories/PROFILE.md",
    "templates/memories/ACTIVE.md",
    "templates/memories/MEMORY_POLICY.md",
    "templates/memories/SESSION_LOG.md",
    "templates/memories/LEARNINGS.md",
    "templates/memories/ERRORS.md",
    "templates/memories/FEATURE_REQUESTS.md",
    "tests/smoke_install.ps1",
    "tests/smoke_install_macos.sh",
    "tests/test_onboarding_launcher.py",
    "tests/test_runtime_paths.py",
]

LOCAL_USER = "Clr"

FORBIDDEN_PATTERNS = [
    r"C:\\Users\\" + LOCAL_USER,
    r"C:/Users/" + LOCAL_USER,
    r"\\\.codex\\vault",
    r"/\.codex/vault",
    r"PERSONAL_PROFILE\.md",
    r"gho_[A-Za-z0-9_]+",
    r"sk-[A-Za-z0-9_-]{20,}",
    r"1649392148@qq\.com",
]

TEXT_SUFFIXES = {".md", ".txt", ".ps1", ".sh", ".py", ".toml", ".json", ".yml", ".yaml", ".csv", ".gitignore", ""}


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in {".git", ".research", "output", "tmp", "__pycache__"} for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            files.append(path)
    return files


def main() -> int:
    failures: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")

    for path in [
        ROOT / "harness/scripts/build_skill_inventory.py",
        ROOT / "harness/scripts/harness_audit.py",
        ROOT / "harness/scripts/memory_router.py",
        ROOT / "harness/scripts/lock_diff.py",
        ROOT / "harness/scripts/memory_write_gate.py",
        ROOT / "harness/scripts/skill_contracts.py",
        ROOT / "harness/scripts/export_runtime_snapshot.py",
        ROOT / "harness/scripts/measure_prompt_baseline.py",
        ROOT / "harness/scripts/vendor_skill.py",
        ROOT / "harness/scripts/runtime_paths.py",
        ROOT / "harness/scripts/start_onboarding.py",
    ]:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"python compile failed for {path.relative_to(ROOT)}: {exc.msg}")

    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"not utf-8: {path.relative_to(ROOT)}")
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text):
                failures.append(f"forbidden pattern {pattern!r} in {path.relative_to(ROOT)}")

    vendor_children = [path for path in (ROOT / "harness/vendor").iterdir() if path.name != ".gitkeep"]
    if vendor_children:
        failures.append("harness/vendor must stay empty except .gitkeep")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print("OK: package validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
