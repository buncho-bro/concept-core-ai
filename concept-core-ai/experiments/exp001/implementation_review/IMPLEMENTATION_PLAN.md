# Experiment 001 implementation plan

MODE: IMPLEMENT + VERIFY only. No formal baseline execution or scientific interpretation.

## Canonical sources

Read directly from GitHub at commit `207bee36f2a5b1b57de2d73d582ef9f890dbe855`, under `concept-core-ai/`:
1. `experiments/exp001/spec.md`
2. APPROVED decisions in `experiments/exp001/decisions.md`
3. `experiments/exp001/review/final_review_v4/VERIFICATION_PLAN.md`

READINESS is READY_FOR_IMPLEMENTATION. IMPLEMENTATION_DETAILS permits the engineering choices below. GitHub contains documentation only, with no existing code, dependencies or test infrastructure. Existing local document relocation is outside this change.

## Modules and sequence

- `src/exp001/config.py`: immutable baseline configuration and SHA-256 purpose seeds; record dependency versions.
- `data.py`: deterministic metadata generation, explicit 16-subpixel geometry rasterizer, fractional RGB float32 storage; independent stratified split and image-only training dataset.
- `model.py`, `training.py`: specified FP32 autoencoder/initialization and Adam/MSE training; pre-update initial checkpoint and final checkpoint after exactly 50 epochs; validation monitoring only; image-only loss path.
- `evaluation.py`: frozen checkpoint latent extraction for all six states; Train-only scaler; one shared multinomial probe/control implementation; no Test access during selection; seven image-statistic and 12288 raw-pixel features.
- `distance.py`: all unordered Test pairs, category unions, standardized and raw distances, sample-instance bootstrap with prescribed PCG64 stream and percentile formula.
- `visualization.py`: reproducible Test PCA coordinates for both attribute displays, 2D/3D plots; fixed reconstruction examples.
- `artifacts.py`, `runner.py`: exclusively created run directories; configuration, seed, commit, environment and source hashes; metadata, images, checkpoints, logs, latent, fitted scalers/classifiers, distance rows, bootstrap indices/means, plots and reports. Preserve failures and interrupted runs.
- `aggregation.py`: explicit five-run input set, common commit/NumPy checks, metric recomputation and specified precedence; keep secondary failures as warnings.
- `cli.py`: separate verify, run-one, reanalyze and aggregate commands; verification never invokes formal runs. Formal execution requires clean committed implementation and successful verification.
- `tests/`: independent fixtures and table-driven checks covering every final_review_v4 requirement, including full bootstrap index streams, pair counts, convergence/selection isolation, checkpoint timing, artifacts, status precedence and equality boundaries.

## Engineering conventions

- SHA-256 first 32 bits are read in digest order (big-endian, equivalent to first eight hexadecimal digits).
- Generation/split use separate explicitly constructed NumPy PCG64 generators, fixed color/shape order, increasing integer sample IDs. Saved split rows are sorted by sample ID.
- Geometry and analysis reductions use float64; unnormalized fractional RGB is exactly representable in float32 as integer multiples of 1/16. Model inputs/parameters/activations/loss remain float32.
- Bootstrap multiplicity is computed with sample occurrence counts: each distinct original pair gets weight count_i * count_j. Tests compare this with explicit instance enumeration.
- NumPy and other numerical dependencies are pinned. Artifacts contain actual runtime versions.
- Reduced fixtures are marked verification-only and excluded from formal aggregation. No research conditions are added or changed.

## Verification and delivery

Run automated checks and a short temporary image-only model fixture; do not run formal seeds through training. Save verification output, coverage mapping, changed files, limitations and blockers in this directory. Report IMPLEMENTATION_COMPLETE only if all required checks pass and no research blocker remains.
