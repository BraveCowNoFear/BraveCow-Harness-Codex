from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

import tiktoken


SKILL_LINE = re.compile(r"^-\s+(.+?):\s+(.+?)\s+\(file:\s+.+\)\s*$")


def bucket_for_text(text: str) -> str:
    lowered = text.lower()
    if "<skills_instructions>" in lowered or "## skills" in lowered:
        return "skills"
    if "memory_summary" in lowered or "## memory" in lowered:
        return "memory"
    if "agents.md instructions" in lowered or "## self-improvement" in lowered:
        return "agents"
    if "<plugins_instructions>" in lowered or "recommended_plugins" in lowered:
        return "plugins"
    return "other"


def measure_messages(messages: list[dict], encoding_name: str = "o200k_base") -> dict:
    encoding = tiktoken.get_encoding(encoding_name)
    buckets = {"skills": 0, "memory": 0, "agents": 0, "plugins": 0, "other": 0}
    skill_entries: list[dict[str, object]] = []
    skill_lines: list[str] = []
    for message in messages:
        for item in message.get("content", []):
            if item.get("type") != "input_text":
                continue
            text = str(item.get("text", ""))
            buckets[bucket_for_text(text)] += len(encoding.encode(text))
            for line in text.splitlines():
                match = SKILL_LINE.match(line)
                if not match:
                    continue
                skill_id, description = match.groups()
                tokens = len(encoding.encode(description))
                skill_entries.append(
                    {"skill_id": skill_id.strip(), "description_tokens": tokens, "description_chars": len(description)}
                )
                skill_lines.append(line)

    skill_entries.sort(key=lambda item: (-int(item["description_tokens"]), str(item["skill_id"])))
    return {
        "encoding": encoding_name,
        "total_tokens": sum(buckets.values()),
        "buckets": buckets,
        "message_count": len(messages),
        "skill_catalog": {
            "entries": len(skill_entries),
            "catalog_line_tokens": len(encoding.encode("\n".join(skill_lines))),
            "description_tokens": sum(int(item["description_tokens"]) for item in skill_entries),
            "top_descriptions": skill_entries[:15],
        },
    }


def run_prompt_probe(codex: str, sentinel: str, timeout: int) -> tuple[list[dict], str, str]:
    commands = [
        ([codex, "debug", "prompt-input", sentinel], "native"),
        ([codex, "-c", 'service_tier="fast"', "debug", "prompt-input", sentinel], "legacy-fast-alias"),
    ]
    diagnostics: list[str] = []
    for command, mode in commands:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        raw = result.stdout
        start = raw.find("[")
        if result.returncode == 0 and start >= 0:
            return json.loads(raw[start:]), mode, " | ".join(diagnostics)
        diagnostic = (result.stderr or raw).strip().replace("\n", " | ")[:600]
        diagnostics.append(diagnostic)
        if "unknown variant `priority`" not in diagnostic.lower():
            break
    raise RuntimeError("prompt-input probe failed: " + " | ".join(diagnostics))


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure model-visible Codex startup prompt tokens.")
    parser.add_argument("--codex", default=shutil.which("codex") or "")
    parser.add_argument("--sentinel", default="harness-audit-sentinel")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.codex:
        raise SystemExit("codex executable not found")

    messages, probe_mode, diagnostic = run_prompt_probe(args.codex, args.sentinel, args.timeout)
    result = measure_messages(messages)
    result["probe_mode"] = probe_mode
    result["native_probe_diagnostic"] = diagnostic
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
