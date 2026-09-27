# Traceability

| Review item | Formal source | PR #8 implementation | Status |
|---|---|---|---|
| Native-thread values fixed before native imports | spec §50A; HD-002-01 | `process_start.py`, `formal_worker.py`, `cli.launch_formal` | Partial: normal CLI complies; direct execution bypass remains. |
| Registration before child process | spec §50A; HD-002-01 | `cli.launch_formal`, `baseline.register_attempt` | Implemented. |
| Human-authorized successor only | spec §50A; HD-002-01 | `baseline.validate_successor_authorization`, authorization-record format | Implemented; Windows automated validation is currently broken. |
| Canonical attempt selection | spec formal baseline rules | `baseline.py`, `aggregation.py` | Maintained. |
| Scientific conditions and success rules | `spec.md` | No change in PR #8 | No conflict found. |
