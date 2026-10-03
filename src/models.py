"""Shared data structures for the dual-judge test quality gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Verdict(str, Enum):
    KEEP = "keep"
    REWRITE = "rewrite"
    CUT = "cut"


@dataclass
class TestCase:
    name: str
    description: str


@dataclass
class JudgeFinding:
    test_name: str
    verdict: Verdict
    reason: str
    source: str  # the requirement line or code reference backing the verdict


@dataclass
class GateResult:
    requirement_findings: list[JudgeFinding] = field(default_factory=list)
    hallucination_findings: list[JudgeFinding] = field(default_factory=list)

    def final_verdicts(self) -> dict[str, JudgeFinding]:
        """Merges both judges' findings per test case.

        A CUT from either judge wins. Otherwise REWRITE wins over KEEP.
        When both judges agree, keeps the one with the more specific reason.
        """
        merged: dict[str, JudgeFinding] = {}
        for finding in [*self.requirement_findings, *self.hallucination_findings]:
            current = merged.get(finding.test_name)
            if current is None:
                merged[finding.test_name] = finding
                continue
            if finding.verdict == Verdict.CUT or current.verdict == Verdict.CUT:
                merged[finding.test_name] = finding if finding.verdict == Verdict.CUT else current
            elif finding.verdict == Verdict.REWRITE:
                merged[finding.test_name] = finding
        return merged
