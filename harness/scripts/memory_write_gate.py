from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


ALLOWED_TARGETS = {
    "PROFILE.md",
    "ACTIVE.md",
    "LEARNINGS.md",
    "ERRORS.md",
    "FEATURE_REQUESTS.md",
    "SESSION_LOG.md",
}
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bgh[opusr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)(api[_ -]?key|password|secret)\s*[:=]\s*\S+"),
)


def validate_candidate(candidate: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    required = ("content", "reusable", "source", "scope", "target", "confidence", "conflicts")
    for field in required:
        if field not in candidate:
            errors.append(f"missing:{field}")

    content = str(candidate.get("content", "")).strip()
    if len(content) < 20:
        errors.append("content-too-short")
    if any(pattern.search(content) for pattern in SECRET_PATTERNS):
        errors.append("possible-secret")
    if candidate.get("reusable") is not True:
        errors.append("not-reusable")
    if not str(candidate.get("source", "")).strip():
        errors.append("source-required")
    if candidate.get("scope") not in {"global", "project", "session"}:
        errors.append("invalid-scope")
    if candidate.get("target") not in ALLOWED_TARGETS:
        errors.append("invalid-target")
    try:
        confidence = float(candidate.get("confidence"))
        if not 0 <= confidence <= 1:
            errors.append("confidence-out-of-range")
        elif confidence < 0.7:
            warnings.append("low-confidence")
    except (TypeError, ValueError):
        errors.append("invalid-confidence")
    if not isinstance(candidate.get("conflicts"), list):
        errors.append("conflicts-must-be-list")
    elif candidate.get("conflicts"):
        warnings.append("conflict-review-required")

    expires_at = candidate.get("expires_at")
    if expires_at:
        try:
            datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
        except ValueError:
            errors.append("invalid-expiry")
    elif candidate.get("target") in {"ACTIVE.md", "SESSION_LOG.md"}:
        warnings.append("expiry-not-declared")

    decision = "reject" if errors else ("review" if warnings else "accept")
    return {
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "write_performed": False,
        "note": "This gate validates only; canonical memory is never written automatically.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a proposed durable-memory write without writing it.")
    parser.add_argument("candidate", nargs="?", type=Path, help="JSON candidate file; omit to read stdin")
    args = parser.parse_args()
    try:
        raw = args.candidate.read_text(encoding="utf-8-sig") if args.candidate else sys.stdin.read()
        candidate = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "reject", "errors": [f"invalid-input:{exc}"], "write_performed": False}))
        return 2
    result = validate_candidate(candidate)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["decision"] != "reject" else 2


if __name__ == "__main__":
    raise SystemExit(main())
