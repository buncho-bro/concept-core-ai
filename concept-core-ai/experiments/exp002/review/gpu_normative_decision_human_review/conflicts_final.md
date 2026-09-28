# Final Conflict Review

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

| Conflict | Classification | Normative treatment | Implementation consequence |
|---|---|---|---|
| C-GPU-001 — CPU-only scope vs CUDA-capable governance | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING | Amend §§44–47 to allow CUDA FP32 while preserving every scientific invariant. GPU-capable does not mean GPU-selected. | Device-aware configuration and verified CUDA path are required before use. |
| C-GPU-002 — registration-before-worker vs pre-registration preflight | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Seed-free fresh preflight occurs before registration; success permits append-only registration; a separate fresh worker revalidates. | Launcher flow must add a preflight subprocess without importing scientific/native libraries too early. |
| C-GPU-003 — device class vs exact canonical identity | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Original CUDA canonical set binds exact UUID/model plus software stack; reproduction hardware is a distinct set under equivalence rules. | Baseline, runtime validation, artifacts, and aggregation need exact identity fields. |
| C-GPU-004 — CPU schema vs CUDA policy fields | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Complete config must bind device, FP32, TF32-off, deterministic policy, RNG/process-start fields, and no-fallback behavior. | Versioned schemas and validators must be extended. |
| C-GPU-005 — environment fingerprint vs GPU provenance | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Bind driver, PyTorch/CUDA/cuDNN, UUID/model, backend and process-start provenance; unused toolkit remains provenance-only. | Environment capture and exact-match validation must be CUDA-aware. |
| C-GPU-006 — first-registration-wins vs post-registration revalidation failure | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Revalidation failure after registration is immutable technical `INVALID`; it never removes or replaces the canonical registration. | Worker-start/revalidation failure artifacts and aggregation validation must preserve the attempt. |
| C-GPU-007 — successor logic vs lost 001 / never-frozen 002 / first persistent 003 | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | baseline-003 is first persistent runtime baseline under new governance. Preserve 001/002 governance facts without fabricating manifests or a runtime predecessor chain. | Freeze logic/schema must support truthful governance lineage distinct from runtime-manifest predecessor. |
| C-GPU-008 — unspecified repetitions/statistic/tie policy | RESOLVED_BY_HUMAN_DECISION; REQUIRES_NORMATIVE_WORDING; IMPLEMENTATION_REVIEW_REQUIRED | Exactly 5 initial, conditional exactly +5, all observations retained, median primary, persistent overlap means uncertainty and CPU incumbent. | Benchmark and selection schemas must enforce counts, overlap set, all-10 recomputation, and metric exclusion. |

## Blocking assessment

All eight conflicts have coherent proposed normative treatment. Six require later implementation review because current source/schema does not yet enforce the policy; that is expected at this documentation stage.

```text
CONFLICTS_RESOLVED_OR_CONSTRAINED: 8 / 8
STILL_BLOCKING: 0
```

No conflict is marked resolved merely because it could be implemented later: each has an explicit Human-approved normative rule. Promotion does not itself establish implementation conformance; implementation, tests, VERIFY, and benchmark evidence remain separate gates.

