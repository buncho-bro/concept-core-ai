# Finding disposition

## REV-002-01: RESOLVED

Canonical registration remains baseline-governed: first registration is canonical, retries cannot replace it, and aggregation resolves records from the frozen baseline rather than caller-selected paths. The canonical/retry regression tests passed.

## REV-002-02: RESOLVED

`runner.execute_registered_attempt` no longer exists. `runner.run_one` rejects formal execution, and `runner._execute_attempt` rejects every config except `formal is False` before artifacts or science start. The only formal body is a function local to `formal_worker.main`, created after `validate_process_start` completes. `formal_worker` imports only stdlib before that guard; `process_start` is also stdlib-only. Fresh-subprocess early-import and OMP/MKL mismatch tests demonstrate rejection before formal science. No alternative supported formal entry point was found in runner, CLI, exports, or reanalysis.

## REV-002-03: RESOLVED

Committed successor-authorization records remain required and revalidated at freeze/run/aggregate. Source inspection and the authorization invalid-case suite confirm that an untracked or altered record, wrong transition fields, integrity hash, Git blob, or source commit is rejected. A free-form reason alone remains insufficient.

## REV-002-04: RESOLVED

The Git helper now forces UTF-8 decoding with strict errors and C locale. The authorization suite reached its assertions and passed on Windows (11 passed, no skips/errors); the prior cp932 pre-assertion failure was not reproduced.
