from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HOME = Path.home()
CODEX_HOME = Path(__import__("os").environ.get("CODEX_HOME", HOME / ".codex"))
DEFAULT_INVENTORY = CODEX_HOME / "harness" / "catalog" / "skill-inventory.json"
DEFAULT_CONTRACTS = CODEX_HOME / "harness" / "catalog" / "skill-contracts.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def evaluate_contracts(inventory: dict, suite: dict) -> dict:
    descriptions: dict[str, str] = {}
    for entry in inventory.get("entries", []):
        if entry.get("has_skill_md") and entry.get("skill_id") not in descriptions:
            descriptions[str(entry["skill_id"])] = str(entry.get("description") or "")

    contracts = suite.get("contracts", [])
    missing_skills: list[str] = []
    description_failures: list[str] = []
    compiled: list[tuple[str, list[re.Pattern], list[re.Pattern]]] = []
    for contract in contracts:
        skill_id = str(contract["skill_id"])
        description = descriptions.get(skill_id)
        if description is None:
            missing_skills.append(skill_id)
            continue
        terms = [str(term).lower() for term in contract.get("description_any", [])]
        if terms and not any(term in description.lower() for term in terms):
            description_failures.append(skill_id)
        positives = [re.compile(pattern, re.IGNORECASE) for pattern in contract.get("positive_patterns", [])]
        excludes = [re.compile(pattern, re.IGNORECASE) for pattern in contract.get("exclude_patterns", [])]
        compiled.append((skill_id, positives, excludes))

    failures: list[dict] = []
    cases = suite.get("cases", [])
    for index, case in enumerate(cases, start=1):
        prompt = str(case.get("prompt", ""))
        expected = sorted(str(item) for item in case.get("expected", []))
        predicted = sorted(
            skill_id
            for skill_id, positives, excludes in compiled
            if any(pattern.search(prompt) for pattern in positives)
            and not any(pattern.search(prompt) for pattern in excludes)
        )
        if predicted != expected:
            failures.append({"case": index, "prompt": prompt, "expected": expected, "predicted": predicted})

    failure_rate = round(len(failures) / len(cases) * 100, 2) if cases else 100.0
    threshold = float(suite.get("max_failure_percent", 5.0))
    return {
        "schema_version": suite.get("schema_version"),
        "cases": len(cases),
        "failed_cases": len(failures),
        "failure_percent": failure_rate,
        "max_failure_percent": threshold,
        "missing_skills": sorted(set(missing_skills)),
        "description_failures": sorted(set(description_failures)),
        "failures": failures,
        "passed": bool(cases) and failure_rate <= threshold and not missing_skills and not description_failures,
        "scope_note": "Deterministic trigger-contract regression; this is not a live model-routing benchmark.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic positive/negative trigger contracts for local skills.")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS)
    args = parser.parse_args()
    result = evaluate_contracts(read_json(args.inventory), read_json(args.contracts))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
