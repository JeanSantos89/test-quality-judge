# Evaluation results

This is a **manual run** of the example fixture (`example/`), not an automated
`python -m src.cli` execution. Reason: no `ANTHROPIC_API_KEY` was available in
the environment this run happened in.

## Methodology

Both judges' roles were played manually, each reasoning only from the inputs
its own system prompt (`src/prompts.py`) defines — the requirement judge never
looked at the source code, the hallucination judge never looked at the
requirement text — mirroring the isolation the tool enforces at the API-call
level. The one caveat worth naming: this was a single reasoning session doing
both passes, not two separate, truly isolated API calls. That's a weaker
isolation guarantee than the tool provides when actually run, though the task
itself (comparing fixed text against fixed text) leaves little room for one
pass to bias the other the way a creative or generative judgment would.

## Requirement judge

Acceptance criteria, from `example/requirement.txt`:

| # | Criterion |
|---|---|
| 1 | Registered email → reset token generated + email sent with a reset link |
| 2 | Token expires after 30 minutes |
| 3 | Expired/used token → rejected without revealing whether the email exists |
| 4 | Valid token + new password → password updated, token invalidated |

| Test case | Verdict | Reason | Source |
|---|---|---|---|
| `request_reset_generates_token_for_registered_email` | **rewrite** | Only asserts a token is returned; criterion 1 also requires an email containing the reset link to be sent, which this case never checks. | Criterion 1 |
| `reset_password_with_valid_token_updates_and_invalidates` | **keep** | Fully exercises "valid token + new password updates and invalidates". | Criterion 4 |
| `reset_password_with_unknown_token_is_rejected` | **rewrite** | Covers an *unknown* token, but criterion 3 is about an *expired or used* token — a different path through the same method, never exercised. | Criterion 3 |
| `reset_password_locks_account_after_three_failed_attempts` | **cut** | No acceptance criterion mentions account lockout after failed attempts. Not justified by the requirement at all. | — (no matching clause) |

**Gap found:** criterion 2 (30-minute token expiry) has no test case exercising it at all — not even indirectly.

## Hallucination judge

| Test case | Verdict | Reason | Source |
|---|---|---|---|
| `request_reset_generates_token_for_registered_email` | **keep** | `PasswordResetService.request_reset(email)` exists and returns a token string. | `src/source.py`, `request_reset` |
| `reset_password_with_valid_token_updates_and_invalidates` | **keep** | `reset_password(token, new_password)` exists; a second call with the same (now-used) token returns `False`, matching the asserted behavior. | `src/source.py`, `reset_password` |
| `reset_password_with_unknown_token_is_rejected` | **keep** | `reset_password` returns `False` for a token not in `self._tokens`. | `src/source.py`, `reset_password` |
| `reset_password_locks_account_after_three_failed_attempts` | **cut** | Cites `PasswordResetService.lock_account_after_attempts`, which does not exist anywhere in `source.py`. | `src/source.py` (method absent) |

Matches the hallucination `example/README.md` already documents, exactly.

## Merged verdict (`GateResult.final_verdicts()`)

A `cut` from either judge wins; otherwise `rewrite` wins over `keep` (`src/models.py:36`).

| Test case | Requirement | Hallucination | **Final** |
|---|---|---|---|
| `request_reset_generates_token_for_registered_email` | rewrite | keep | **rewrite** |
| `reset_password_with_valid_token_updates_and_invalidates` | keep | keep | **keep** |
| `reset_password_with_unknown_token_is_rejected` | rewrite | keep | **rewrite** |
| `reset_password_locks_account_after_three_failed_attempts` | cut | cut | **cut** |

Gate exit code: `1` (at least one `cut`).

## Finding: the fixture's documented expectation is looser than the prompt it tests

`example/README.md` says three of the four cases "should come back `keep` from
both judges". Under a strict reading of `REQUIREMENT_JUDGE_SYSTEM` — *"If you
cannot find a line that backs 'keep', you must not use 'keep'"* — two of those
three only partially satisfy their criterion (see table above) and should
rewrite, not keep. The hallucination side matches the documented expectation
exactly; only the requirement side diverges. This isn't a bug, but it's a real
gap between what the fixture's own README promises and what its own prompt,
read literally, produces — worth tightening one side or the other before
someone runs this expecting the documented output verbatim.

## What a real run still needs

1. An actual `ANTHROPIC_API_KEY` run, to confirm the model's verdicts match
   (or diverge from) this manual walkthrough — this run is a sanity check on
   the fixture and prompts, not a substitute for calling the model.
2. A decision on the discrepancy above: loosen the requirement judge's prompt,
   or tighten the fixture's documented expectation to match it.
3. `MODEL` in `src/judges.py` is hardcoded to `claude-sonnet-5-5` with no env
   override — fine for a fixture, but worth parameterizing before this is used
   against real projects with different model/cost tradeoffs.
