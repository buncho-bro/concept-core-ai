# Test audit

## Complete non-formal suite

`254 passed, 0 failed, 0 errors, 0 skipped`; 14 existing matplotlib/Pyparsing deprecation warnings. The first invocation encountered a permission-denied shared pytest Temp directory before fixture setup (76 setup errors). Re-running with a dedicated review Temp directory completed with exit code 0; this is the reported result. No formal training or formal seed result was produced.

## Authorization-only

`tests/test_exp002_authorization.py`: `11 passed, 0 failed, 0 errors, 0 skipped`. Evidence class A/C: real Git subprocesses and isolated temporary repositories. UTF-8 strict decoding is explicit.

## Fresh-worker boundary

`tests/test_exp002_runtime_governance.py`: fresh Python subprocess validation, later NumPy import attack, OMP mismatch, and MKL mismatch all passed. Evidence class A. The official launcher test is subprocess validation-only with parent monkeypatching of registration (B/D), not scientific training.

## Direct-bypass and registration crash window

`tests/test_exp002_baseline.py`: public old function absence, `run_one` rejection, `_execute_attempt(formal=True)` rejection, canonical registration before launch, and `OSError` failure-artifact persistence passed. Evidence class B/C; direct-bypass test additionally confirms no artifacts are created.

## Critical subset

Authorization + runtime-governance + baseline: `39 passed, 14 warnings in 5.91s`.
