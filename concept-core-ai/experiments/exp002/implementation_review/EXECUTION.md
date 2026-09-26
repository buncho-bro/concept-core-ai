# Experiment 002 execution and verification

The normative sources are `experiments/exp002/spec.md` and `decisions.md`, promoted by merge commit `be87d3bbc02c1c19253396a6fa131ed938fb647e`. This guide adds no research conditions. The next stage after the implementation PR is REVIEW/VERIFY; this implementation task does not authorize or execute formal RUN.

## Verification

Use Python 3.12 and the existing pinned project dependencies. From the project directory, install the package with its `verify` extra or put `src` on `PYTHONPATH`, then run:

```text
python -m exp002 verify --output <new-verification-directory>
```

This runs the complete Exp001 and Exp002 test suite. It creates a UTF-8 pytest log, JUnit XML, and a receipt containing environment and hashes of both implementations, tests, package files, and normative documents. Tests use temporary synthetic fixtures and non-formal seeds. Formal seed derivation and aggregation are tested as pure calculations/in-memory records, without formal baseline artifacts.

After review, commit the implementation and verify it in the intended runtime environment. The receipt must match the current implementation and environment. A different checkout with different file line endings needs its own verification receipt. Keep subsequent execution/verification outputs outside tracked source paths (the existing `runs/` and `.verify-tmp/` directories are ignored).

## Separate future benchmark, freeze, and RUN stages

After VERIFY, use non-formal wall-clock benchmarks only to select performance settings. Normalize the selected settings without running scientific code:

```text
python -m exp002 prepare-performance --performance <selected-performance.json> --output <normalized-performance.json>
```

Then create the immutable baseline manifest. This operation requires a clean commit, matching successful Exp002 verification, pinned dependencies, and the required runtime environment:

```text
python -m exp002 freeze-baseline --baseline <new-baseline-directory> --baseline-id <id> --baseline-version <version> --verification <receipt.json> --performance <normalized-performance.json> --device cpu
```

For a Human-authorized replacement baseline, also provide `--predecessor <old-baseline-directory> --reason <reason>`. The new baseline records that provenance but does not inherit attempts.

Only after freeze may a formal attempt be registered and run:

```text
python -m exp002 run-one --mode RUN --baseline <baseline-directory> --master-seed <approved-seed> --attempt-id <new-id> --output <new-attempt-directory>
```

The performance JSON accepts `torch_threads`, `torch_interop_threads`, `omp_threads`, `mkl_threads`, `num_workers`, and `persistent_workers`. Counts are validated and the fully resolved settings are recorded. For example, the implementation's conservative **test defaults**, not a selected formal configuration, are:

```json
{"torch_threads": 1, "torch_interop_threads": 1, "omp_threads": 1, "mkl_threads": 1, "num_workers": 0, "persistent_workers": false}
```

Select final machine-specific settings before RUN using non-formal wall-clock benchmarking only. The runner reads them only from the frozen manifest; it has no per-run performance override. Launch a fresh process with the corresponding `OMP_NUM_THREADS` and `MKL_NUM_THREADS` environment variables set before Python starts. The runner applies and records the frozen values. No batch-size, epoch, optimizer, architecture, loss, or mathematical analysis controls are exposed as performance options.

The runner first creates an exclusive canonical registration for that seed, then begins scientific execution. Technical/interrupted failures remain `INVALID`; numerical training failures use `EXPERIMENTAL_FAILURE`; neither can be replaced in the baseline. A diagnostic retry uses a separate identity and output:

```text
python -m exp002 run-one --mode RUN --baseline <baseline-directory> --master-seed <seed> --attempt-id <retry-id> --retry-of <canonical-id> --retry-reason <reason> --output <new-retry-directory>
```

## Artifacts and reanalysis

- `configuration.json`: complete scientific configuration, formal marker, run ID, seeds including bootstrap sub-seeds, source commit, execution commit, implementation fingerprint, environment, device and performance settings.
- `metadata.csv`, `split.npz`, `images.npy`: all 9000 generated images/IDs and exhaustive split membership. Only four active splits enter learning/evaluation; Reserved is never encoded or analyzed.
- `initial.pt`, `final.pt`, `training.csv`: inherited checkpoint schema and 50-epoch balanced-loss monitoring.
- `latent/{initial,final}_{train,validation,seen_test,heldout_test}.npz`: eight frozen latent artifacts, each with ordered sample IDs.
- `reconstruction_metrics.json`: initial/final/zero metrics on both Test subsets plus Seen-Test sanity ratio inputs. The five-run gate is evaluated only during aggregation.
- `representatives.npz`, `representative_metrics.json`, `representatives.png`: exactly one minimum Test sample ID for each of the nine combinations, both reconstruction states, both absolute-error maps, per-image metrics, identities and zero baseline.
- `evaluation/probe_*.json`, `pixel_*.json`: scaler statistics, candidate convergence and validation scores, selected C, coefficients/classes, separate Seen/Held-out metrics and predictions.
- `evaluation/bootstrap_indices.npz`: independent Seen-only and cross index streams, with original sample-ID mapping. Both encoder states and both distance scales reuse these fixed draws.
- `evaluation/pairs_*.npz`, `bootstrap_*.npz`, `distance_*.json`: original-pair indices, category codes, raw/standardized distances, bootstrap replicate values, validity counts, CIs and contrasts. Held-out-only statistics are descriptive with no required bootstrap.
- `evaluation/pca_*`: separate descriptive PCA artifacts for Seen and Held-out Test, with sample IDs and labels; PCA is never used by primary metrics.
- `status.json`, `failure.json` when applicable, `report.json`, `integrity.json`: execution observations, errors, evaluation flags, and SHA-256 inventory. Failed attempts are retained.

The Exp001 four-category integer distance code is reused: 0 = same color/same shape, 1 = same color/different shape, 2 = different color/same shape, 3 = different color/different shape. Cross pairs never contain code 0. Indices within each split refer to ascending sample IDs.

```text
python -m exp002 reanalyze <attempt-directory> --output <new-evaluation-directory>
python -m exp002 aggregate --baseline <baseline-directory> --output <new-aggregate-directory>
```

Reanalysis checks integrity and requires the original environment and implementation. It evaluates saved latents/images without re-encoding or refitting the AE. Formal aggregation accepts no attempt paths: it resolves exactly one canonical registration for each formal seed from the baseline, checks frozen provenance and artifact integrity, reports the exact canonical IDs plus retries, and then applies spec §40 in order. It recomputes held-out accuracy from confusion matrices and cross contrasts from recorded category means.

## Implementation choices within the approved freedom

- Retain Exp001 color-major/shape-major generation and one continuous split PCG64 stream. Shuffle each combination in sample-ID order, then apply the Exp002 positions.
- Reuse Exp001 rasterization, image normalization, model, initialization, precision setup, optimizer construction, checkpoint I/O, scaler, classifier selection, pixel features, pair/statistical utilities, percentile interpolation, PCA and artifact I/O without changing Exp001 source files.
- Compute foreground/background loss in FP32 per image. Aggregate evaluation per-image values in fixed order using float64 accumulation. Empty foreground/background targets are rejected as invalid data; no fallback mathematics is introduced.
- Cache bootstrap index arrays once and compress instance multiplicities as original-ID counts. The resulting pair multiplicities are checked against literal instance-pair enumeration. No bootstrap model/scaler refit occurs.
- Compare probe threshold boundaries using exact fractions of correct/total counts when available, with no tolerance. Other approved strict/non-strict comparisons remain unchanged.
- Keep Exp002 orchestration and aggregation separate from Exp001. No performance benchmark or final formal performance selection was performed during IMPLEMENT.
