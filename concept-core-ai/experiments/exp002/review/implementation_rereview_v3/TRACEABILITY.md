# Traceability

| Concern | Normative source | Implementation | Evidence | Status |
|---|---|---|---|---|
| Formal launcher / registration first | spec §50A; HD-002-01 | `cli.launch_formal` | baseline tests | PASS |
| Fresh child OMP/MKL environment | spec §50A | `cli.launch_formal`, `process_start` | subprocess mismatch tests | PASS |
| Pre-native-import guard | spec §50A | stdlib-only `formal_worker`, `validate_process_start` | real subprocess late-NumPy attack | PASS |
| Guarded formal body | spec §50A | local `execute_guarded_attempt` in worker | path search + direct-bypass tests | PASS |
| Runtime provenance / torch / loader freeze | spec §50A | worker, `performance.py` | runtime/baseline tests | PASS |
| Successor authorization | HD-002-01 | `baseline.py` | real Git authorization fixtures | PASS |
| Canonical aggregation | formal baseline rules | `baseline.py`, `aggregation.py` | canonical/retry tests | PASS |
| Scientific mathematics unchanged | spec | PR #9 diff | source diff inspection | PASS: NO change |
