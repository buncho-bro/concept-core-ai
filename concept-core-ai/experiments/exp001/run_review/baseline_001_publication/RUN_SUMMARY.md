# Experiment 001 — formal baseline 001

MODE: RUN
RUN STATUS: RUN_COMPLETE

Experiment-level classification: **INCONCLUSIVE**

Execution commit: `e9791b236e2c2618ed77e031e667c58b24e76e01` (PR #2 merged before RUN).
Formal seeds: 1001, 1002, 1003, 1004, 1005; one attempt per seed, in that order.
Device: CPU. OMP_NUM_THREADS=1; MKL_NUM_THREADS=1.
Environment: `{"python": "3.12.14", "platform": "Windows-11-10.0.26200-SP0", "packages": {"numpy": "2.3.5", "torch": "2.7.1", "scipy": "1.15.3", "scikit-learn": "1.6.1", "matplotlib": "3.10.3", "threadpoolctl": "3.6.0", "pytest": "8.4.1"}}`

Pre-RUN VERIFY: 106 passed, 0 failed/errors/skipped, exit_code=0;
implementation_unchanged_during_verification=true; formal_runs_executed=0.
Receipt: [verification/verification.json](verification/verification.json).

| Master seed | Run ID | Execution status | Evaluation flags | Complete |
| --- | --- | --- | --- | --- |
| 1001 | exp001-seed-1001-attempt-01 | VALID | NONE | true |
| 1002 | exp001-seed-1002-attempt-01 | VALID | NONE | true |
| 1003 | exp001-seed-1003-attempt-01 | VALID | NONE | true |
| 1004 | exp001-seed-1004-attempt-01 | VALID | NONE | true |
| 1005 | exp001-seed-1005-attempt-01 | VALID | NONE | true |

Formal runs executed: 5; invalid: 0; experimental failures: 0.
Aggregate warnings: NONE.
Post-hoc changes: **NONE**. Protected implementation, tests, dependency locks, spec and decisions remained unchanged.
All five runs have matching commit/environment, correct derived seeds, and verified artifact hashes.

Aggregate: [aggregate/aggregate_metrics.json](aggregate/aggregate_metrics.json).
Manifest: [RUN_MANIFEST.json](RUN_MANIFEST.json).

This records only the formal classification under the preregistered Experiment 001 conditions. Detailed scientific interpretation is deferred to MODE: ANALYZE.

Operational warnings: Matplotlib used a writable temporary cache because the default user cache was inaccessible; VERIFY also emitted 14 dependency deprecation warnings. These warnings did not fail verification or any run.

Original run, aggregate and audit artifacts remain unchanged locally. This separate publication copy replaces personal absolute paths with portable paths in reports/logs. Run ZIP contents and the verification receipt are byte-preserving copies. No run was deleted, overwritten, selected again or repeated.
