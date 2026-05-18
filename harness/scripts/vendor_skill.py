from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path


HOME = Path.home()
CODEX_HOME = Path(__import__("os").environ.get("CODEX_HOME", HOME / ".codex"))
VENDOR_ROOT = CODEX_HOME / "harness" / "vendor"


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._").lower()
    return cleaned or "unnamed-resource"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a quarantined vendor manifest.")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--kind",
        choices=[
            "skill",
            "plugin",
            "framework",
            "runtime",
            "model",
            "tooling",
            "marketplace",
            "registry",
            "specification",
        ],
        default="skill",
    )
    parser.add_argument("--slug")
    parser.add_argument("--reference-url", action="append", default=[])
    parser.add_argument("--license")
    parser.add_argument("--why")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    slug = args.slug or slugify(args.title)
    target_dir = VENDOR_ROOT / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "title": args.title,
        "slug": slug,
        "kind": args.kind,
        "source_url": args.source_url,
        "reference_urls": args.reference_url,
        "license": args.license,
        "why_it_matters": args.why,
        "captured_at": datetime.now(UTC).isoformat(),
        "review_status": "pending",
        "activation_state": "quarantined",
        "notes": args.notes,
    }

    (target_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    notes_lines = [
        "# Quarantined Import",
        "",
        f"- Title: {args.title}",
        f"- Kind: {args.kind}",
        f"- Source: {args.source_url}",
    ]
    for url in args.reference_url:
        notes_lines.append(f"- Reference: {url}")
    if args.license:
        notes_lines.append(f"- License: {args.license}")
    if args.why:
        notes_lines.append(f"- Why it matters: {args.why}")
    notes_lines.extend(["- Review status: pending", "- Activation state: quarantined"])
    if args.notes:
        notes_lines.append(f"- Notes: {args.notes}")
    (target_dir / "NOTES.md").write_text("\n".join(notes_lines) + "\n", encoding="utf-8")
    print(f"Prepared {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

