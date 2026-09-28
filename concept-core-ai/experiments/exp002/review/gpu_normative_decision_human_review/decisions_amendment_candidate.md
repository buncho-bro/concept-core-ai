# Proposed Amendment to `experiments/exp002/decisions.md`

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

This candidate proposes appending the following decision section. It is not authoritative until separately promoted by Human review.

# 41. GPU-Capable Execution and Performance Governance

## Decision boundary

CUDA FP32 may be implemented and benchmarked as an execution/performance path for the unchanged Experiment 002. This is an execution-governance change, not a new scientific experiment.

```text
GPU-CAPABLE GOVERNANCE != GPU SELECTED
```

The later approved benchmark may select CPU. Neither this amendment nor the existence of CUDA hardware selects CUDA.

## Scientific invariants

Dataset generation and splits, held-out combinations, reconstruction objective, per-image balanced loss, architecture, latent dimension, Adam configuration, learning rate, 50 epochs, batch size 128, probes, C grid, scaler semantics, distance definitions, bootstrap mathematics and iterations, reconstruction gate, success classification, formal master seeds, and seed derivation remain unchanged.

AMP, enabled mixed-precision autocast, GradScaler, FP16, BF16, TF32, quantization, scientific batch-size changes, automatic precision or device fallback, and scientific-metric performance selection are prohibited.

## Execution and performance governance

CPU and CUDA are complete candidate configurations, not isolated device labels. A CUDA/hybrid candidate must be designed independently; the old CPU optimum is not presumed optimal. Technical reliability and memory feasibility are eligibility gates. Eligible candidates are ranked only by median wall-clock time under the approved five-observation and conditional-plus-five procedure. Scientific outcomes are neither eligibility evidence nor ranking evidence.

Memory feasibility means successful approved non-formal workload completion without OOM, with peak allocated and peak reserved memory recorded. No arbitrary VRAM reserve percentage is introduced.

## Original canonical formal set

If CUDA is selected, the original five-run canonical set freezes and exact-matches the physical GPU UUID/model, NVIDIA driver, execution-relevant PyTorch/CUDA identity, and cuDNN identity, along with deterministic backend, TF32-disabled, process-start, precision, and complete performance policy. All five runs use the same physical GPU.

Hardware failure or replacement cannot be hidden inside the set. A replacement requires Human authorization, a new baseline/version, and a complete new five-run canonical set. The first-registration-wins and non-replacing retry rules remain unchanged.

## Future independent reproduction

An independent reproduction may use another CUDA GPU only after satisfying the approved equivalence, fresh preflight, policy, and provenance requirements. It is explicitly a different reproduction set. The exact driver/GPU identities of the original canonical set are not universal scientific conditions, and reproduction runs never replace original canonical members.

## Determinism, process start, and RNG

Deterministic CUDA process-start policy is mandatory. The exact `CUBLAS_WORKSPACE_CONFIG` value remains intentionally deferred to pinned-version implementation design/review and target-GPU validation. It must be frozen and verified before CUDA benchmarking and formal baseline freeze; a current source literal is not approval.

Existing seed semantics are preserved. Explicit CUDA RNG initialization uses the existing `model_seed` where required, with no new seed purpose and no new normative model-construction RNG save/restore operation under the current architecture.

## Preflight, registration, and technical INVALID

A fresh, seed-free, non-scientific CUDA preflight occurs before registration. Failure creates no registration. Success is followed by registration and then a separate fresh formal worker. That worker revalidates all frozen identity and policy fields before scientific work. Failure after registration is an immutable technical `INVALID` associated with the registered attempt.

This sequence reconciles preventive device validation with the requirement that the first registered attempt cannot be erased after formal execution is launched.

## Benchmark decision

Each eligible candidate receives exactly five initial repetitions. Preserve all timings, order, min, max, and median. If relevant min-max intervals overlap, every relevant candidate receives exactly five additional repetitions and all ten observations are used. If overlap remains, record `PERFORMANCE_TIE_OR_UNCERTAIN` and retain CPU as lower-complexity incumbent without claiming speed superiority.

## Governance lineage versus runtime-manifest lineage

`exp002-baseline-003/v1` is the first persistent runtime baseline under the post-change GPU-capable governance. The reported baseline-001 loss and Human-approved baseline-002 identity remain governance history. Their unavailable runtime manifests are not recreated, and baseline-003 does not invent a runtime predecessor link to them.

The baseline-003 identity is not a CUDA selection. Its eventual manifest binds whichever complete configuration survives approved VERIFY and wall-clock-only benchmark selection.

## Rationale

CUDA can reduce execution time without changing the research question, but it expands nondeterminism, device identity, native-library, memory, and process-start risks. The exact-identity canonical policy makes the original formal set internally coherent; the separate reproduction policy avoids converting one GPU stack into a universal scientific requirement. The preflight/worker split prevents avoidable registrations while preserving immutable audit semantics after registration.

