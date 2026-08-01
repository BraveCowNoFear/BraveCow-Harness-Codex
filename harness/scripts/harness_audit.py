from __future__ import annotations

import argparse
import json
import re
import sqlite3
import time
from datetime import UTC, datetime
from pathlib import Path

try:
    from .config_gate import check_config
    from .lock_diff import diff_locks
    from .memory_router import graphiti_ports_ready, route_memory
    from .memory_search import update_index
    from .memory_write_gate import validate_candidate
    from .skill_contracts import evaluate_contracts
except ImportError:  # direct script execution
    from config_gate import check_config
    from lock_diff import diff_locks
    from memory_router import graphiti_ports_ready, route_memory
    from memory_search import update_index
    from memory_write_gate import validate_candidate
    from skill_contracts import evaluate_contracts

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
LOCK_PATH = CODEX_HOME / "harness" / "catalog" / "harness.lock.json"
PREVIOUS_LOCK_PATH = CODEX_HOME / "harness" / "catalog" / "harness.lock.previous.json"
CONTRACTS_PATH = CODEX_HOME / "harness" / "catalog" / "skill-contracts.json"
VENDOR_DIR = CODEX_HOME / "harness" / "vendor"
MEMORY_INDEX_PATH = CODEX_HOME / "harness" / "index" / "memory-fts.sqlite3"
PROMPT_BASELINE_PATH = CODEX_HOME / "harness" / "catalog" / "prompt-baseline.json"
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


def load_lock() -> dict:
    if not LOCK_PATH.exists():
        return {}
    try:
        return json.loads(read_text(LOCK_PATH))
    except json.JSONDecodeError:
        return {"lock_error": "invalid JSON"}


def load_prompt_baseline() -> dict:
    if not PROMPT_BASELINE_PATH.exists():
        return {}
    try:
        return json.loads(read_text(PROMPT_BASELINE_PATH))
    except json.JSONDecodeError:
        return {"prompt_error": "invalid JSON"}


def collect_memory_index_status() -> dict:
    try:
        result = update_index(MEMORY_DIR, MEMORY_INDEX_PATH)
        connection = sqlite3.connect(MEMORY_INDEX_PATH)
        try:
            result["total_chunks"] = connection.execute("SELECT count(*) FROM memory_fts").fetchone()[0]
        finally:
            connection.close()
        result["status"] = "ready"
        return result
    except (OSError, sqlite3.Error) as exc:
        return {"status": "error", "diagnostic": str(exc)[:300]}


def collect_memory_status() -> list[tuple[str, bool]]:
    names = [
        "PROFILE.md",
        "ACTIVE.md",
        "MEMORY_POLICY.md",
        "SESSION_LOG.md",
        "LEARNINGS.md",
        "ERRORS.md",
        "FEATURE_REQUESTS.md",
    ]
    return [(name, (MEMORY_DIR / name).exists()) for name in names]


def collect_router_status() -> dict:
    try:
        result = route_memory(
            "what changed before the browser lifecycle rule",
            MEMORY_DIR,
            MEMORY_INDEX_PATH,
            limit=1,
            max_chars=512,
        )
        return result.get("decision", {})
    except (OSError, sqlite3.Error) as exc:
        return {"resolved": "error", "diagnostic": str(exc)[:300]}


def collect_write_gate_status() -> dict:
    return validate_candidate(
        {
            "content": "A reusable audit finding with explicit source, scope, confidence, expiry, and conflicts.",
            "reusable": True,
            "source": "harness self-test",
            "scope": "global",
            "target": "LEARNINGS.md",
            "confidence": 1.0,
            "expires_at": None,
            "conflicts": [],
        }
    )


def lock_coverage(lock: dict) -> dict:
    skills = lock.get("skills", [])
    total = len(skills)
    provenance_complete = sum(
        bool(item.get("content_sha256"))
        and bool(item.get("rollback", {}).get("ref"))
        and bool(item.get("provenance", {}).get("kind"))
        for item in skills
    )
    licenses_present = sum(item.get("license", {}).get("status") == "present" for item in skills)
    verified = sum(item.get("verification", {}).get("status") == "passed" for item in skills)
    return {
        "total": total,
        "provenance_complete": provenance_complete,
        "provenance_percent": round(provenance_complete / total * 100, 1) if total else 100.0,
        "licenses_present": licenses_present,
        "verified": verified,
    }


def collect_skill_contract_status(inventory: dict) -> dict:
    if not CONTRACTS_PATH.exists():
        return {"passed": False, "diagnostic": "skill-contracts.json missing"}
    try:
        suite = json.loads(read_text(CONTRACTS_PATH))
        return evaluate_contracts(inventory, suite)
    except (OSError, json.JSONDecodeError, re.error) as exc:
        return {"passed": False, "diagnostic": str(exc)[:300]}


def collect_lock_diff_status(lock: dict) -> dict:
    if not PREVIOUS_LOCK_PATH.exists():
        return {"status": "not-enough-snapshots", "total_changes": None}
    try:
        before = json.loads(read_text(PREVIOUS_LOCK_PATH))
        return {"status": "ready", **diff_locks(before, lock)}
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "error", "diagnostic": str(exc)[:300], "total_changes": None}


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
    config_gate = check_config(CONFIG_PATH, run_runtime=True)
    inventory = load_inventory()
    lock = load_lock()
    prompt_baseline = load_prompt_baseline()
    memory_index = collect_memory_index_status()
    router_status = collect_router_status()
    write_gate_status = collect_write_gate_status()
    coverage = lock_coverage(lock)
    contract_status = collect_skill_contract_status(inventory)
    lock_diff_status = collect_lock_diff_status(lock)
    summary = inventory.get("summary", {})
    plugin_summary = inventory.get("plugin_summary", {})
    plugins = inventory.get("plugins", [])
    counts = summary.get("counts", {})
    valid_counts = summary.get("valid_counts", {})
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
        f"- Config syntax gate: `{config_gate.get('syntax', 'unknown')}`",
        f"- Config runtime gate: `{config_gate.get('runtime', 'unknown')}`",
        f"- Codex CLI: `{config_gate.get('codex_version', 'unknown')}`",
    ]
    if prompt_baseline:
        skill_catalog = prompt_baseline.get("skill_catalog", {})
        lines.extend(
            [
                f"- Last measured startup prompt: `{prompt_baseline.get('total_tokens', 'unknown')}` tokens",
                f"- Skill descriptions: `{skill_catalog.get('description_tokens', 'unknown')}` tokens across `{skill_catalog.get('entries', 'unknown')}` catalog entries",
                f"- Prompt probe mode: `{prompt_baseline.get('probe_mode', 'unknown')}`",
            ]
        )
    if config.get("config_error"):
        lines.append(f"- Config read error: `{config['config_error']}`")
    if config_gate.get("diagnostic"):
        lines.append(f"- Config gate diagnostic: `{config_gate['diagnostic']}`")

    lines.extend(["", "## Memory Entry Points", ""])
    for name, exists in collect_memory_status():
        lines.append(f"- `{name}`: {'present' if exists else 'missing'}")
    lines.extend(
        [
            f"- SQLite FTS5 index: `{memory_index.get('status', 'unknown')}`",
            f"- Indexed Markdown files: `{memory_index.get('scanned', 0)}`",
            f"- Indexed sections: `{memory_index.get('total_chunks', 0)}`",
            f"- Incremental updates this run: `{memory_index.get('updated', 0)}`",
            f"- Retrieval router result: `{router_status.get('resolved', 'unknown')}`",
            f"- Retrieval degradation latency: `{router_status.get('latency_ms', 'unknown')} ms`",
            f"- Durable-memory write gate: `{write_gate_status.get('decision', 'unknown')}`; writes performed: `{write_gate_status.get('write_performed', False)}`",
            f"- Graphiti passive port health: `{'ready' if graphiti_ports_ready() else 'unavailable'}` (no service startup attempted)",
        ]
    )

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
            f"- Valid shared skills: `{valid_counts.get('shared', 0)}`",
            f"- Valid Codex skills: `{valid_counts.get('codex', 0)}`",
            f"- Valid OpenClaw skills: `{valid_counts.get('openclaw', 0)}`",
            f"- Unique discoverable real paths: `{summary.get('unique_discoverable_real_paths', 0)}`",
            f"- Entries declaring a version: `{summary.get('declared_version_count', 0)}`",
            f"- Trigger contract: `{contract_status.get('failed_cases', 'unknown')}/{contract_status.get('cases', 'unknown')} failed ({contract_status.get('failure_percent', 'unknown')}%)`; passed: `{contract_status.get('passed', False)}`",
            f"- Harness lock skills: `{len(lock.get('skills', []))}`",
            f"- Harness lock plugins: `{len(lock.get('plugins', []))}`",
            f"- Harness lock components: `{len(lock.get('components', []))}`",
            f"- Previous-lock drift snapshot: `{lock_diff_status.get('status', 'unknown')}`; changes: `{lock_diff_status.get('total_changes', 'unknown')}`",
            f"- Provenance + rollback coverage: `{coverage.get('provenance_complete', 0)}/{coverage.get('total', 0)} ({coverage.get('provenance_percent', 0)}%)`",
            f"- Skills with detected license files: `{coverage.get('licenses_present', 0)}/{coverage.get('total', 0)}`",
            f"- Skills with recorded passing verification: `{coverage.get('verified', 0)}/{coverage.get('total', 0)}`",
            "",
            "## Codex Plugin Cache",
            "",
            "Remote install markers and exact config ids choose one resolved package per logical plugin. Other cache entries remain rollback evidence.",
            "",
            f"- Cached plugin packages: `{plugin_summary.get('packages', 0)}`",
            f"- Plugin-provided skills: `{plugin_summary.get('skills', 0)}`",
            f"- Packages with apps: `{plugin_summary.get('with_apps', 0)}`",
            f"- Packages with MCP content: `{plugin_summary.get('with_mcp', 0)}`",
            f"- Invalid plugin manifests: `{plugin_summary.get('invalid_manifests', 0)}`",
            f"- Enabled by config: `{plugin_summary.get('enabled_by_config', 0)}`",
            f"- Installed through remote markers: `{plugin_summary.get('installed_remote', 0)}`",
            f"- Resolved logical plugins: `{plugin_summary.get('resolved', 0)}`",
            f"- Resolved plugin skill entries: `{plugin_summary.get('resolved_skill_entries', 0)}`",
            f"- Cache-only packages: `{plugin_summary.get('cache_only', 0)}`",
        ]
    )

    for item in plugins:
        skill_ids = ", ".join(item.get("skill_ids", [])) or "none"
        lines.append(
            f"- `{item.get('name', 'unknown')}@{item.get('version', 'unknown')}` "
            f"from `{item.get('cache_source', 'unknown')}`; state: `{item.get('state', 'unknown')}`; "
            f"resolved: `{item.get('resolved', False)}`; reason: `{item.get('resolution_reason', 'unknown')}`; skills: `{skill_ids}`"
        )

    lines.extend(["", "## Pinned Components", ""])
    for component in lock.get("components", []):
        lines.append(
            f"- `{component.get('id', 'unknown')}`: declared `{component.get('declared_version', 'unknown')}`, "
            f"installed `{component.get('installed_version', 'unknown')}`, state `{component.get('state', 'unknown')}`, "
            f"rollback `{component.get('rollback', {}).get('ref', 'unknown')}`"
        )

    lines.extend(
        [
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
            "- Use Markdown plus SQLite FTS5 as the default local memory path; keep graph/vector retrieval optional.",
            "- Treat the generated harness lock as observation evidence, not authorization to auto-update.",
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
