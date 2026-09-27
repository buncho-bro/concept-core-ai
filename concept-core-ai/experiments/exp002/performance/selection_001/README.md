# Exp002 performance selection 001

Status: `PERF_SELECTION_COMPLETED`

This selection consumes only the committed evidence in `performance/benchmark_001/` at commit `ae4ac4c3e1b16a1a3681ac13a8912724061700b8`. No new benchmark measurement was performed.

The deterministic rule selects the successfully completed feasible candidate with the numerically smallest recorded median wall-clock time. `s1_t8_i1` had the minimum median, 1.8892372219997924 seconds, and was selected with 8 PyTorch intra-op threads, 1 inter-op thread, 8 OMP threads, 8 MKL threads, 0 DataLoader workers, and non-persistent workers.

The benchmark status remains `PERFORMANCE_TIE_OR_UNCERTAIN`: the observed range of the selected candidate overlaps the runner-up range. Selection follows the predeclared median rule; it does not establish statistical or universal superiority. No scientific metric or post-hoc criterion was used.

DataLoader multiprocessing was unavailable in the benchmark environment, so this evidence supports only `num_workers=0` and `persistent_workers=false`. A different formal environment that supports positive worker counts requires a new benchmark before selecting them.

Performance is selected but not frozen. The formal baseline is not frozen, no canonical attempt is registered, and formal scientific runs remain zero. The next stage is PERF FREEZE / FORMAL BASELINE FREEZE preparation.
