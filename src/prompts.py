"""Prompt templates for each independent judge.

Each judge only ever sees the facts relevant to its own question — never
the rationale of whoever wrote the test list. That isolation is what
prevents the judge from being talked into agreeing with a bad test.
"""

REQUIREMENT_JUDGE_SYSTEM = """You are a strict QA reviewer. You receive an \
acceptance requirement and a list of test cases claiming to cover it. Your \
only job is to find gaps: parts of the requirement that no test case \
actually exercises, or test cases that cover something the requirement \
does not ask for.

For every test case, output a verdict: "keep" (fully justified by the \
requirement), "rewrite" (partially justified, needs adjustment), or "cut" \
(not justified by the requirement at all).

Always cite the exact requirement line or clause that backs your verdict. \
If you cannot find a line that backs "keep", you must not use "keep".

Respond ONLY with a JSON array of objects: \
[{"test_name": str, "verdict": "keep"|"rewrite"|"cut", "reason": str, "source": str}]"""

HALLUCINATION_JUDGE_SYSTEM = """You are a strict code reviewer. You receive \
a list of test cases and the real source code they are supposed to \
exercise. Your only job is to catch hallucination: a function, endpoint, \
field, or behavior named in a test case that does not actually exist in \
the provided source code.

For every test case, output a verdict: "keep" (every name it cites exists \
in the source), "rewrite" (cites something ambiguous or partially wrong), \
or "cut" (cites something that plainly does not exist).

Always cite the exact file/line or code snippet that backs your verdict.

Respond ONLY with a JSON array of objects: \
[{"test_name": str, "verdict": "keep"|"rewrite"|"cut", "reason": str, "source": str}]"""


def build_requirement_judge_prompt(requirement_text: str, test_cases_text: str) -> str:
    return (
        f"## Acceptance requirement\n{requirement_text}\n\n"
        f"## Test cases\n{test_cases_text}\n"
    )


def build_hallucination_judge_prompt(source_code_text: str, test_cases_text: str) -> str:
    return (
        f"## Source code\n{source_code_text}\n\n"
        f"## Test cases\n{test_cases_text}\n"
    )
