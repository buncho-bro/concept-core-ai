# Final Conflict Review

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

| Conflict | Classification | Normative treatment | Implementation consequence |
|---|---|---|---|
| C-GPU-001 — CPU-only scope vs CUDA-capable governance | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING | Amend §§44–47 to allow CUDA FP32 while preserving every scientific invariant. GPU-capable does not mean GPU-selected. | Device-aware configuration and verified CUDA path are required before use. |
| C-GPU-002 — registration-before-worker vs pre-registration preflight | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Seed-free fresh preflight occurs before registration; success permits append-only registration; a separate fresh worker revalidates. | Launcher flow must add a preflight subprocess without importing scientific/native libraries too early. |
| C-GPU-003 — device class vs exact canonical identity | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Original CUDA canonical set binds the same physical GPU, exact model and software stack, plus exact stable/reliable UUID when available; otherwise it records UUID absence and uses an approved alternative same-device mechanism. Reproduction hardware is a distinct set. | Baseline, runtime validation, artifacts, and aggregation need conditional UUID and alternative-evidence fields. |
| C-GPU-004 — CPU schema vs CUDA policy fields | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Complete config must bind device, FP32, TF32-off, deterministic policy, RNG/process-start fields, and no-fallback behavior. | Versioned schemas and validators must be extended. |
| C-GPU-005 — environment fingerprint vs GPU provenance | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Bind driver, PyTorch/CUDA/cuDNN, model, conditional reliable UUID or approved alternative same-device evidence, backend and process-start provenance; unused toolkit remains provenance-only. | Environment capture and exact-match validation must be CUDA-aware without making UUID availability universal. |
| C-GPU-006 — first-registration-wins vs post-registration revalidation failure | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Revalidation failure after registration is immutable technical `INVALID`; it never removes or replaces the canonical registration. | Worker-start/revalidation failure artifacts and aggregation validation must preserve the attempt. |
| C-GPU-007 — successor logic vs lost 001 / never-frozen 002 / first persistent 003 | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | baseline-003 is first persistent runtime baseline under new governance. Preserve 001/002 governance facts without fabricating manifests or a runtime predecessor chain. | Freeze logic/schema must support truthful governance lineage distinct from runtime-manifest predecessor. |
| C-GPU-008 — unspecified repetitions/statistic/tie/reliability interaction | REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED; HUMAN_CONFIRMATION_REQUIRED; STILL_BLOCKING | Approved five/+five, median, uncertainty, audit, and no-replacement rules remain. `HD-A-GPU-007-CLARIFICATION-01` proposes all eligible candidates as the expansion set, but its failure-stage edge cases require Human confirmation. | Benchmark schema must preserve failed observations and enforce the confirmed expansion/eligibility rules without post-hoc retries. |

## Blocking assessment

Seven conflicts have complete Human-approved treatment. C-GPU-008 has a coherent clarification candidate but remains promotion-blocking pending Human confirmation. Implementation review remains required because current source/schema does not yet enforce the policy.

```text
CONFLICTS_RESOLVED_OR_CONSTRAINED: 7 / 8
HUMAN_CONFIRMATION_REQUIRED: HD-A-GPU-007-CLARIFICATION-01
STILL_BLOCKING: 1
```

No conflict is marked resolved merely because it could be implemented later. Promotion is blocked by the unconfirmed clarification; after confirmation, promotion still would not establish implementation conformance, and implementation, tests, VERIFY, and benchmark evidence remain separate gates.
