from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_receipt(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["recorded_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_messages(stream: Any, inbox: queue.Queue[dict[str, Any]]) -> None:
    for line in stream:
        line = line.strip()
        if not line:
            continue
        try:
            inbox.put(json.loads(line))
        except json.JSONDecodeError:
            continue


def read_stderr(stream: Any, lines: list[str]) -> None:
    for line in stream:
        if len(lines) >= 40:
            del lines[0]
        lines.append(line.rstrip())


def send(process: subprocess.Popen[str], payload: dict[str, Any]) -> None:
    assert process.stdin is not None
    process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
    process.stdin.flush()


def process_error(process: subprocess.Popen[str], stderr_lines: list[str]) -> RuntimeError:
    detail = "\n".join(stderr_lines[-10:]).strip()
    suffix = f": {detail}" if detail else ""
    return RuntimeError(f"App Server exited with code {process.returncode}{suffix}")


def wait_for_id(
    inbox: queue.Queue[dict[str, Any]],
    request_id: int,
    deadline: float,
    process: subprocess.Popen[str],
    stderr_lines: list[str],
) -> dict[str, Any]:
    deferred: list[dict[str, Any]] = []
    try:
        while time.monotonic() < deadline:
            try:
                message = inbox.get(timeout=min(0.25, max(0.01, deadline - time.monotonic())))
            except queue.Empty:
                if process.poll() is not None:
                    raise process_error(process, stderr_lines)
                continue
            if message.get("id") == request_id:
                return message
            deferred.append(message)
    finally:
        for message in deferred:
            inbox.put(message)
    raise TimeoutError(f"Timed out waiting for App Server response {request_id}")


def response_result(message: dict[str, Any], label: str) -> dict[str, Any]:
    if "error" in message:
        raise RuntimeError(f"{label} failed: {message['error']}")
    result = message.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"{label} returned no result")
    return result


def wait_for_method(
    inbox: queue.Queue[dict[str, Any]],
    method: str,
    deadline: float,
    process: subprocess.Popen[str],
    stderr_lines: list[str],
) -> dict[str, Any]:
    while time.monotonic() < deadline:
        try:
            message = inbox.get(timeout=min(0.25, max(0.01, deadline - time.monotonic())))
        except queue.Empty:
            if process.poll() is not None:
                raise process_error(process, stderr_lines)
            continue
        if message.get("method") == method:
            return message
    raise TimeoutError(f"Timed out waiting for App Server notification {method}")


def start_codex_task(args: argparse.Namespace) -> dict[str, Any]:
    command = [args.executable, *args.executable_arg, "app-server"]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert process.stdout is not None
    inbox: queue.Queue[dict[str, Any]] = queue.Queue()
    reader = threading.Thread(target=read_messages, args=(process.stdout, inbox), daemon=True)
    reader.start()
    assert process.stderr is not None
    stderr_lines: list[str] = []
    stderr_reader = threading.Thread(target=read_stderr, args=(process.stderr, stderr_lines), daemon=True)
    stderr_reader.start()
    deadline = time.monotonic() + args.timeout
    try:
        send(process, {"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "bravecow-harness", "version": "0.7.0"}}})
        response_result(wait_for_id(inbox, 1, deadline, process, stderr_lines), "initialize")
        send(process, {"method": "initialized", "params": {}})
        send(
            process,
            {
                "id": 2,
                "method": "thread/start",
                "params": {
                    "cwd": str(Path(args.workspace).resolve()),
                    "serviceName": "BraveCow Harness",
                    "ephemeral": args.ephemeral,
                },
            },
        )
        thread_result = response_result(wait_for_id(inbox, 2, deadline, process, stderr_lines), "thread/start")
        thread = thread_result.get("thread", thread_result)
        thread_id = thread.get("id") if isinstance(thread, dict) else None
        if not thread_id:
            raise RuntimeError("thread/start returned no thread id")
        if not args.ephemeral:
            send(process, {"id": 3, "method": "thread/name/set", "params": {"threadId": thread_id, "name": "BraveCow 新手指南 · 从这里开始"}})
            response_result(wait_for_id(inbox, 3, deadline, process, stderr_lines), "thread/name/set")
        if args.language in {"auto", "zh-CN"}:
            prompt = (
                "$bravecow-onboarding\n\n请用简体中文开始安装后的交互式新手课程。"
                "先检测 Codex 和当前操作系统，每次只教一课，使用普通生活或商科例子，并在每课后等待用户回答。"
            )
        else:
            prompt = (
                "$bravecow-onboarding\n\nStart the post-install interactive beginner course in English. "
                "Detect Codex and the current operating system, teach one lesson per turn, use everyday or business examples, "
                "and wait for the learner after each lesson."
            )
        inputs: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        skill_path = Path(args.skill_path).resolve()
        if skill_path.exists():
            inputs.append({"type": "skill", "name": "bravecow-onboarding", "path": str(skill_path)})
        send(process, {"id": 4, "method": "turn/start", "params": {"threadId": thread_id, "input": inputs}})
        turn_result = response_result(wait_for_id(inbox, 4, deadline, process, stderr_lines), "turn/start")
        turn = turn_result.get("turn", turn_result)
        turn_id = turn.get("id") if isinstance(turn, dict) else None
        wait_for_method(inbox, "turn/completed", deadline, process, stderr_lines)
        return {
            "status": "started",
            "runtime": "Codex",
            "thread_id": thread_id,
            "turn_id": turn_id,
            "method": "app-server",
            "first_turn": "completed",
            "ephemeral": args.ephemeral,
        }
    finally:
        try:
            if process.stdin:
                process.stdin.close()
        except OSError:
            pass
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start a new Codex onboarding task through App Server.")
    parser.add_argument("--executable", default=os.environ.get("CODEX_EXECUTABLE", "codex"))
    parser.add_argument("--executable-arg", action="append", default=[])
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--skill-path", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--language", choices=["auto", "zh-CN", "en"], default="auto")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--ephemeral", action="store_true", help="Create a non-persistent task for acceptance testing.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    receipt = Path(args.receipt).resolve()
    try:
        result = start_codex_task(args)
        write_receipt(receipt, result)
        print(f"Started Codex onboarding task: {result['thread_id']}")
        return 0
    except Exception as first_exc:
        first_error = str(first_exc)
        if "unknown variant `priority`" in first_error and "expected `fast` or `flex`" in first_error:
            args.executable_arg.extend(["-c", 'service_tier="fast"'])
            try:
                result = start_codex_task(args)
                result["compatibility_override"] = "service_tier=fast"
                write_receipt(receipt, result)
                print(f"Started Codex onboarding task with desktop compatibility override: {result['thread_id']}")
                return 0
            except Exception as retry_exc:
                first_error = f"{retry_exc} (initial error: {first_error})"
        write_receipt(receipt, {"status": "failed", "runtime": "Codex", "method": "app-server", "error": first_error})
        print(f"Failed to start Codex onboarding task: {first_error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
