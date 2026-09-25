# Experiment 002 implementation report

## A. Implementation status

COMPLETE. The next stage is REVIEW/VERIFY of this implementation. No formal RUN was performed or scheduled.

## B. Source of truth

- Repository: `buncho-bro/concept-core-ai`.
- GitHub main/source commit: `be87d3bbc02c1c19253396a6fa131ed938fb647e` (merged PR #5).
- Normative sources: `experiments/exp002/spec.md` and `experiments/exp002/decisions.md`; Exp001 formal specification is inherited only where not overridden.
- Both `final_candidate_review` and `decisions_candidate_review`: `READY_FOR_IMPLEMENTATION`, `NEW_BLOCKERS: NONE`, `AMBIGUITIES: NONE`, `CONFLICTS: NONE`.
- Work started from a fresh GitHub checkout. Existing unrelated local work was not used as the source or changed.

## C. Files changed

All paths below are under the repository's `concept-core-ai/` directory.

- Added `src/exp002/`: `__init__.py`, `__main__.py`, `config.py`, `data.py`, `performance.py`, `reconstruction.py`, `training.py`, `evaluation.py`, `distance.py`, `artifacts.py`, `visualization.py`, `runner.py`, `aggregation.py`, `cli.py`.
- Added seven test modules: `tests/test_exp002_data.py`, `test_exp002_reconstruction.py`, `test_exp002_evaluation.py`, `test_exp002_distance.py`, `test_exp002_aggregation.py`, `test_exp002_runner.py`, `test_exp002_pipeline.py`.
- Added the `exp002` CLI entry point to `pyproject.toml`.
- Added this report, `EXECUTION.md`, and `verification/{pytest.txt,junit.xml,verification.json}` under `experiments/exp002/implementation_review/`.
- No Exp001 source/experiment files, existing tests, approved Exp002 documents, candidate documents, review history, or dependency versions were changed.

## D. Exp001 code reused

Direct imports preserve the generator, 4×4 supersampling/rasterization, FP32 image-only dataset normalization, autoencoder architecture and initialization, precision controls, Adam construction, checkpoint save/load, Train-only scaler, logistic-regression C selection/convergence/tie behavior, pixel controls, pair layouts/statistics, compressed Seen-pair multiplicities, exact percentile formula/CI validity rule, PCA and artifact/metadata I/O. Exp001 code itself remains unchanged.

## E. Exp002-specific implementation

- `exp002|` purpose seeds and two independent bootstrap sub-seeds.
- Fixed six Seen/three Held-out combinations; exact 4800/600/600/300/2700 split; leakage guards and deterministic representatives.
- Per-image foreground/background FP32 loss, equal image weighting, corresponding model/zero evaluation metrics and Seen-Test sanity inputs.
- Seen-only probe/scaler fitting with separate Seen/Held-out evaluation and derived deltas/gaps.
- Seen-only, descriptive Held-out-only, and primary cross distances; raw/standardized artifacts; deterministic independent bootstrap draw archives and replicate values.
- Exactly nine representatives with both checkpoints, absolute errors, identities, metrics and zero baselines.
- Independent Exp002 runner, seven-step experiment aggregation, artifact integrity and environment/performance eligibility.

## F. Test results

The full suite was run through `python -m exp002 verify`:

| Result | Count |
| --- | ---: |
| Passed | 215 |
| Failed | 0 |
| Skipped | 0 |
| Errors | 0 |

This includes all 106 existing Exp001 tests and 109 new Exp002 tests. Runtime: 157.76 seconds. Fourteen dependency deprecation warnings originated from Matplotlib/pyparsing; no test failed. See `verification/pytest.txt` and `verification/junit.xml`.

The receipt records exit code 0, unchanged implementation during verification, environment versions and source/test/document hashes. An earlier focused run passed 107 Exp002 tests before the two saved-pipeline integration tests were added.

Python compilation/static syntax checking passed for `src` and `tests`. The repository defines no additional lint/static-check configuration. `git diff --check` passed. The final diff was inspected for scope.

## G. Determinism

- SHA-256 derivation was independently compared with hexadecimal first-eight-digit calculations, including all formal seed values as pure arithmetic (no corresponding run artifacts).
- Metadata, selected rasterized images and exact per-combination shuffled memberships repeat with non-formal fixture seed 77.
- Both bootstrap streams match the prescribed PCG64 calls for all 1000 iterations. Reversing analysis execution order and consuming unrelated global RNG values does not change either stream.
- Tiny-fixture training repeats the same history/weights; changing Validation pixels cannot change final training weights.
- Repeated frozen extraction is identical and does not alter weights. Identical synthetic saved Initial/Final latents produce identical distance summaries and all bootstrap replicate arrays.

## H. Leakage

Dataset constructors and saved split validation reject wrong split/combinations, Reserved use and altered shuffled memberships. AE entry points require Seen Train/Validation. Perturbing Seen/Held-out Test inputs and Held-out labels leaves probe scaler statistics, C candidates, selected C and coefficients unchanged. The integration fixture poisons all Reserved image pixels with NaN; the complete pixel/latent evaluation still succeeds without reading Reserved.

## I. Pair counts

Seen-only: 179700 unique unordered pairs, categories 29700/30000/30000/90000. Cross: 180000 pairs, categories 0/60000/60000/60000 (same combination is prohibited). Held-out descriptive: 44850 pairs. Saved pair arrays and category statistics were checked, and primary contrast sign was compared with analytically obvious fixtures.

## J. Bootstrap

The Seen stream uses 600-from-600; the cross stream draws 600 Seen then 300 Held-out per iteration. Original-ID multiplicity compression agrees with literal sampled-instance pairing. Seen same-original-ID pairs are excluded; cross multiplicities are retained. Invalid iterations are attribute/category-specific. Tests cover 949/950 valid replicates, explicit interpolation/endpoints and the exact 2.5/97.5 percentiles. No model, representation or scaler is refitted in bootstrap. The saved integration artifacts contain all index streams, mapping IDs, replicate statistics and validity counts.

## K. Status and aggregation

Runner regressions cover no flags, individual/joint probe/distance failure flags, secondary flags, numerical training failure and technical exceptions at training/export/evaluation. Completed evaluation preserves `VALID`; numerical training failure remains `EXPERIMENTAL_FAILURE`; technical exceptions persist `INVALID` artifacts.

Aggregation tests cover exact formal set, same commit/Python/dependencies/device/thread/worker configuration, all seven precedence steps, missing/non-finite primary evidence, gate boundaries, exact 4/5 and 0.05/0.70 thresholds, strict distance positivity, one successful attribute, positive-direction INCONCLUSIVE, NO_EVIDENCE, and non-blocking CI/control warnings. Artifact corruption is rejected. Probe differences use exact correct/300 fractions for threshold decisions.

## L. Performance choices

The implementation exposes only approved thread/worker settings and retains fixed batch size, optimizer, epochs and mathematics. It reuses an image memmap, chunks pixel feature extraction, caches bootstrap index streams and uses exact multiplicity compression. Inherited probe/PCA BLAS contexts remain single-threaded. Test defaults were used for verification; no wall-clock benchmark or final machine-specific formal configuration was selected.

## M. Permitted implementation details

Package/CLI names, JSON/NPZ/CSV/PNG layout, deterministic original-ID ordering, cached index storage, descriptive Held-out/PCA presentation and separate error maps for both states are implementation choices. Empty foreground/background targets are technical invalid-data errors, with no invented loss fallback. Details and future execution prerequisites are recorded in `EXECUTION.md`.

## N. Unresolved issues / blockers

NONE identified during implementation and automated verification. Human REVIEW/VERIFY of the implementation and frozen pre-RUN performance selection are still separate workflow stages; this report does not claim a formal baseline result or authorize RUN.

## O. Explicit restrictions check

- Formal Experiment 002 runs executed: **0**.
- Scientific conditions changed: **NO**.
- Approved `spec.md` / `decisions.md` changed: **NO**.
- Review history changed: **NO**.
- Experiment 001 scientific behavior/source changed: **NO**; all existing tests pass.
- Formal Experiment 002 result directories created: **0**. The only new experiment directory is `implementation_review`; test artifacts live in temporary synthetic fixture directories.
- Formal results used for tuning: **NO**.
