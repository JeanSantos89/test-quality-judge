# test-quality-judge

A quality gate with two independent LLM judges that review a generated
test-case list: one against the acceptance requirement, the other
against the real source code — each in a clean context, never seeing the
other's verdict or the original author's rationale.

**→ See [RESULTS.md](./RESULTS.md) for a walkthrough of the example fixture**,
including a real gap found between the fixture's documented expectation and
what its own prompt, read literally, produces.

## Why

When an LLM generates test cases from a requirement, two mistakes go
unnoticed easily:

1. The tests cover less (or something different) than the acceptance
   criteria ask for — a requirement gap.
2. A test cites a function, endpoint, or behavior that doesn't actually
   exist in the code — a hallucination.

Whoever generated the tests is biased toward validating their own work.
Asking them to self-review doesn't catch either problem reliably.

## How it works

Two judges, each in an isolated context:

- **Requirement judge**: given the acceptance criteria and the test case
  list, flags what the criteria ask for that no test actually covers.
- **Hallucination judge**: given the test case list and the real source
  code, checks whether every cited name (function, route, field) exists.

Both judges only ever receive the facts of the cycle (requirement, code)
— never the defense of whoever wrote the tests. Every final verdict
(keep / rewrite / cut) comes with a cited source: the requirement line or
code reference backing it.

## Usage

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m src.cli \
  --requirement example/requirement.txt \
  --source-code example/source.py \
  --test-cases example/cases.json
```

See `example/README.md` for what to expect from the fixture run — it's
seeded with one deliberate requirement gap and one deliberate
hallucination, so the gate's output can be checked against a known
answer.

## Status

Generalization of a real quality gate (two independent judges — a
requirement reviewer and a code reviewer — screening generated test
cases before they enter a test suite). Reimplemented from scratch, no
original requirement, code, or test data included.
