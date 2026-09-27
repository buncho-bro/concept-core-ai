# Exp002 CPU performance benchmark 001

Status: `PERF_BENCHMARK_COMPLETED`

This directory records a non-formal wall-clock benchmark of the verified Exp002 implementation. It does not select or freeze a performance configuration and does not create a formal baseline.

## Workload

Each repetition trained the verified Exp002 autoencoder for two complete epochs over 1,024 fixed 64×64 RGB images, using batch size 128, the verified optimizer, FP32 precision rules, and balanced reconstruction loss. Every image contained both foreground and background. Dataset, model, and loader randomness were fixed under the `NON_FORMAL_PERFORMANCE_BENCHMARK` namespace. One identical warm-up was excluded for every candidate. Each candidate then ran three measured repetitions.

The timed region began immediately before the first DataLoader iteration and ended after the second epoch. It therefore included DataLoader startup and iteration plus forward, loss, backward, and optimizer work. Environment creation, imports, model creation, reporting, and Git operations were excluded.

## Execution-environment restriction

DataLoader multiprocessing was unavailable. The attempted `s2_t8_w1_np` candidate failed before its first training batch when Python multiprocessing attempted to create its IPC/socket listener and received `PermissionError: [Errno 1] Operation not permitted`. It is classified as `ENVIRONMENT_INFEASIBLE`; it has no timing and is not treated as slow.

Consequently, the feasible benchmark space was restricted to `num_workers=0` and `persistent_workers=false`. These results are valid only for an environment with that restriction. A later PERF SELECTION/FREEZE stage must not select `num_workers>0` from this evidence. If the intended formal environment supports multiprocessing, a new benchmark in that environment is required before selecting a positive worker count.

## Results

Twelve feasible candidates completed, producing 36 valid timing observations. Ordering used median wall-clock seconds only. No scientific outcome metric was inspected or used for advancement or ranking.

The fastest observed median was `s1_t8_i1` at 1.889237 seconds. The next was `s3_t8_o4_m8` at 1.986348 seconds. Their observed ranges overlap, so timing uncertainty is `PERFORMANCE_TIE_OR_UNCERTAIN`. This is benchmark evidence, not a frozen selection.

Scientific source, tests, normative documents, dependency definitions, and VERIFY artifacts were unchanged. Formal scientific runs executed: 0. Final performance selected: no. Final performance frozen: no. Real formal baseline frozen: no.
