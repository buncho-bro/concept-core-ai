# Experiment 001 — execution status / evaluation flags fix

Mode: FIX + VERIFY

## FIX SUMMARY

FIX_COMPLETE

- Removed the two-line post-evaluation conversion from PROBE_FAILED / DISTANCE_FAILED to EXPERIMENTAL_FAILURE. A run that completes evaluation now retains VALID, its evaluation flags, complete=true and reason=null.
- Preserved the existing ExperimentalFailure handler and technical-exception handler. Training ExperimentalFailure remains EXPERIMENTAL_FAILURE; technical exceptions remain INVALID and are re-raised after preserving failure artifacts.
- Clarified rotation metadata as `{low: 0.0, high: 360.0, high_inclusive: false}`. Circle rotation remains 0.0. The generator and its Uniform[0,360) behavior are unchanged.
- No aggregation implementation or existing test was changed.

Canonical sources were read from GitHub main at `39f201e1a42e8045d9694546fdf113896fd8d908`, after PR #1 had been merged:

1. `experiments/exp001/spec.md`, sections 18 and 19 (blob `980bb0ba3830f08a8a99aacc0c5147695ebe091b`).
2. APPROVED `experiments/exp001/decisions.md`, DEC-NB-v2-01 (blob `7751de576220cf898653341304aabe9b4393da94`).
3. `experiments/exp001/review/final_review_v4/VERIFICATION_PLAN.md` (blob `c12d1df0981a2b45d00d2e5d90b959fa9c88cc4e`).

The production code and existing tests were matched by Git blob hashes against the remote implementation before editing. Only runner.py and config.py differ among the existing implementation/test/dependency files.

## FILES CHANGED

- `src/exp001/runner.py`: delete evaluation-flag-based execution-status conversion.
- `src/exp001/config.py`: explicitly record the exclusive upper rotation bound.
- `tests/test_runner_status.py`: seven additional regression cases.
- `experiments/exp001/implementation_review/fix_status_semantics/FIX_REPORT.md`: this record.
- `experiments/exp001/implementation_review/fix_status_semantics/verification/pytest.txt`
- `experiments/exp001/implementation_review/fix_status_semantics/verification/junit.xml`
- `experiments/exp001/implementation_review/fix_status_semantics/verification/verification.json`

## TESTS RUN

1. Before the fix: new regression file, 3 passed / 4 failed. The expected failures reproduced the incorrect status in cases B/C/D and the ambiguous rotation metadata representation.
2. After the fix: `python -m pytest tests/test_runner_status.py tests/test_aggregation.py -q` — 54 passed.
3. Full existing verification command:

```text
python -m exp001 verify --output experiments/exp001/implementation_review/fix_status_semantics/verification
```

Full verification ran the original 99 cases plus seven new cases. The code fingerprint stayed unchanged during verification. CPU environment: Python 3.12.14, NumPy 2.3.5, PyTorch 2.7.1; dependencies were not changed.

## TESTS PASSED

**106 passed**, CLI exit code **0**, pytest duration **68.80 seconds**.

| Required case | Verified result |
| --- | --- |
| A: evaluation flags empty | VALID, complete=true, reason=null |
| B: PROBE_FAILED | VALID; flag retained |
| C: DISTANCE_FAILED | VALID; flag retained |
| D: PROBE_FAILED + DISTANCE_FAILED | VALID; both flags retained |
| E: training raises ExperimentalFailure | EXPERIMENTAL_FAILURE; evaluation not called |
| F: technical training exception | INVALID; exception and artifacts preserved; evaluation not called |
| Rotation metadata JSON round trip | high=360.0, high_inclusive=false; circle=0.0 |

Runner tests verify returned and saved status, saved report state, completion/reason fields, failure files, artifact integrity and stage calls. Their expensive training/evaluation work is mocked and their isolated harness uses non-formal seed 77. Existing aggregation tests confirm VALID with missing primary evidence/flags and EXPERIMENTAL_FAILURE with missing evidence produce INCONCLUSIVE, while INVALID produces NOT_EVALUATED.

## TESTS FAILED

**0 in final verification; 0 errors; 0 skipped.**

Four intentionally observed pre-fix regression failures are resolved. The unchanged visualization dependencies emit 14 Matplotlib/Pyparsing deprecation warnings; these are not test failures.

## SPEC DEVIATIONS

**None.** Research specifications, dataset distribution, model, training, probes, distances, bootstrap, Pixel controls, success thresholds and aggregate classification rules are unchanged. The optional rotation edit changes artifact wording only.

## FORMAL RUNS EXECUTED

**0**

No formal five-seed baseline was executed. All fixture outcomes are implementation verification evidence, not Experiment 001 scientific results. No official scientific classification or interpretation was produced.

## READY_FOR_RUN

**READY_FOR_RUN**

The requested fix and verification are complete. Formal execution remains reserved for a later authorized MODE: RUN. Use a clean committed checkout and a verification receipt matching that checkout/environment, as already required by the CLI.

GitHub copies of logs/receipts omit personal absolute paths, hostnames and OS details. Test outcomes, library versions and implementation fingerprints are preserved. Original local evidence is retained; re-run verify after checkout to obtain a local, unredacted runtime receipt.
