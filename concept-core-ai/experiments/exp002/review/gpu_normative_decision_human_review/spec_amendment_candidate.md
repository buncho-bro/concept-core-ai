# Proposed Amendment to `experiments/exp002/spec.md`

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

This is a patch-form proposal, not an authoritative specification. Unmentioned sections remain unchanged.

## 1. Replace §44, “Performance Optimization,” with

### 44. Performance Optimization and Execution Device

Experiment 002 permits implementation-level CPU performance optimization and CUDA FP32 execution as performance paths. CUDA changes only where the already-defined float32 mathematics executes; it does not change that mathematics.

An eligible performance candidate is a complete configuration fixed before measurement. It includes at least:

```text
device and device class
torch thread configuration
OMP/MKL process-start configuration
DataLoader worker configuration
precision policy
deterministic backend policy
CUDA process-start policy when CUDA is used
```

CPU candidates may include the existing threading, DataLoader, caching, vectorization, chunking, and I/O knobs. CUDA candidates may additionally include approved device-transfer and execution-path choices that preserve the same FP32 operations and scientific outputs. The previously selected CPU configuration MUST NOT be assumed optimal for a CUDA/hybrid path.

`GPU-CAPABLE GOVERNANCE != GPU SELECTED`. The approved benchmark may select CPU.

## 2. Replace §45, “Prohibited Performance Changes,” with

### 45. Scientific Invariants and Prohibited Performance Changes

Performance work MUST NOT change dataset generation or contents; splits or held-out combinations; reconstruction objective or aggregation; architecture or latent dimension; optimizer or learning rate; 50 epochs; batch size 128; probe definitions, C grid, scaler semantics, distance definitions, bootstrap mathematics or iteration count; reconstruction gate; success classification; formal master seeds; or seed derivation.

The following are prohibited for both benchmarking and formal execution:

```text
AMP
autocast-enabled mixed precision
GradScaler
FP16
BF16
TF32
quantization
automatic batch-size reduction
automatic precision fallback
silent CPU fallback
scientific-metric-based performance selection
```

All model inputs, parameters, gradients, optimizer state, loss calculations, reconstruction metrics, and latent exports remain float32 under the existing scientific definition.

## 3. Replace §46, “Performance Benchmarking,” with

### 46. Performance Benchmarking and Selection

Performance benchmarking is non-formal and occurs only after the GPU-capable implementation has passed VERIFY and before baseline freeze or formal execution. Complete CPU and CUDA configurations MUST be predefined before their measurements begin.

Technical/runtime reliability is an eligibility gate. An eligible CUDA candidate must pass the approved fresh preflight, deterministic/backend checks, required provenance checks, and a successful approved representative/full non-formal workload without OOM. Technical failure includes OOM; process or device failure; backend- or deterministic-policy failure; preflight or required-provenance failure; and other technical inability to execute the predefined candidate. Record GPU memory peak allocated and peak reserved; no fixed VRAM-percentage threshold applies.

Preserve every attempted measured repetition, execution order, observed timing when valid, and technical failure evidence. A failed measured repetition MUST NOT be silently discarded, replaced, rerun, or converted into a successful timing to obtain five or ten successful measurements. No result-dependent retry policy may be introduced after measurement begins. A candidate that fails its preregistered reliability rule is `PERFORMANCE_INFEASIBLE`; it receives no artificial timing and does not enter wall-clock ranking. This benchmark-specific status is separate from formal-run `VALID`, `INVALID`, and `EXPERIMENTAL_FAILURE` and from experiment-level classification.

Every predefined candidate is scheduled for exactly five initial measured repetitions. A valid timing observation exists only for a successfully completed measured repetition; failed attempts count in the immutable attempt record and are not replaced. For candidates that remain eligible and have five valid timing observations under the confirmed reliability rule, preserve candidate configuration, execution order, every observation, minimum, maximum, and median. Median wall-clock seconds is the sole primary ranking statistic. Scientific metrics MUST NOT be eligibility, ranking, stopping, repetition-count, or selection evidence.

The following deterministic expansion rule is proposed by `HD-A-GPU-007-CLARIFICATION-01` and remains `HUMAN_CONFIRMATION_REQUIRED`: identify the eligible candidate with the lowest five-valid-observation median and compare its `[minimum, maximum]` interval against every other eligible candidate with five valid observations. If none overlaps, do not expand. If at least one overlaps, `RELEVANT_CANDIDATES_FOR_EXPANSION = ALL ELIGIBLE CANDIDATES`; every eligible candidate is scheduled for exactly five additional measured repetitions. When all additional attempts complete validly under the confirmed reliability rule, minimum, maximum, and median are recomputed from all ten valid observations. Compare the lowest all-ten median candidate's interval against every other eligible candidate's all-ten interval. If no overlap remains, select by median. If any overlap remains, record `PERFORMANCE_TIE_OR_UNCERTAIN` and retain CPU as the lower-complexity incumbent without claiming CPU speed or statistical superiority.

Expansion applies only to candidates still eligible under the reliability rule, and failed repetitions are never replaced to manufacture five or ten valid observations. Before benchmark approval, Human confirmation MUST settle the preregistered handling when a candidate fails during the initial stage, becomes ineligible before expansion, or fails during expansion. No performance configuration or baseline-003 may be frozen if no eligible candidate remains; return to Human/benchmark-design review without consulting scientific outcomes.

The selected complete configuration is frozen before formal execution and is identical across the five canonical runs.

## 4. Replace §47, “Formal Run Consistency,” with

### 47. Formal Run Consistency and Canonical CUDA Identity

All five original canonical runs use the same git commit, scientific implementation fingerprint, required dependency environment, complete frozen performance configuration, device class, and backend/precision policy.

For a CUDA-selected original canonical set, the baseline additionally freezes and all five runs exact-match:

```text
physical GPU model
stable/reliable physical GPU UUID when exposed by the approved runtime
explicit UUID-unavailable record and approved alternative same-device evidence otherwise
NVIDIA driver identity
execution-relevant PyTorch version/build identity
torch.version.cuda and the CUDA runtime/interface used by PyTorch
execution-relevant cuDNN identity
deterministic backend settings
TF32-disabled state
required CUDA process-start policy
```

An installed but unused system CUDA toolkit is recorded as provenance-only and does not replace the execution-relevant CUDA identity.

All five original canonical runs execute on the same physical GPU and exact-match the frozen GPU model. When a stable/reliable GPU UUID is exposed by the approved runtime, the baseline records and freezes it and all five runs exact-match it. UUID absence or unreliable exposure does not alone prohibit CUDA; that fact is recorded explicitly and the implementation uses an alternative same-physical-device provenance/validation mechanism established during implementation review and VERIFY. This amendment does not invent that mechanism. A GPU failure or physical replacement cannot silently complete the set, even with the same model. Replacement requires Human authorization, a new baseline/version, and a new five-run canonical set. No run from a replacement device becomes a member of the original set.

A future independent reproduction may use a different CUDA GPU only under the then-approved equivalence, preflight, policy, and complete provenance requirements. It is labeled as a distinct reproduction set and is never substituted into the original canonical set. Cross-hardware bitwise equality remains unnecessary; within-set frozen-identity rules remain mandatory.

There is no silent CUDA-to-CPU fallback. A configured CUDA path that cannot satisfy the baseline becomes a technical failure under the attempt-governance rules.

## 5. Insert new §47A after §47

### 47A. CUDA Determinism, RNG, Preflight, and Memory Provenance

CUDA execution remains FP32. TF32 is disabled for every applicable backend. Deterministic backend behavior and deterministic algorithms required by the verified implementation are enabled and verified; incompatible nondeterministic operations fail eligibility or execution rather than silently relaxing policy.

The required CUDA process-start environment is established before importing CUDA/native scientific libraries. Its concrete `CUBLAS_WORKSPACE_CONFIG` value is not established by this amendment. Before CUDA benchmarking, implementation review MUST select a value compatible with the pinned PyTorch/CUDA/cuDNN stack, validate it on the target GPU, freeze the approved value in benchmark configuration and evidence, and VERIFY that it was present before native scientific imports. The later formal baseline binds the verified value. No implementation default or existing literal becomes normatively approved merely by existing in source.

Existing seed purposes are unchanged. Explicit CUDA RNG initialization, if required, uses the existing `model_seed`; no new CUDA-specific seed purpose is introduced. No new normative model-construction global-RNG save/restore procedure is required under the current architecture.

Before registration of a CUDA formal attempt, the launcher runs a dedicated seed-free, non-scientific preflight in a fresh subprocess. The preflight validates at least device availability, expected model, stable/reliable UUID when available or the approved alternative same-device evidence when not, driver, PyTorch/CUDA/cuDNN identity, FP32/TF32 and deterministic backend policy, required process-start policy, and a minimal allocation/operation/synchronization path. It performs no dataset generation, model initialization using a formal seed, training, evaluation, or scientific metric calculation.

A failed preflight creates no registration. After a successful preflight, the launcher registers the attempt exactly once and launches a separate fresh formal worker. The worker revalidates the frozen identity and policies before scientific execution. Failure after registration is the immutable technical status `INVALID` for that registered attempt.

Approved non-formal feasibility and formal artifacts record GPU memory telemetry including peak allocated and peak reserved memory. OOM causes candidate ineligibility or registered technical `INVALID`, according to whether it occurs before or after registration. It never triggers automatic batch-size, precision, or CPU fallback.

Checkpoints remain device-portable state artifacts and MUST be loadable with explicit `map_location` for approved CPU analysis of CUDA-generated artifacts. CPU analysis MUST consume recorded artifacts without retraining or changing scientific calculations.

## 6. Append to §50A, “Formal Baseline and Canonical Attempt Governance”

Under the post-change GPU-capable governance, the first persistent runtime baseline identity is:

```text
exp002-baseline-003/v1
```

This identity is GPU-capable but does not preselect CUDA. The complete selected CPU or CUDA performance configuration is frozen only after approved VERIFY and benchmark selection. Historical baseline-001 and baseline-002 facts remain governance history; unavailable runtime manifests MUST NOT be recreated or invented. Consequently baseline-003 may have no runtime-manifest predecessor even while its governance record explains the prior identities.

For CUDA formal attempts, the registration sequence is:

```text
fresh seed-free non-scientific preflight
-> successful preflight
-> append-only registration
-> separate fresh formal worker
-> worker revalidation
-> scientific execution
```

Preflight failure leaves the seed slot unregistered. Any launch or revalidation failure after registration preserves the registration and records technical `INVALID`. Formal aggregation verifies the CUDA identity and policy evidence bound to the baseline and every canonical artifact in addition to all existing checks. An identity/policy mismatch makes the affected canonical attempt invalid and prevents a false complete-set claim; retries do not replace it.

## 7. Status of all other sections

Sections 0–43, 48–50, 51, and 52 retain their existing scientific and interpretive meaning except for the cross-references introduced above. No scientific equation, threshold, sample, seed, or aggregation rule is amended.
# Approved clarification — deterministic benchmark procedure

`HD-A-GPU-007-CLARIFICATION-01` is Human-approved. Each predefined candidate receives exactly five initial measured repetitions. A technical failure immediately makes that candidate `PERFORMANCE_INFEASIBLE`, stops its remaining repetitions, preserves all successful and failed attempts, timings, evidence and order, prohibits replacement/rerun, and excludes it from comparison. Zero eligible candidates returns to Human review with no selection/performance/baseline freeze; one is `SOLE_ELIGIBLE_CANDIDATE`, not a timing winner, and needs no expansion.

With two or more eligible candidates, calculate each five-observation minimum, maximum and median; choose the numerical lowest median and compare its inclusive interval to every other eligible interval (a shared boundary overlaps). No overlap selects by approved median rule. Any overlap fixes expansion membership as all candidates eligible at expansion start and schedules exactly five additional repetitions for each. An expansion failure immediately makes that candidate infeasible, preserves its initial/additional successes, failure and order, does not restart/rerun/replace or alter membership, and excludes it from final ranking.

Eligible expanded candidates have exactly ten valid observations. Zero returns to Human review; one is sole eligible without superiority claim. With two or more, recompute min/max/median across ten and compare the lowest-median interval with every other. No overlap selects by median. Persistent overlap records `PERFORMANCE_TIE_OR_UNCERTAIN` and retains CPU only if the CPU incumbent is eligible, solely as lower-complexity tie-break; otherwise return to Human review without freeze. Scientific metrics are prohibited from eligibility, expansion, stopping, ranking, tie-break and selection.
