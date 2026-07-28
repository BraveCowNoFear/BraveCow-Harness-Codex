from __future__ import annotations

import argparse
import json
import socket
import time
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from .memory_search import DEFAULT_DB, DEFAULT_MEMORY_DIR, read_text, search, update_index
except ImportError:  # direct script execution
    from memory_search import DEFAULT_DB, DEFAULT_MEMORY_DIR, read_text, search, update_index


TEMPORAL_TERMS = ("when", "before", "after", "timeline", "history", "changed", "何时", "之前", "之后", "时间线", "历史", "变化")
RELATION_TERMS = ("relationship", "related", "depends", "caused", "entity", "关系", "关联", "依赖", "导致", "实体")
SEMANTIC_TERMS = ("similar", "concept", "meaning", "why", "analogy", "相似", "概念", "含义", "为什么", "类比")


@dataclass
class RouteDecision:
    requested: str
    resolved: str
    reason: str
    degraded: bool
    graphiti_ready: bool | None
    latency_ms: float


def classify_query(query: str, source: str | None = None) -> str:
    if source:
        return "direct"
    lowered = query.lower()
    if any(term in lowered for term in TEMPORAL_TERMS + RELATION_TERMS):
        return "graph"
    if any(term in lowered for term in SEMANTIC_TERMS):
        return "semantic"
    return "fts"


def graphiti_ports_ready(host: str = "127.0.0.1", ports: tuple[int, ...] = (8000, 6379), timeout: float = 0.25) -> bool:
    for port in ports:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                pass
        except OSError:
            return False
    return True


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
    graphiti_ready: bool | None = None
    degraded = False
    reason = "canonical Markdown source requested"

    if requested == "direct":
        evidence = direct_evidence(memory_dir, source or "", max_chars)
        resolved = "direct" if evidence else "fts"
        if not evidence:
            degraded = True
            reason = "requested Markdown source was unavailable; used FTS5"
    else:
        evidence = []
        resolved = requested

    if requested == "graph":
        graphiti_ready = graphiti_ports_ready()
        if graphiti_ready:
            resolved = "graphiti-ready"
            reason = "temporal/relationship query; Graphiti ports are already healthy"
        else:
            resolved = "fts"
            degraded = True
            reason = "Graphiti unavailable; immediate local FTS5 fallback without service startup"
    elif requested == "semantic":
        resolved = "fts"
        degraded = True
        reason = "no local vector adapter configured; used bounded FTS5 evidence"
    elif requested == "fts":
        reason = "ordinary exact/sub-string query"

    index = update_index(memory_dir, db_path)
    if not evidence:
        evidence = [asdict(hit) for hit in search(query, db_path, limit)]
    evidence = bounded_hits(evidence, max_chars)
    elapsed_ms = (time.perf_counter() - started) * 1000
    decision = RouteDecision(requested, resolved, reason, degraded, graphiti_ready, round(elapsed_ms, 2))
    return {
        "decision": asdict(decision),
        "index": index,
        "evidence": evidence,
        "evidence_chars": sum(len(str(item.get("snippet", ""))) for item in evidence),
        "max_evidence_chars": max_chars,
        "graphiti_handoff_required": resolved == "graphiti-ready",
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
