# Approved Human Decision Package

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

Decisions `HD-A-GPU-001` through `HD-A-GPU-015` are approved Human input for this recovery candidate. The separately labeled `HD-A-GPU-007-CLARIFICATION-01` is a new proposal with `HUMAN_CONFIRMATION_REQUIRED`. None of these entries by itself promotes the candidate into authoritative `spec.md` or `decisions.md`.

## HD-A-GPU-001 — NVIDIA driver identity

For the original canonical five-run set, freeze the exact NVIDIA driver identity in the baseline and require an exact match for all five runs. This exact identity is not a universal requirement for future independent reproduction.

## HD-A-GPU-002 — PyTorch/CUDA execution identity

For the original canonical set, freeze and exact-match the execution-relevant PyTorch identity and CUDA interface/runtime identity, including `torch.version.cuda`. An installed but unused system CUDA toolkit is provenance-only and is not substituted for the runtime actually used by PyTorch.

## HD-A-GPU-003 — cuDNN identity

For the original canonical set, freeze the exact execution-relevant cuDNN identity and require an exact match for all five runs.

## HD-A-GPU-004 — physical GPU identity

All five members of a CUDA-selected original canonical set must execute on the same physical GPU, and the GPU model must match the frozen baseline identity. When the approved runtime environment exposes a stable/reliable GPU UUID, record, freeze, and exact-match it across all five runs. Lack of a reliably available UUID does not by itself make CUDA infeasible; record that absence explicitly and use the alternative same-physical-device provenance/validation mechanism approved during implementation review and VERIFY. This candidate does not invent that mechanism. A replacement physical GPU cannot supply a member of the existing canonical set even when it is the same model; replacement requires Human authorization, a new baseline/version, and a new five-run canonical set. Physical GPU identity is not a universal scientific condition for independent reproduction.

## HD-A-GPU-005 — independent reproduction hardware

A future independent reproduction may use a different CUDA GPU if it passes the approved equivalence, preflight, policy, and provenance requirements. Such runs are a distinct reproduction set and never replacement members of the original canonical set.

## HD-A-GPU-006 — initial benchmark repetitions

Each eligible complete performance candidate receives exactly five initial measured repetitions. The primary statistic is median wall-clock time. Retain every individual observation and the minimum, maximum, and median.

## HD-A-GPU-007 — overlap and uncertainty

If min-max timing intervals overlap after the five initial measurements, perform exactly five additional measurements for every relevant candidate and recompute using all ten observations. If the intervals still overlap, record `PERFORMANCE_TIE_OR_UNCERTAIN` and retain CPU as the lower-complexity incumbent without claiming CPU performance superiority.

The approved wording above did not define “relevant candidate” deterministically for three or more candidates. The proposed clarification in `HD-A-GPU-007-CLARIFICATION-01` below is new and is not yet Human-approved.

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

Technical/runtime reliability is an eligibility gate. Rank eligible candidates using the approved wall-clock procedure only. Training loss, validation loss, reconstruction quality, probe results, distance results, bootstrap results, and every other scientific outcome are forbidden as eligibility, ranking, stopping, repetition-count, or selection evidence.

Technical failures include OOM, process or device failure, backend/deterministic-policy failure, preflight or required-provenance failure, and other technical inability to execute the predefined candidate. Preserve every failed measured repetition, its order, and its failure evidence. A failed measured repetition is not silently deleted, replaced, rerun, or converted into a successful timing to manufacture the requested number of successful observations. No result-dependent retry policy may be introduced after measurements begin. A candidate failing the preregistered reliability rule is `PERFORMANCE_INFEASIBLE` and receives no artificial timing or wall-clock rank. If no eligible candidate remains, freeze neither a performance configuration nor baseline-003; return to Human/benchmark-design review without consulting scientific outcomes. Benchmark eligibility terminology remains separate from formal-run `VALID`, `INVALID`, and `EXPERIMENTAL_FAILURE` and from experiment-level classification.

## HD-A-GPU-007-CLARIFICATION-01 — proposed deterministic expansion set

```text
STATUS: HUMAN_CONFIRMATION_REQUIRED
```

This is a new Human clarification candidate, not a previously approved decision.

After exactly five scheduled initial measured repetitions per candidate, and only when every candidate still eligible under the preregistered reliability rule has five valid timing observations without replacement:

1. identify the eligible candidate with the numerically lowest five-observation median;
2. compare its five-observation `[minimum, maximum]` interval with every other eligible candidate's interval;
3. if no interval overlaps it, do not expand and select by the approved median rule;
4. if at least one interval overlaps it, define `RELEVANT_CANDIDATES_FOR_EXPANSION = ALL ELIGIBLE CANDIDATES`;
5. schedule exactly five additional measured repetitions for every eligible candidate; when those attempts complete validly under the confirmed reliability rule, each expanded candidate has exactly ten valid observations;
6. recompute minimum, maximum, and median from all ten observations for every eligible candidate;
7. identify the numerically lowest all-ten median and compare its all-ten interval with every other eligible candidate's all-ten interval;
8. if no overlap remains, select by the approved median rule;
9. if any overlap remains, record `PERFORMANCE_TIE_OR_UNCERTAIN` and retain CPU as the lower-complexity incumbent without claiming CPU speed or statistical superiority.

Expansion applies only to candidates remaining eligible under the reliability rule. Failed repetitions are never replaced to manufacture five or ten valid observations. The precise preregistered handling of a candidate that fails during the initial stage, becomes ineligible before expansion, or fails during expansion is not uniquely fixed by the existing approved decisions. Human confirmation of this clarification must also settle those edge cases before benchmark design can be approved; scientific metrics cannot settle them.

## Cross-cutting boundary

These decisions govern execution and performance only. They do not change any scientific condition. CUDA execution is FP32 only; AMP, autocast-based mixed precision, GradScaler, FP16, BF16, TF32, quantization, automatic batch-size changes, automatic precision changes, and silent CPU fallback are prohibited.
