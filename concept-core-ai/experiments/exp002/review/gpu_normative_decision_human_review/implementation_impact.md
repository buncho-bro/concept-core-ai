# Future Implementation Impact Review

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

No implementation was modified. This review describes likely changes required only after authoritative promotion.

## Current-state findings

- `Performance` contains CPU thread and DataLoader fields only; no device, precision, deterministic-backend, CUDA identity, or memory fields.
- `baseline.freeze_baseline` records `device` and `device_class`, but not GPU model, reliable-UUID availability/value, alternative same-device evidence, driver, PyTorch CUDA build/runtime, cuDNN, TF32, deterministic policy, or CUDA process-start identity.
- `validate_runtime` compares dependency environment and device class, not exact CUDA hardware/software identity.
- `cli.launch_formal` registers before launching the worker and has no separate pre-registration CUDA preflight.
- `formal_worker` correctly begins with a stdlib-only process-start guard for OMP/MKL, but currently applies `CUBLAS_WORKSPACE_CONFIG` with a source default after PyTorch/scientific imports. That literal is not approved by HD-A-GPU-010 and must not be treated as the future normative value.
- Training/reconstruction uses explicit float32 and disabled autocast, providing a useful base, but complete CUDA FP32/TF32/determinism verification is not yet implemented.
- Checkpoint loading already accepts a device/map-location path through inherited code, but CUDA-to-CPU portability and artifact analysis require explicit verification.
- Aggregation validates current baseline/registration/artifact consistency but not proposed CUDA identity and policy fields.
- Existing performance evidence/selection is CPU-only historical evidence and does not satisfy the proposed five/+five GPU-capable benchmark policy.
- Existing benchmark governance does not preserve the proposed complete failure taxonomy/attempt order or forbid result-dependent replacement strongly enough, and it does not implement the unconfirmed all-eligible expansion clarification.

## Change classification

| Area | Likely modules/artifacts | Classification | Required future treatment |
|---|---|---|---|
| CUDA device support | training, reconstruction, runner, CLI/config | EXECUTION_ONLY | Preserve explicit float32 and unchanged data/model/loss/evaluation semantics; no fallback. |
| Complete performance-candidate schema | `performance.py`, benchmark artifacts | GOVERNANCE_ONLY / EXECUTION_ONLY | Add device and CUDA policy fields; freeze config before measurement. |
| Baseline schema and baseline-003 lineage | `baseline.py`, manifest/decision schemas | GOVERNANCE_ONLY | Bind complete identity; distinguish governance history from runtime predecessor; do not fabricate 001/002. |
| GPU/environment provenance | `artifacts.py`, preflight, worker, aggregation | GOVERNANCE_ONLY / EXECUTION_ONLY | Capture model and reliable UUID when exposed; otherwise record UUID absence and the implementation-review-approved alternative same-device evidence, plus driver, PyTorch/CUDA/cuDNN, backend, and process-start fields. |
| CUDA process-start policy | `process_start.py`, CLI, worker | EXECUTION_ONLY / GOVERNANCE_ONLY | Establish reviewed value before native imports; remove unreviewed late default behavior. |
| Seed-free fresh preflight | new preflight entry point, CLI | EXECUTION_ONLY | Separate process, no formal seed/scientific imports/work; no registration on failure. |
| Worker revalidation and immutable failure | worker, CLI, baseline registry | GOVERNANCE_ONLY / EXECUTION_ONLY | Revalidate after registration; persist technical `INVALID` and integrity evidence. |
| Physical GPU/model/conditional UUID and stack checks | preflight, baseline, worker, aggregation | GOVERNANCE_ONLY / EXECUTION_ONLY | Enforce same physical GPU and exact model; exact-match reliable UUID when available, otherwise validate approved alternative evidence; reproduction mode remains distinct. Do not invent the alternative mechanism in this candidate. |
| TF32/FP32/determinism | model precision setup, worker, tests | EXECUTION_ONLY | Disable TF32, mixed precision, and silent relaxation; verify observed state. |
| CUDA RNG | model construction/config | EXECUTION_ONLY | Use existing `model_seed`; preserve purpose list/derivation. |
| Checkpoint portability | inherited checkpoint loader, export/reanalysis | EXECUTION_ONLY / TEST_ONLY | Explicit device mapping and CPU consumption of CUDA-created state. |
| Memory telemetry/OOM | training/runner/worker/benchmark artifacts | EXECUTION_ONLY / GOVERNANCE_ONLY | Record peak allocated/reserved; OOM never causes automatic batch/precision/device changes. |
| Five/+five benchmark | benchmark runner and selection schema | GOVERNANCE_ONLY | After Human confirmation, enforce all-eligible expansion, all-10 recomputation, and CPU-incumbent uncertainty rule; reject execution while clarification remains unconfirmed. |
| Reliability eligibility and metric exclusion | benchmark/selection validators | GOVERNANCE_ONLY | Preserve every attempted repetition/failure/order; prohibit replacement and post-hoc retry; separate `PERFORMANCE_INFEASIBLE` from formal/scientific statuses; prevent scientific fields from affecting eligibility, stopping, repetition count, or selection. |
| Reliability/expansion edge cases | benchmark design and schema | GOVERNANCE_ONLY | Human-confirm the initial-stage, pre-expansion, and expansion-stage failure policy before implementation/benchmarking; do not infer it from outcomes. |
| Aggregation validation | `aggregation.py` | GOVERNANCE_ONLY | Validate exact CUDA evidence and technical INVALID semantics before §40 unchanged. |
| Regression and CUDA policy tests | tests | TEST_ONLY | Implement the plan in `test_verify_plan.md`. |

## Potentially scientific assessment

```text
POTENTIALLY_SCIENTIFIC: NONE REQUIRED BY THIS CANDIDATE
```

Any future proposal to change batch size, precision, architecture, optimizer, epochs, objective, dataset, seed system, evaluation mathematics, or success criteria is outside this amendment and would be `POTENTIALLY_SCIENTIFIC`, therefore blocking pending separate Human review. Device-dependent numerical differences under the same specified FP32 mathematics are an execution property to be monitored, not permission to alter scientific rules.

## Implementation gate

Normative promotion is currently blocked by `HD-A-GPU-007-CLARIFICATION-01`. After Human confirmation, promotion would authorize implementation work but would not certify it. Before any CUDA benchmark: implement; approve the alternative same-device mechanism for UUID-unavailable environments; review the concrete CUDA process-start value for the pinned stack and target hardware; run the full future test/VERIFY plan; and produce target-environment preflight evidence. No current CUDA support claim is made.
