# GPU Normative Traceability

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

Abbreviations: `S44–47` = current spec performance sections; `S50A` = formal baseline/canonical governance; `D31` = CPU performance decision; `D39–40` = baseline and process-start decisions. “Later approval” means approval after normative promotion, not a missing decision in this candidate.

## Human decisions

| Decision | Ambiguity | Current sections affected | Proposed amendment | Modules likely affected | Future tests | VERIFY requirement | Benchmark evidence | Remaining Human approval |
|---|---|---|---|---|---|---|---|---|
| HD-A-GPU-001 | A-GPU-001 | S47, S50A; D39–40 | Exact driver freeze/match for original CUDA set; reproduction distinction | `artifacts.py`, `baseline.py`, `formal_worker.py`, `aggregation.py` | driver match/mismatch | capture actual driver before benchmark and exact runtime validation | candidate and environment driver identity | None for policy; actual selected stack is frozen later |
| HD-A-GPU-002 | A-GPU-002 | S47, S50A; D39–40 | Bind PyTorch build, `torch.version.cuda`, actual CUDA runtime/interface; toolkit provenance-only | same plus preflight/environment collector | PyTorch/CUDA match/mismatch; unused toolkit non-authoritative | version fields present, internally consistent, checked before scientific work | exact execution identity for every repetition | None for policy; concrete versions follow pinned environment |
| HD-A-GPU-003 | A-GPU-003 | S47, S50A; D39–40 | Exact cuDNN identity for original set | environment collector, baseline, worker, aggregation | cuDNN match/mismatch | cuDNN query succeeds and is exact-matched | cuDNN identity | None for policy |
| HD-A-GPU-004 | A-GPU-004 | S47, S50A; D39 | Same GPU UUID/model; replacement means new baseline and five runs | preflight, baseline, worker, aggregation | UUID/model match and mismatch; replacement rejection | stable UUID/model capture across validation stages | target UUID/model per repetition | New Human authorization only if replacement is later requested |
| HD-A-GPU-005 | A-GPU-005 | S47; decisions new §41 | Separate independent reproduction under equivalence/preflight/provenance | baseline/reproduction schema and aggregation labels | distinct-set labeling; no canonical substitution | reproduction policy mode cannot satisfy original-set slots | not part of original selection unless separately approved | Future reproduction baseline/config approval |
| HD-A-GPU-006 | A-GPU-006 | S46; D31 | Exactly five initial timings; retain observations/min/max/median | benchmark runner/schema/selection | count=5; order and summaries exact | benchmark tools enforce no missing/extra initial observations | all five values, order, min/max/median | None |
| HD-A-GPU-007 | A-GPU-007 | S46; D31 | Overlap => exactly +5 relevant candidates; all 10; persistent overlap => uncertain and CPU incumbent | benchmark/selection logic | overlap detection, +5 counts, all-10 recompute, CPU tie-break | selection rejects incomplete expansion or superiority claim | relevant set, 10 values, ranges, uncertainty | None |
| HD-A-GPU-008 | A-GPU-008 | S44, S46; D31 | Predefine complete CPU/CUDA configurations; no CPU-optimum assumption | performance schema and benchmark launcher | complete config validation; no mid-candidate mutation | config immutable before native imports and measurements | full config plus hash and order | Approval of later benchmark design/candidate set |
| HD-A-GPU-009 | A-GPU-009 | S46, new S47A | Approved workload success without OOM; allocated/reserved peaks; no percentage threshold | CUDA workload, telemetry, benchmark schema | OOM; telemetry fields; no fallback | memory reset/query semantics validated on target stack | workload identity, completion, peak allocated/reserved | Approval of representative/full workload design if not already specified |
| HD-A-GPU-010 | A-GPU-010 | D40, S50A; new S47A | Mandatory pre-import CUDA policy; value selected by version-specific design/target validation, then frozen | `process_start.py`, launcher, preflight, worker, baseline | missing/mismatch/late `CUBLAS_WORKSPACE_CONFIG`; frozen value | concrete value validated for pinned stack and target GPU before benchmark | value, process-start observation, validation result | Concrete value requires later implementation design/review, not a new normative policy vote |
| HD-A-GPU-011 | A-GPU-011 | spec §3 and new S47A | Existing `model_seed` initializes CUDA RNG as required; no new purpose/save-restore rule | config/model construction/worker | fixed-vector seed preservation; CUDA init uses model seed; no extra purpose | CPU seed vectors unchanged; deterministic repeated CUDA fixture | seed-free preflight; benchmark config records no formal seeds | None |
| HD-A-GPU-012 | A-GPU-012 | S50A, D40; new S47A | Fresh seed-free preflight before registration; separate fresh worker revalidation | `cli.py`, new preflight module, `formal_worker.py` | freshness, forbidden imports, no seed, failed-preflight no registration, sequencing | subprocess boundaries and pre-import checks verified | preflight receipt per candidate/environment | None |
| HD-A-GPU-013 | A-GPU-013 | spec §42/S50A; D39–40 | Post-registration revalidation failure is immutable technical `INVALID` | launcher, worker, baseline registry, aggregation | immutable INVALID; canonical retained; no replacement | crash/revalidation artifacts satisfy integrity and aggregation semantics | reliability failures excluded, not timed/ranked | None |
| HD-A-GPU-014 | A-GPU-014 | S50A; D39–40; execution decision record | baseline-003 first persistent post-change runtime baseline; governance lineage separate | baseline schema/freeze/authorization/provenance | freeze as 003; no fabricated 001/002; no false predecessor | repository state and governance record validated before freeze | selected complete config points to approved evidence | Human approval required only for actual later baseline freeze/promotion workflow |
| HD-A-GPU-015 | A-GPU-015 | S46; D31 | Reliability eligibility; wall-clock-only ranking; scientific metrics forbidden | benchmark, selection record, audit validation | ineligible exclusion; metric-field non-use; selection recomputation | audit proves selector inputs contain timings/eligibility only | timing-only decision inputs and rule | None |

## Conflict-to-decision map

| Conflict | Resolving/constraining decisions | Result |
|---|---|---|
| C-GPU-001 | HD-A-GPU-008, HD-A-GPU-015 | CUDA becomes an allowed complete execution candidate without scientific change or preselection. |
| C-GPU-002 | HD-A-GPU-012, HD-A-GPU-013 | Preflight precedes registration; formal worker and immutable audit semantics follow registration. |
| C-GPU-003 | HD-A-GPU-001..005 | Original canonical identity is exact; independent reproduction is distinct. |
| C-GPU-004 | HD-A-GPU-008..012 | Complete schema gains device, precision, backend, RNG, memory, and process-start policy. |
| C-GPU-005 | HD-A-GPU-001..005, HD-A-GPU-010 | GPU/software/backend provenance and exact-match rules extend the environment fingerprint. |
| C-GPU-006 | HD-A-GPU-012, HD-A-GPU-013 | Post-registration failure is technical `INVALID`, not de-registration. |
| C-GPU-007 | HD-A-GPU-014 | Governance facts are preserved separately; baseline-003 is the first persistent post-change runtime baseline. |
| C-GPU-008 | HD-A-GPU-006, HD-A-GPU-007, HD-A-GPU-015 | Repetition, statistic, overlap, tie, and metric-exclusion policy is complete. |

## Coverage conclusion

All 15 approved Human Decisions and all eight conflict IDs appear in the proposed normative text, implementation impact, and future verification plan. No approved decision disappears. Remaining approvals concern concrete later implementation/benchmark/baseline artifacts, not unresolved normative meaning.

