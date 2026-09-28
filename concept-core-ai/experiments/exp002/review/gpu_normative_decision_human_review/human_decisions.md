# Approved Human Decision Package

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

All decisions below are approved Human input for this recovery candidate. They do not themselves promote the candidate into authoritative `spec.md` or `decisions.md`.

## HD-A-GPU-001 — NVIDIA driver identity

For the original canonical five-run set, freeze the exact NVIDIA driver identity in the baseline and require an exact match for all five runs. This exact identity is not a universal requirement for future independent reproduction.

## HD-A-GPU-002 — PyTorch/CUDA execution identity

For the original canonical set, freeze and exact-match the execution-relevant PyTorch identity and CUDA interface/runtime identity, including `torch.version.cuda`. An installed but unused system CUDA toolkit is provenance-only and is not substituted for the runtime actually used by PyTorch.

## HD-A-GPU-003 — cuDNN identity

For the original canonical set, freeze the exact execution-relevant cuDNN identity and require an exact match for all five runs.

## HD-A-GPU-004 — physical GPU identity

All five members of the original canonical set must execute on the same physical GPU, identified by exact GPU UUID and model. A replacement GPU cannot supply a member of that canonical set; replacement requires a new Human-authorized baseline and a new five-run canonical set.

## HD-A-GPU-005 — independent reproduction hardware

A future independent reproduction may use a different CUDA GPU if it passes the approved equivalence, preflight, policy, and provenance requirements. Such runs are a distinct reproduction set and never replacement members of the original canonical set.

## HD-A-GPU-006 — initial benchmark repetitions

Each eligible complete performance candidate receives exactly five initial measured repetitions. The primary statistic is median wall-clock time. Retain every individual observation and the minimum, maximum, and median.

## HD-A-GPU-007 — overlap and uncertainty

If min-max timing intervals overlap after the five initial measurements, perform exactly five additional measurements for every relevant candidate and recompute using all ten observations. If the intervals still overlap, record `PERFORMANCE_TIE_OR_UNCERTAIN` and retain CPU as the lower-complexity incumbent without claiming CPU performance superiority.

## HD-A-GPU-008 — complete hybrid candidates

Benchmark complete predefined CPU/CUDA performance configurations. Do not assume the prior CPU optimum is also the optimum for a CUDA/hybrid execution path. All knobs in a candidate must be fixed before its measurements begin.

## HD-A-GPU-009 — GPU memory feasibility

GPU memory feasibility is established by successful completion of the approved representative/full non-formal workload without OOM. Record peak allocated and peak reserved memory. Do not invent a fixed VRAM-percentage reserve threshold.

## HD-A-GPU-010 — deterministic CUDA process-start policy

A required deterministic CUDA process-start policy must be frozen. The concrete `CUBLAS_WORKSPACE_CONFIG` value is intentionally not yet Human-approved. It must be established later through version-specific implementation design/review and target-hardware validation, then verified before benchmarking and baseline freeze. This deferral is an implementation-design/verification obligation, not a reopened Human normative ambiguity.

## HD-A-GPU-011 — CUDA RNG and seed semantics

Preserve existing seed semantics. Where explicit CUDA RNG initialization is required, use the existing `model_seed`; introduce no CUDA-specific seed purpose. Under the current architecture there is no new normative requirement to save and restore global RNG state around model construction.

## HD-A-GPU-012 — fresh preflight before registration

Run a dedicated, fresh, seed-free, non-scientific CUDA preflight subprocess before any attempt registration. On successful preflight: register the attempt, then launch a separate fresh formal worker, which must revalidate the frozen environment and device policy.

## HD-A-GPU-013 — revalidation failure semantics

A pre-registration preflight failure creates no attempt registration. A post-registration formal-worker revalidation failure produces an immutable registered technical `INVALID`; first-registration-wins and audit preservation continue to apply.

## HD-A-GPU-014 — baseline-003 lineage

`exp002-baseline-003/v1` is the first persistent runtime baseline under post-change GPU-capable governance. Do not fabricate baseline-001 or baseline-002 runtime manifests. Preserve the historical governance facts about those identities separately from runtime-manifest lineage.

## HD-A-GPU-015 — eligibility and ranking

Technical/runtime reliability is an eligibility gate. Rank eligible candidates using the approved wall-clock procedure only. Training loss, validation loss, reconstruction quality, probe results, distance results, bootstrap results, and every other scientific outcome are forbidden inputs to performance selection.

## Cross-cutting boundary

These decisions govern execution and performance only. They do not change any scientific condition. CUDA execution is FP32 only; AMP, autocast-based mixed precision, GradScaler, FP16, BF16, TF32, quantization, automatic batch-size changes, automatic precision changes, and silent CPU fallback are prohibited.

