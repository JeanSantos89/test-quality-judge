"""Judge runners: each one calls the LLM in isolation and parses its verdicts."""

from __future__ import annotations

import json

from anthropic import Anthropic

from .models import JudgeFinding, TestCase, Verdict
from .prompts import (
    HALLUCINATION_JUDGE_SYSTEM,
    REQUIREMENT_JUDGE_SYSTEM,
    build_hallucination_judge_prompt,
    build_requirement_judge_prompt,
)

MODEL = "claude-sonnet-5-5"


def _format_test_cases(cases: list[TestCase]) -> str:
    return "\n".join(f"- {c.name}: {c.description}" for c in cases)


def _parse_findings(raw_json: str) -> list[JudgeFinding]:
    items = json.loads(raw_json)
    return [
        JudgeFinding(
            test_name=item["test_name"],
            verdict=Verdict(item["verdict"]),
            reason=item["reason"],
            source=item["source"],
        )
        for item in items
    ]


def run_requirement_judge(client: Anthropic, requirement_text: str, cases: list[TestCase]) -> list[JudgeFinding]:
    """Checks each test case against the acceptance requirement, in a clean context."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=REQUIREMENT_JUDGE_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": build_requirement_judge_prompt(requirement_text, _format_test_cases(cases)),
            }
        ],
    )
    return _parse_findings(response.content[0].text)


def run_hallucination_judge(client: Anthropic, source_code_text: str, cases: list[TestCase]) -> list[JudgeFinding]:
    """Checks each test case against the real source code, in a clean context."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=HALLUCINATION_JUDGE_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": build_hallucination_judge_prompt(source_code_text, _format_test_cases(cases)),
            }
        ],
    )
    return _parse_findings(response.content[0].text)
