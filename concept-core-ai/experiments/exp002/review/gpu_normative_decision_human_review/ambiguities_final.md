# Final Ambiguity Review

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

Fourteen of the 15 previously identified Human normative ambiguities are resolved by the approved decision package. A-GPU-007 remains open only for the new deterministic expansion-set clarification and its reliability-failure edge cases. Implementation details required to realize otherwise resolved policy are tracked separately and do not reopen those Human questions.

| Ambiguity | Human decision | Disposition | Resolution |
|---|---|---|---|
| A-GPU-001 | HD-A-GPU-001 | RESOLVED_BY_HUMAN_DECISION | Freeze and exact-match NVIDIA driver for the original canonical set; do not universalize it. |
| A-GPU-002 | HD-A-GPU-002 | RESOLVED_BY_HUMAN_DECISION | Freeze the actual PyTorch/CUDA execution identity, including `torch.version.cuda`; unused toolkit is provenance-only. |
| A-GPU-003 | HD-A-GPU-003 | RESOLVED_BY_HUMAN_DECISION | Freeze and exact-match the execution-relevant cuDNN identity. |
| A-GPU-004 | HD-A-GPU-004 | RESOLVED_BY_HUMAN_DECISION | Same physical GPU and frozen model for all original canonical runs. Exact-match stable/reliable UUID when available; otherwise explicitly record absence and use an alternative mechanism approved at implementation review/VERIFY. Replacement creates a new baseline and five-run set. |
| A-GPU-005 | HD-A-GPU-005 | RESOLVED_BY_HUMAN_DECISION | Different hardware is allowed only for a distinct independent reproduction satisfying equivalence/preflight/provenance. |
| A-GPU-006 | HD-A-GPU-006 | RESOLVED_BY_HUMAN_DECISION | Exactly five initial observations; median primary; retain observations, min, max, median. |
| A-GPU-007 | HD-A-GPU-007; proposed HD-A-GPU-007-CLARIFICATION-01 | HUMAN_CONFIRMATION_REQUIRED | Approved +5/uncertainty principles remain. Proposed deterministic rule expands all eligible candidates when the initial lowest-median interval overlaps any other; Human confirmation must also settle eligibility-failure edge cases. |
| A-GPU-008 | HD-A-GPU-008 | RESOLVED_BY_HUMAN_DECISION | Benchmark predefined complete CPU/CUDA configurations; do not transplant the CPU optimum by assumption. |
| A-GPU-009 | HD-A-GPU-009 | RESOLVED_BY_HUMAN_DECISION | Successful approved workload without OOM plus allocated/reserved telemetry; no fixed percentage. |
| A-GPU-010 | HD-A-GPU-010 | RESOLVED_BY_HUMAN_DECISION | Normative procedure is fixed; concrete `CUBLAS_WORKSPACE_CONFIG` is deliberately delegated to version-specific design, validation, freeze, and VERIFY. |
| A-GPU-011 | HD-A-GPU-011 | RESOLVED_BY_HUMAN_DECISION | Existing `model_seed` covers explicit CUDA RNG; no new seed purpose or normative RNG save/restore. |
| A-GPU-012 | HD-A-GPU-012 | RESOLVED_BY_HUMAN_DECISION | Seed-free fresh preflight precedes registration; a different fresh formal worker revalidates after registration. |
| A-GPU-013 | HD-A-GPU-013 | RESOLVED_BY_HUMAN_DECISION | Preflight failure is unregistered; post-registration revalidation failure is immutable technical `INVALID`. |
| A-GPU-014 | HD-A-GPU-014 | RESOLVED_BY_HUMAN_DECISION | baseline-003 is first persistent post-change runtime baseline; baseline-001/002 history is governance-only where manifests are absent. |
| A-GPU-015 | HD-A-GPU-015 | RESOLVED_BY_HUMAN_DECISION | Reliability is eligibility; failed measured repetitions and order are immutable audit evidence, never replacement opportunities; ineligible candidates receive no artificial timing; wall clock alone ranks eligible candidates and scientific metrics are prohibited. |

## Result

```text
AMBIGUITIES_RESOLVED: 14 / 15
HUMAN_CONFIRMATION_REQUIRED: HD-A-GPU-007-CLARIFICATION-01
REMAINING_HUMAN_NORMATIVE_AMBIGUITIES: 1
```

The still-needed concrete CUDA process-start value is an implementation-design and target-validation requirement governed by a precise approved procedure. It is not an unresolved Human policy choice and must not be invented during promotion. The deterministic benchmark expansion set and its reliability-failure edge cases are a separate unresolved Human clarification and block promotion until confirmed.
