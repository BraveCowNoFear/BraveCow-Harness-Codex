from __future__ import annotations

import json
import sys


for raw in sys.stdin:
    message = json.loads(raw)
    request_id = message.get("id")
    method = message.get("method")
    if request_id is None:
        continue
    if method == "initialize":
        result = {"serverInfo": {"name": "fake-codex", "version": "test"}}
    elif method == "thread/start":
        result = {"thread": {"id": "thread-test-123"}}
    elif method == "thread/name/set":
        result = {}
    elif method == "turn/start":
        inputs = message.get("params", {}).get("input", [])
        assert any(item.get("type") == "skill" and item.get("name") == "bravecow-onboarding" for item in inputs)
        result = {"turn": {"id": "turn-test-456"}}
    else:
        result = {}
    print(json.dumps({"id": request_id, "result": result}), flush=True)
    if method == "turn/start":
        print(json.dumps({"method": "turn/completed", "params": {"threadId": "thread-test-123", "turn": {"id": "turn-test-456", "status": "completed"}}}), flush=True)
