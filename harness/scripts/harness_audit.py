from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


HOME = Path.home()
CODEX_HOME = Path(__import__("os").environ.get("CODEX_HOME", HOME / ".codex"))
CONFIG_PATH = CODEX_HOME / "config.toml"
MEMORY_DIR = CODEX_HOME / "memories"
AGENTS_DIR = CODEX_HOME / "agents"
AUTOMATIONS_DIR = CODEX_HOME / "automations"
INVENTORY_PATH = CODEX_HOME / "harness" / "catalog" / "skill-inventory.json"
VENDOR_DIR = CODEX_HOME / "harness" / "vendor"
DEFAULT_OUTPUT = CODEX_HOME / "harness" / "reports" / "agent-harness-audit.md"


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_inventory() -> dict:
    if not INVENTORY_PATH.exists():
        return {}
    last_error: json.JSONDecodeError | None = None
    for _ in range(3):
        try:
            return json.loads(read_text(INVENTORY_PATH))
        except json.JSONDecodeError as exc:
            last_error = exc
            time.sleep(0.2)
    if last_error is not None:
        raise RuntimeError(f"Failed to parse inventory at {INVENTORY_PATH}: {last_error}") from last_error
    return {}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return tomllib.loads(read_text(CONFIG_PATH))
    except Exception as exc:  # noqa: BLE001
        return {"config_error": str(exc)}


def collect_memory_status() -> list[tuple[str, bool]]:
    names = ["PROFILE.md", "ACTIVE.md", "LEARNINGS.md", "ERRORS.md", "FEATURE_REQUESTS.md"]
    return [(name, (MEMORY_DIR / name).exists()) for name in names]


def collect_agent_profiles() -> list[str]:
    if not AGENTS_DIR.exists():
        return []
    return sorted(path.stem for path in AGENTS_DIR.glob("*.toml"))


def collect_automations() -> list[str]:
    if not AUTOMATIONS_DIR.exists():
        return []
    return sorted(path.name for path in AUTOMATIONS_DIR.iterdir() if path.is_dir())


def collect_vendor_candidates() -> list[dict]:
    candidates: list[dict] = []
    if not VENDOR_DIR.exists():
        return candidates
    for manifest_path in sorted(VENDOR_DIR.glob("*/manifest.json")):
        try:
            candidates.append(json.loads(read_text(manifest_path)))
        except json.JSONDecodeError:
            candidates.append(
                {
                    "title": manifest_path.parent.name,
                    "slug": manifest_path.parent.name,
                    "kind": "unknown",
                    "review_status": "invalid-manifest",
                    "activation_state": "quarantined",
                }
            )
    return candidates


def collect_unmanifested_vendor_dirs() -> list[str]:
    if not VENDOR_DIR.exists():
        return []
    missing: list[str] = []
    for path in sorted(VENDOR_DIR.iterdir()):
        if not path.is_dir():
            continue
        if path.name.startswith("."):
            continue
        if not (path / "manifest.json").exists():
            missing.append(path.name)
    return missing


def render_report() -> str:
    config = load_config()
    inventory = load_inventory()
    summary = inventory.get("summary", {})
    counts = summary.get("counts", {})
    missing_links = summary.get("missing_shared_links", {})
    shared_mirrors = summary.get("shared_mirrors", {})
    shadowed_shared = summary.get("shadowed_shared_skills", {})
    codex_shadow_ids = [item["skill_id"] for item in shadowed_shared.get("codex", [])]
    openclaw_shadow_ids = [item["skill_id"] for item in shadowed_shared.get("openclaw", [])]
    codex_mirrors = [
        skill_id
        for skill_id, payload in shared_mirrors.items()
        if any(ref.get("runtime") == "codex" for ref in payload.get("refs", []))
    ]
    openclaw_mirrors = [
        skill_id
        for skill_id, payload in shared_mirrors.items()
        if any(ref.get("runtime") == "openclaw" for ref in payload.get("refs", []))
    ]
    vendor_candidates = collect_vendor_candidates()
    pending_vendor = [item for item in vendor_candidates if item.get("review_status") == "pending"]
    unmanifested_vendor_dirs = collect_unmanifested_vendor_dirs()

    lines = [
        "# Agent Harness Audit",
        "",
        f"Generated: {datetime.now(UTC).isoformat()}",
        "",
        "## Runtime",
        "",
        f"- Model: `{config.get('model', 'unknown')}`",
        f"- Reasoning effort: `{config.get('model_reasoning_effort', 'unknown')}`",
        f"- Approval policy: `{config.get('approval_policy', 'unknown')}`",
        f"- Sandbox mode: `{config.get('sandbox_mode', 'unknown')}`",
    ]
    if config.get("config_error"):
        lines.append(f"- Config read error: `{config['config_error']}`")

    lines.extend(["", "## Memory Entry Points", ""])
    for name, exists in collect_memory_status():
        lines.append(f"- `{name}`: {'present' if exists else 'missing'}")

    lines.extend(["", "## Agent Profiles", ""])
    profiles = collect_agent_profiles()
    if profiles:
        lines.extend(f"- `{profile}`" for profile in profiles)
    else:
        lines.append("- `none`")

    lines.extend(["", "## Automations", ""])
    automations = collect_automations()
    if automations:
        lines.extend(f"- `{automation}`" for automation in automations)
    else:
        lines.append("- `none`")

    lines.extend(
        [
            "",
            "## Skill Coverage",
            "",
            f"- Shared skills: `{counts.get('shared', 0)}`",
            f"- Codex skill entries: `{counts.get('codex', 0)}`",
            f"- OpenClaw skill entries: `{counts.get('openclaw', 0)}`",
            "",
            "## Shared Mirrors",
            "",
            f"- Mirrored into Codex via shared path: `{len(codex_mirrors)}`",
            f"- Mirrored into OpenClaw via shared path: `{len(openclaw_mirrors)}`",
            "",
            "## Missing Shared Links",
            "",
            f"- Missing in Codex: `{', '.join(missing_links.get('codex', [])) or 'none'}`",
            f"- Missing in OpenClaw: `{', '.join(missing_links.get('openclaw', [])) or 'none'}`",
            "",
            "## Shared Skill Shadows",
            "",
            f"- Codex local copies of shared skill ids: `{', '.join(codex_shadow_ids) or 'none'}`",
            f"- OpenClaw local copies of shared skill ids: `{', '.join(openclaw_shadow_ids) or 'none'}`",
            "",
            "## Vendor Quarantine",
            "",
            f"- Quarantined candidates: `{len(vendor_candidates)}`",
            f"- Pending review: `{len(pending_vendor)}`",
            f"- Vendor dirs missing manifest: `{', '.join(unmanifested_vendor_dirs) or 'none'}`",
        ]
    )

    for item in vendor_candidates:
        lines.append(
            f"- `{item.get('slug', 'unknown')}`: `{item.get('kind', 'unknown')}` / "
            f"`{item.get('review_status', 'unknown')}` / `{item.get('activation_state', 'unknown')}`"
        )

    lines.extend(
        [
            "",
            "## Baseline Guidance",
            "",
            "- Keep private runtime state out of Git.",
            "- Prefer shared skills and runtime junctions over copied duplicates.",
            "- Catalog external resources before activation.",
            "- Treat this report as local state, not a portable artifact.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a point-in-time harness audit report.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = render_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

