"""CLI entry point: runs both judges and prints the merged gate result.

Usage:
    python -m src.cli \
        --requirement requirement.txt \
        --source-code app.py \
        --test-cases cases.json
"""

from __future__ import annotations

import argparse
import json
import sys

from anthropic import Anthropic

from .judges import run_hallucination_judge, run_requirement_judge
from .models import GateResult, TestCase


def load_test_cases(path: str) -> list[TestCase]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [TestCase(name=item["name"], description=item["description"]) for item in raw]


def main() -> None:
    parser = argparse.ArgumentParser(description="Dual-judge test quality gate")
    parser.add_argument("--requirement", required=True, help="Path to the acceptance requirement (text file)")
    parser.add_argument("--source-code", required=True, help="Path to the source code the tests exercise")
    parser.add_argument("--test-cases", required=True, help="Path to a JSON file: [{name, description}, ...]")
    args = parser.parse_args()

    with open(args.requirement, encoding="utf-8") as f:
        requirement_text = f.read()
    with open(args.source_code, encoding="utf-8") as f:
        source_code_text = f.read()
    cases = load_test_cases(args.test_cases)

    client = Anthropic()

    result = GateResult(
        requirement_findings=run_requirement_judge(client, requirement_text, cases),
        hallucination_findings=run_hallucination_judge(client, source_code_text, cases),
    )

    verdicts = result.final_verdicts()
    exit_code = 0

    for name, finding in verdicts.items():
        print(f"[{finding.verdict.value.upper()}] {name}")
        print(f"  reason: {finding.reason}")
        print(f"  source: {finding.source}")
        if finding.verdict.value == "cut":
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
