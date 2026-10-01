from __future__ import annotations

import argparse
import json
import re
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from .memory_search import DEFAULT_DB, DEFAULT_MEMORY_DIR, read_text, search, update_index, normalize_query
except ImportError:  # direct script execution
    from memory_search import DEFAULT_DB, DEFAULT_MEMORY_DIR, read_text, search, update_index, normalize_query


SEMANTIC_TERMS = ("similar", "concept", "meaning", "why", "analogy", "相似", "概念", "含义", "为什么", "类比")


@dataclass
class RouteDecision:
    requested: str
    resolved: str
    reason: str
    degraded: bool
    latency_ms: float


def classify_query(query: str, source: str | None = None) -> str:
    if source:
        return "direct"
    lowered = query.lower()
    if any(term in lowered for term in SEMANTIC_TERMS):
        return "semantic"
    return "fts"


def bounded_hits(hits: list[dict], max_chars: int) -> list[dict]:
    budget = max(1, max_chars)
    output: list[dict] = []
    used = 0
    for hit in hits:
        item = dict(hit)
        snippet = str(item.get("snippet", ""))
        remaining = budget - used
        if remaining <= 0:
            break
        item["snippet"] = snippet[:remaining]
        output.append(item)
        used += len(item["snippet"])
    return output


def direct_evidence(memory_dir: Path, source: str, max_chars: int) -> list[dict]:
    candidate = (memory_dir / source).resolve()
    root = memory_dir.resolve()
    if root not in candidate.parents or candidate.suffix.lower() != ".md" or not candidate.is_file():
        return []
    text = read_text(candidate)[: max(1, max_chars)]
    return [{"source": candidate.name, "section": "direct", "score": 0.0, "snippet": text}]


def markdown_fallback(query: str, memory_dir: Path, limit: int, max_chars: int) -> tuple[list[dict], dict]:
    """Bounded literal search: no database, network, writes, or executable query syntax."""
    terms = re.findall(r'"([^"]+)"', normalize_query(query))
    terms = [term.casefold() for term in terms if term]
    hits: list[dict] = []
    scanned = skipped = total_bytes = attempted = 0
    max_files, max_bytes = 64, 4 * 1024 * 1024
    truncated = False
    root = memory_dir.resolve()
    try:
        candidates = sorted(memory_dir.iterdir())
    except OSError:
        return [], {"scanned_files": 0, "scanned_bytes": 0, "skipped_files": 0,
                    "bounded": True, "truncated": False, "root_unavailable": True}
    for path in candidates:
        if path.suffix.lower() != ".md":
            continue
        if attempted >= max_files or total_bytes >= max_bytes:
            truncated = True
            break
        attempted += 1
        try:
            if root not in path.resolve().parents:
                skipped += 1
                continue
            remaining = max_bytes - total_bytes
            with path.open("rb") as stream:
                raw = stream.read(remaining)
                truncated = truncated or bool(stream.read(1))
            total_bytes += len(raw)
            scanned += 1
            text = raw.decode("utf-8-sig")
        except (OSError, UnicodeError):
            skipped += 1
            continue
        lowered = text.casefold()
        positions = [lowered.find(term) for term in terms if term in lowered]
        if not positions:
            continue
        start = max(0, min(positions) - 80)
        hits.append({"source": path.name, "section": "literal-fallback", "score": 0.0,
                     "snippet": text[start:start + min(512, max_chars)]})
        if len(hits) >= max(1, min(limit, 50)):
            truncated = True
            break
    return hits, {"scanned_files": scanned, "attempted_files": attempted, "scanned_bytes": total_bytes,
                  "skipped_files": skipped, "bounded": True, "truncated": truncated}


def route_memory(
    query: str,
    memory_dir: Path = DEFAULT_MEMORY_DIR,
    db_path: Path = DEFAULT_DB,
    limit: int = 6,
    max_chars: int = 8000,
    source: str | None = None,
) -> dict:
    started = time.perf_counter()
    requested = classify_query(query, source)
    degraded = False
    reason = "canonical Markdown source requested"

    if requested == "direct":
        try:
            evidence = direct_evidence(memory_dir, source or "", max_chars)
        except (OSError, UnicodeError):
            evidence = []
        resolved = "direct" if evidence else "fts"
        if not evidence:
            degraded = True
            reason = "requested Markdown source was unavailable; used FTS5"
    else:
        evidence = []
        resolved = requested

    if requested == "semantic":
        resolved = "fts"
        degraded = True
        reason = "no local vector adapter configured; used bounded FTS5 evidence"
    elif requested == "fts":
        reason = "ordinary exact/sub-string query"

    index: dict = {"status": "skipped-direct"}
    if resolved != "direct":
        try:
            index = update_index(memory_dir, db_path)
            evidence = [asdict(hit) for hit in search(query, db_path, limit, strict=True)]
        except (OSError, sqlite3.Error, UnicodeError) as exc:
            index = {"status": "unavailable", "error_type": type(exc).__name__}
            degraded = True
            reason = "local index unavailable; used bounded canonical Markdown scan"
        short_terms = any(0 < len(term) < 3 for term in re.findall(r'"([^"]+)"', normalize_query(query)))
        if index.get("status") == "unavailable" or (not evidence and short_terms):
            evidence, scan = markdown_fallback(query, memory_dir, limit, max(1, max_chars))
            index["fallback"] = scan
            resolved = "markdown-scan"
            degraded = True
            if short_terms and index.get("status") != "unavailable":
                reason = "trigram cannot match short terms; used bounded literal Markdown scan"
    evidence = bounded_hits(evidence, max_chars)
    elapsed_ms = (time.perf_counter() - started) * 1000
    decision = RouteDecision(requested, resolved, reason, degraded, round(elapsed_ms, 2))
    return {
        "decision": asdict(decision),
        "index": index,
        "evidence": evidence,
        "evidence_chars": sum(len(str(item.get("snippet", ""))) for item in evidence),
        "max_evidence_chars": max_chars,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Route memory lookup to the cheapest sufficient, degradable backend.")
    parser.add_argument("query")
    parser.add_argument("--memory-dir", type=Path, default=DEFAULT_MEMORY_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--source", help="Known canonical Markdown filename, for example ACTIVE.md")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--max-chars", type=int, default=8000)
    args = parser.parse_args()
    payload = route_memory(args.query, args.memory_dir, args.db, args.limit, args.max_chars, args.source)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
