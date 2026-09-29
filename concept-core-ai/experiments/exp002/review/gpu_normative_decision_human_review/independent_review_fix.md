# Independent Review Fix Record

> **NON-AUTHORITATIVE REVIEW-CANDIDATE FIX**

## Review result before fix

```text
NOT_READY_FOR_NORMATIVE_PROMOTION
```

The independent review identified exactly three findings. This record does not promote authoritative documents, approve implementation, select a device, run a benchmark, or freeze a baseline.

## RF-GPU-001 — GPU UUID availability qualifier

**Disposition: RESOLVED**

The candidate now requires the same physical GPU and exact frozen model for a CUDA-selected original canonical set. A stable/reliable UUID is recorded, frozen, and exact-matched when exposed. UUID absence/unreliability is recorded and invokes an alternative same-device provenance/validation mechanism to be established during implementation review and VERIFY; this fix does not invent that mechanism. Same-model physical replacement still requires Human authorization, a new baseline/version, and a new five-run set.

Files changed for RF-GPU-001:

- `human_decisions.md`
- `spec_amendment_candidate.md`
- `decisions_amendment_candidate.md`
- `ambiguities_final.md`
- `conflicts_final.md`
- `traceability.md`
- `implementation_impact.md`
- `test_verify_plan.md`
- `READINESS.md`

## RF-GPU-002 — failed performance observations and reliability governance

**Disposition: RESOLVED**

The candidate now defines technical failures, preserves every failed measured repetition and attempt order, prohibits silent deletion/replacement/rerun and post-hoc retry policy, uses `PERFORMANCE_INFEASIBLE` only as a benchmark-specific eligibility term, assigns no artificial timing, and forbids performance/baseline freeze when no eligible candidate remains. Scientific metrics are excluded from eligibility, stopping, repetition count, ranking, and selection.

Files changed for RF-GPU-002:

- `human_decisions.md`
- `spec_amendment_candidate.md`
- `decisions_amendment_candidate.md`
- `ambiguities_final.md`
- `conflicts_final.md`
- `traceability.md`
- `implementation_impact.md`
- `test_verify_plan.md`
- `READINESS.md`

## RF-GPU-003 — deterministic “relevant candidates” definition

**Disposition: HUMAN_CONFIRMATION_REQUIRED**

New clarification candidate `HD-A-GPU-007-CLARIFICATION-01` proposes: after exactly five scheduled initial attempts and five valid observations for every candidate remaining eligible under the confirmed rule, compare the initial lowest-median candidate's interval with all others; any overlap makes `RELEVANT_CANDIDATES_FOR_EXPANSION = ALL ELIGIBLE CANDIDATES`; schedule exactly five more repetitions for every eligible candidate; where all complete validly under the confirmed reliability rule, recompute from all ten valid observations; compare the all-ten lowest-median interval with all others; persistent overlap records `PERFORMANCE_TIE_OR_UNCERTAIN` and retains CPU without a superiority claim.

Human confirmation must also settle preregistered handling for failure during the initial stage, ineligibility before expansion, and failure during expansion. The fix does not infer those rules from outcomes or scientific metrics.

Files changed for RF-GPU-003:

- `README.md`
- `recovery_record.md`
- `human_decisions.md`
- `spec_amendment_candidate.md`
- `decisions_amendment_candidate.md`
- `ambiguities_final.md`
- `conflicts_final.md`
- `traceability.md`
- `implementation_impact.md`
- `test_verify_plan.md`
- `READINESS.md`
- `independent_review_fix.md`

## Invariants

- Scientific conditions changed: **NO**.
- Authoritative `spec.md` changed: **NO**.
- Authoritative `decisions.md` changed: **NO**.
- Implementation changed: **NO**.
- Tests changed: **NO**.
- Formal seeds used: **NONE**.
- Formal attempts registered: **0**.
- Formal scientific runs: **0**.
- Performance benchmark run: **NO**.
- CPU/CUDA selected: **NO**.
- baseline-003 runtime frozen: **NO**.
- Historical candidate fabricated: **NO**.

## Post-fix readiness

```text
NOT_READY_FOR_NORMATIVE_PROMOTION
HUMAN_CONFIRMATION_REQUIRED:
HD-A-GPU-007-CLARIFICATION-01
```
