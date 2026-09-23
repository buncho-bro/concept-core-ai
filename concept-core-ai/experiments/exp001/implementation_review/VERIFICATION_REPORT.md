# Experiment 001 — Implementation verification report

Date: 2026-09-23 (Asia/Tokyo)

## IMPLEMENTATION STATUS

**IMPLEMENTATION_COMPLETE**

IMPLEMENT + VERIFY completed. Implementation readiness: **READY_FOR_RUN** for the approved procedure, subject to committing the reviewed implementation before a later MODE: RUN.

The canonical source was read directly from GitHub, not from the existing local research documents:

- Repository: `buncho-bro/concept-core-ai`, directory `concept-core-ai/`.
- Commit: `207bee36f2a5b1b57de2d73d582ef9f890dbe855` (main was rechecked and remained at this commit).
- Priority: `spec.md`, APPROVED `decisions.md`, final_review_v4 `VERIFICATION_PLAN.md`.
- final_review_v4 readiness: `READY_FOR_IMPLEMENTATION`.
- Source URLs and Git blob IDs: `CANONICAL_SOURCES.json`.

The implementation includes dataset generation/rasterization/splitting, the exact autoencoder and initialization, FP32 training and checkpoint semantics, six latent states, exploratory 2D/3D PCA, linear probes, all-pair standardized/raw distances, the prescribed bootstrap, both Pixel controls, artifact integrity/failure preservation, reanalysis and experiment aggregation. CLI operations are separated.

## TESTS RUN

Final command:

```powershell
.\.venv\Scripts\python.exe -m exp001 verify --output experiments/exp001/implementation_review/verification_20260923_complete
```

Additional checks: dependency consistency (`pip check`) and CLI command discovery.

Final evidence:

- `verification_20260923_complete/pytest.txt`
- `verification_20260923_complete/junit.xml`
- `verification_20260923_complete/verification.json`
- `VERIFICATION_MATRIX.md`: mapping to all ten final_review_v4 verification requirements.

Verification exercised full 9,000-record metadata/split conditions, 404,550 Test pairs, all 1,000 bootstrap iterations, and a full saved-evaluation pipeline on synthetic fixtures. The actual Autoencoder training test used two synthetic images, model seed 72 and 50 epochs. It checked update-before/after checkpoint state and all six latent exports without a formal baseline run.

## TESTS PASSED

**99 passed**, final pytest duration **67.50 seconds**, CLI exit code **0**.

- Fixed SHA-256 vectors, independent purpose seeds and deterministic ordering.
- Dataset bounds, nine strata, independent split stream, disjoint complete splits, geometric/boundary fixtures and fractional RGB round trip.
- Exact architecture, 1,646,307 parameters, initialization, biases, FP32 settings, Adam/MSE, loader behavior and checkpoint timing.
- Validation monitoring does not alter parameter updates; image-only Autoencoder data path; frozen latent extraction.
- Train-only ddof=0 scaling, exclusion threshold, validation-only C selection, smallest-C ties, nonconvergence flags and Test isolation.
- All pair counts, category unions, raw and standardized distances, exact bootstrap index stream, instance multiplicities, repeated means/CI, linear quantiles and 950/949 boundaries.
- Shared Pixel classifier path, 7/12288 features, PCA/reconstruction artifacts, sample-ID mapping and saved-evaluation integration.
- Failure status preservation, multiple flags, aggregation precedence, common commit/NumPy, all success boundaries, same-attribute requirement and nonprimary warnings.
- Recalculation from artifacts, integrity checks, overwrite rejection, verification/reanalysis guards and Japanese-path UTF-8 logs.

Dependency consistency check: **passed**.

## TESTS FAILED

**0 in final verification.**

Resolved implementation/verification issues during development:

1. An earlier full test run passed 98 tests, but its CLI log display failed because Windows emitted a Japanese path in its local encoding. The subprocess log encoding is now explicitly UTF-8, with an actual-child-process regression test.
2. The first isolated encoding regression test intercepted a Windows platform-query subprocess as well as its intended child. The test's environment probe was isolated; the regression test and final full suite passed afterward.

Earlier verification artifacts remain in `verification_20260923/` and `verification_20260923_final/`; the authoritative final verification is `verification_20260923_complete/`. The first directory's raw pytest log uses the original Windows encoding. Its test-only receipt is not evidence that the earlier CLI completed successfully.

## SPEC DEVIATIONS

**None identified.** Research specifications, APPROVED decisions and scientific interpretation were not changed.

Engineering choices are documented in `IMPLEMENTATION_PLAN.md`: explicit NumPy generation/split streams, fixed sample ordering, float32 fractional RGB storage, float64 geometry/analysis, occurrence-count bootstrap implementation, file layout and dependency pins. Exact correct/total arithmetic preserves the specified probe delta equality boundary without adding a tolerance.

## KNOWN LIMITATIONS

- Verified on Windows 11, Python 3.12.14, CPU. CUDA execution and cross-hardware bitwise identity were not tested.
- NumPy 2.3.5, PyTorch 2.7.1, SciPy 1.15.3, scikit-learn 1.6.1, Matplotlib 3.10.3, threadpoolctl 3.6.0, pytest 8.4.1. Full installed dependency versions are pinned in `requirements-lock.txt`.
- 14 Matplotlib/Pyparsing deprecation warnings occurred; no test failure or convergence warning was hidden.
- Full-size 50-epoch formal training runtime, memory demand and scientific outcomes have not been measured. Formal training is intentionally reserved for MODE: RUN.
- The working tree already contained a relocation of tracked documents before this task. That state was preserved. New implementation files are local and uncommitted; no GitHub push was performed.
- `run-one` requires a clean committed implementation and a successful verification receipt matching the implementation and runtime. Resolve/review the existing local placement and commit the intended files before formal execution. This is a provenance prerequisite, not an unresolved research condition.

## BLOCKERS

**No unresolved implementation or research-condition blockers.**

## FORMAL EXPERIMENT EXECUTION

**Formal baseline runs executed: 0.**

No formal master seed was trained through the baseline. Temporary status/aggregation fixtures may contain formal seed numbers as test inputs, but they are not scientific runs. No official SUCCESS / INCONCLUSIVE / NO_EVIDENCE conclusion was produced, and no experimental result was scientifically interpreted. There is no project-level `runs/` or `aggregate/` output from this task.

## FILES CHANGED

New implementation and project files:

- `.gitignore`, `README.md`, `pyproject.toml`, `requirements-lock.txt`
- `src/exp001/__init__.py`, `src/exp001/__main__.py`
- `src/exp001/config.py`, `src/exp001/data.py`, `src/exp001/model.py`
- `src/exp001/training.py`, `src/exp001/evaluation.py`, `src/exp001/distance.py`
- `src/exp001/visualization.py`, `src/exp001/artifacts.py`, `src/exp001/runner.py`
- `src/exp001/aggregation.py`, `src/exp001/cli.py`
- `tests/conftest.py`, `tests/test_data.py`, `tests/test_model_training.py`
- `tests/test_evaluation.py`, `tests/test_distance.py`, `tests/test_aggregation.py`
- `tests/test_artifacts.py`, `tests/test_pipeline.py`

New review evidence under `experiments/exp001/implementation_review/`:

- `IMPLEMENTATION_PLAN.md`, `CANONICAL_SOURCES.json`, `VERIFICATION_MATRIX.md`, `VERIFICATION_REPORT.md`
- `verification_20260923/`, `verification_20260923_final/`, `verification_20260923_complete/`: pytest logs, JUnit XML and verification receipts.

The local `.venv/` and test caches are ignored. Existing research documents were not edited.
