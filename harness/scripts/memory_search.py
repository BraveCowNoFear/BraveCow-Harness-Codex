from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from .runtime_paths import HARNESS_HOME, MEMORY_HOME
except ImportError:  # direct script execution
    from runtime_paths import HARNESS_HOME, MEMORY_HOME


DEFAULT_MEMORY_DIR = MEMORY_HOME
DEFAULT_DB = HARNESS_HOME / "index" / "memory-fts.sqlite3"


@dataclass
class SearchHit:
    source: str
    section: str
    score: float
    snippet: str


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_markdown(text: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    heading = "Document"
    body: list[str] = []

    def flush() -> None:
        content = "\n".join(body).strip()
        if content:
            chunks.append((heading, content))

    for line in text.splitlines():
        match = re.match(r"^#{1,4}\s+(.+?)\s*$", line)
        if match:
            flush()
            heading = match.group(1).strip()
            body = []
        else:
            body.append(line)
    flush()
    return chunks


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS files (
            source TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL,
            mtime_ns INTEGER NOT NULL,
            size INTEGER NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            source UNINDEXED,
            section,
            content,
            tokenize='trigram'
        );
        """
    )
    return connection


def iter_markdown_files(memory_dir: Path) -> list[Path]:
    if not memory_dir.exists():
        return []
    return sorted(path for path in memory_dir.glob("*.md") if path.is_file())


def update_index(memory_dir: Path = DEFAULT_MEMORY_DIR, db_path: Path = DEFAULT_DB, rebuild: bool = False) -> dict:
    if rebuild and db_path.exists():
        db_path.unlink()
    connection = connect(db_path)
    scanned = updated = unchanged = removed = chunks = 0
    current_sources: set[str] = set()
    try:
        for path in iter_markdown_files(memory_dir):
            scanned += 1
            source = path.name
            current_sources.add(source)
            stat = path.stat()
            row = connection.execute(
                "SELECT content_hash, mtime_ns, size FROM files WHERE source = ?", (source,)
            ).fetchone()
            if row and row[1] == stat.st_mtime_ns and row[2] == stat.st_size:
                unchanged += 1
                continue

            text = read_text(path)
            digest = content_hash(text)
            if row and row[0] == digest:
                connection.execute(
                    "UPDATE files SET mtime_ns = ?, size = ? WHERE source = ?",
                    (stat.st_mtime_ns, stat.st_size, source),
                )
                unchanged += 1
                continue

            connection.execute("DELETE FROM memory_fts WHERE source = ?", (source,))
            sections = split_markdown(text)
            connection.executemany(
                "INSERT INTO memory_fts(source, section, content) VALUES (?, ?, ?)",
                [(source, section, content) for section, content in sections],
            )
            connection.execute(
                "INSERT INTO files(source, content_hash, mtime_ns, size) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(source) DO UPDATE SET content_hash=excluded.content_hash, "
                "mtime_ns=excluded.mtime_ns, size=excluded.size",
                (source, digest, stat.st_mtime_ns, stat.st_size),
            )
            updated += 1
            chunks += len(sections)

        stale = [
            row[0]
            for row in connection.execute("SELECT source FROM files").fetchall()
            if row[0] not in current_sources
        ]
        for source in stale:
            connection.execute("DELETE FROM memory_fts WHERE source = ?", (source,))
            connection.execute("DELETE FROM files WHERE source = ?", (source,))
            removed += 1
        connection.commit()
    finally:
        connection.close()
    return {
        "database": str(db_path),
        "memory_dir": str(memory_dir),
        "scanned": scanned,
        "updated": updated,
        "unchanged": unchanged,
        "removed": removed,
        "new_chunks": chunks,
    }


def normalize_query(query: str) -> str:
    stopwords = {
        "a", "an", "and", "are", "before", "after", "changed", "did", "do", "for", "how",
        "in", "is", "of", "on", "or", "the", "to", "was", "what", "when", "where", "why",
    }
    raw_tokens = re.findall(r"[\w\-\.\\/:]+", query, flags=re.UNICODE)
    tokens = [token for token in raw_tokens if token.lower() not in stopwords]
    if not tokens:
        tokens = raw_tokens
    if not tokens:
        return '""'
    return " OR ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens[:12])


def search(query: str, db_path: Path = DEFAULT_DB, limit: int = 8) -> list[SearchHit]:
    if not db_path.exists():
        return []
    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute(
            """
            SELECT source, section, bm25(memory_fts) AS score,
                   snippet(memory_fts, 2, '[', ']', ' … ', 24) AS snippet
            FROM memory_fts
            WHERE memory_fts MATCH ?
            ORDER BY score
            LIMIT ?
            """,
            (normalize_query(query), max(1, min(limit, 50))),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    finally:
        connection.close()
    return [SearchHit(source=row[0], section=row[1], score=float(row[2]), snippet=row[3]) for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="Incrementally index and search canonical Markdown memory with SQLite FTS5.")
    parser.add_argument("query", nargs="?")
    parser.add_argument("--memory-dir", type=Path, default=DEFAULT_MEMORY_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--index-only", action="store_true")
    args = parser.parse_args()

    index_result = update_index(args.memory_dir, args.db, rebuild=args.rebuild)
    payload: dict[str, object] = {"index": index_result, "query": args.query or "", "hits": []}
    if args.query and not args.index_only:
        payload["hits"] = [asdict(hit) for hit in search(args.query, args.db, args.limit)]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
