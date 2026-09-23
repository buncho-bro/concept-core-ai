# Verification coverage

All results in this directory are IMPLEMENT/VERIFY evidence, not Experiment 001 scientific results.

| final_review_v4 requirement | Automated evidence |
| --- | --- |
| 1: fixed five seeds, SHA-256 vectors, common commit/NumPy, no run-level classification | `test_seed_fixed_vectors_and_order`, `test_formal_set_exclusions`, artifact and pipeline tests |
| 2: exact PCG64/API, first and all 1000 vectors, continuous stream, repeated means/CI | `test_bootstrap_all_indices_reference`, `test_full_bootstrap_means_and_ci_reproducible`, `test_saved_evaluation_pipeline` |
| 3: occurrence semantics, exclude same original, multiplicity, percentile, 950/949 | `test_instance_multiplicity_against_explicit_enumeration`, `test_quantile_and_valid_boundary`; saved evaluation pipeline requires no model/checkpoints |
| 4: statuses, multiple flags, priority, secondary warnings | table-driven `test_table_status_precedence`, runner technical/numerical failure tests |
| 5: deltas/medians/4-of-5/equality/attribute boundaries | `test_four_of_five_boundary`, `test_accuracy_equalities`, `test_distance_strict_equalities`, `test_attribute_success`, `test_positive_trend_or_semantics`, recomputation tests |
| 6: dataset/rasterization | `test_distribution_bounds_and_clipping`, independent polygon apothem fixtures, boundary/direction checks, fractional disk round trip |
| 7: stratification/disjoint/union/seed isolation/leakage | `test_metadata_and_independent_split`, image-only dataset test, validation-invariance test, Test-isolation classifier spies |
| 8: exact model/initialization/FP32/Adam/MSE/50 epochs/checkpoints | `test_exact_architecture_and_initialization`, `test_model_seed_isolated`, `test_precision_optimizer_and_loader`, actual two-image Autoencoder 50-epoch fixture |
| 9: six latent states/scalers/probe/distance | six-state export in model fixture, evaluation tests, all 404550 pair counts, category-union oracle, standardized/raw oracle, full saved evaluation pipeline |
| 10: Pixel controls and reanalysis artifacts | 7/12288 feature oracle, shared classifier tests, synthetic evaluation pipeline, saved pair/indices/means/ID/scaler checks, integrity/reanalysis/aggregate-from-artifacts tests |

## Fixture scope

- Actual Autoencoder training fixture: seed 72, two synthetic images, 50 epochs, temporary output. This verifies the production loop without executing any formal master seed training.
- Dataset metadata checks: full 9,000 records and all nine combinations.
- Raster checks: independent geometric oracle at fixed pixels/rotations, boundary fixtures, no-clipping bounds over all metadata records.
- Bootstrap checks: 900 synthetic Test rows, all 404,550 pairs, all 1,000 iterations. No reduced-iteration substitution in the reproducibility checks.
- End-to-end saved evaluation: 9,000 synthetic records/images, six synthetic latent states; full classifiers, pair analysis, bootstrap, PCA and controls. `formal=false`. It contains no formally trained encoder.
- Runner failure injection and aggregate tables use temporary test-only records. Their seed labels are input fixtures, not execution of the formal baseline.
- CPU validation only. No formal training, experiment classification or scientific interpretation is performed.

## Engineering regression checks

- Windows Japanese-path verification logs are explicitly UTF-8, tested with an actual child Python process.
- Verification records the implementation fingerprint before running tests and rejects a changed fingerprint at completion.
- Accuracy deltas use exact correct/total fractions from saved confusion matrices when available. This implements the 0.10 equality boundary without changing it or adding a tolerance.
- Exclusively created output directories and file modes reject silent replacement; artifact hashes detect changes before aggregation or reanalysis.
