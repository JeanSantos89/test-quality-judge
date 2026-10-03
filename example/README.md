# Example run

This folder is a self-contained fixture to try the gate end to end.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd test-quality-judge
python -m src.cli \
  --requirement example/requirement.txt \
  --source-code example/source.py \
  --test-cases example/cases.json
```

## What to expect

- `request_reset_generates_token_for_registered_email`,
  `reset_password_with_valid_token_updates_and_invalidates` and
  `reset_password_with_unknown_token_is_rejected` should come back `keep`
  from both judges — they match real methods and real acceptance
  criteria.
- The requirement judge should flag a **gap**: criterion 2 (token expires
  after 30 minutes) has no test case covering it at all. Depending on
  phrasing, it may attach that gap note to the closest related case or
  report it as missing coverage.
- The hallucination judge should **cut**
  `reset_password_locks_account_after_three_failed_attempts`: it calls
  `PasswordResetService.lock_account_after_attempts`, a method that does
  not exist in `source.py`.
