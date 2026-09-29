# Experiment 002 GPU Normative Decision — Human-Reviewed Recovery Candidate

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

## Status and scope

This directory is a new, non-authoritative normative review candidate. It was created after the previous untracked `gpu_normative_decision/` review candidate was not persisted. It is not a reconstruction of that missing directory and is not claimed to reproduce any unavailable file exactly.

An independent review of the persisted candidate returned `NOT_READY_FOR_NORMATIVE_PROMOTION` with findings `RF-GPU-001` through `RF-GPU-003`. The Human subsequently approved `HD-A-GPU-007-CLARIFICATION-01`, including its technical-failure edge-case policy. This revision records the transition `PROPOSED -> HUMAN_APPROVED`; it remains non-authoritative until separate Human authorization promotes it.

The candidate is derived from the current authoritative `spec.md` and `decisions.md`, current implementation/governance source, retained prior-review facts supplied by the Human, and approved Human Decisions `HD-A-GPU-001` through `HD-A-GPU-015`. The retained prior-review files were not present in the repository during this task and are not represented as repository artifacts here.

## Boundary

This candidate proposes CUDA FP32 as an implementation-level execution/performance path. It does not change the scientific experiment. Dataset, split, model, objective, optimizer, 50 epochs, batch size 128, evaluation mathematics, success rules, master seeds, and seed derivation remain unchanged.

The candidate does not promote or edit `spec.md` or `decisions.md`; implement CUDA support; run a CPU/CUDA benchmark; select a device; freeze `exp002-baseline-003/v1`; use formal seeds; register attempts; execute formal work; or recreate the missing historical review directory.

`GPU-CAPABLE GOVERNANCE != GPU SELECTED`. A later approved benchmark may select CPU.

## Contents

- `recovery_record.md` — truthful non-persistence and derivation record.
- `human_decisions.md` — the complete approved 15-decision package.
- `spec_amendment_candidate.md` — exact proposed amendments to the current specification.
- `decisions_amendment_candidate.md` — proposed rationale and boundary amendments.
- `ambiguities_final.md` — disposition of A-GPU-001 through A-GPU-015.
- `conflicts_final.md` — disposition of C-GPU-001 through C-GPU-008.
- `traceability.md` — decision and conflict traceability.
- `implementation_impact.md` — inspected future implementation/governance/test impact only.
- `test_verify_plan.md` — future implementation verification and benchmark-evidence plan.
- `READINESS.md` — promotion readiness conclusion.
- `independent_review_fix.md` — independent-review findings, changed-file scope, and disposition.

## Current repository facts

- Authoritative scientific specification and decisions: unchanged.
- Implementation and tests: unchanged.
- Formal attempts registered by this task: 0.
- Formal scientific runs executed by this task: 0.
- Performance benchmark executed by this task: no.
- CPU/CUDA selected by this task: no.
- Runtime baseline frozen by this task: no.
- Current candidate readiness: pending final candidate-level review.
- Human clarification: `HD-A-GPU-007-CLARIFICATION-01` is approved and recorded in `human_approval_record.md`.
