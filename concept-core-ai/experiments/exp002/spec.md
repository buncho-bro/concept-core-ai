# Experiment 002 Specification

## 0. Status

This document is the approved formal specification for Experiment 002.

Experiment 002 inherits Experiment 001 unless explicitly overridden here.

This document defines the scientific, evaluation, reproducibility, and formal-run differences from Experiment 001.

Experiment 001 remains unchanged.

Formal Experiment 002 execution may begin only after implementation against this specification and verification are complete.

---

# 1. Objective

Experiment 002 tests whether a self-supervised autoencoder can form reusable latent structure corresponding to known attributes when:

1. trivial near-zero reconstruction is discouraged,
2. some color×shape combinations are never observed during representation learning,
3. evaluation explicitly tests unseen attribute combinations,
4. learning-induced changes are distinguished from information already readable from random features.

The main question is:

> Does training create reusable attribute-related latent structure that transfers to unseen color×shape combinations?

Experiment 002 does not directly prove the existence of a concept core.

---

# 2. Relationship to Experiment 001

Unless overridden by this document, Experiment 002 inherits from Experiment 001:

- five formal master seeds,
- purpose-based derived seed structure,
- autoencoder architecture,
- latent dimension = 32,
- initialization rules,
- float32 execution,
- AMP/FP16/BF16/TF32 disabled,
- Adam optimizer configuration,
- fixed 50 epochs,
- batch size = 128,
- no scheduler,
- no early stopping,
- no gradient clipping,
- initial and final checkpoints,
- logistic-regression probe family,
- C grid,
- convergence policy,
- class label order,
- standardization threshold,
- run execution-status semantics,
- evaluation-flag semantics,
- same-commit formal-set requirement,
- same-environment formal-set requirement,
- artifact integrity requirements,
- no post-hoc threshold modification.

Any implementation change not explicitly authorized here is prohibited for the formal Experiment 002 baseline.

Where an Experiment 001 rule assumes a 900-sample Test set or another Experiment 001-specific dataset structure that conflicts with an explicit Experiment 002 rule, the Experiment 002 rule takes precedence.

---

# 3. Formal Master Seeds

Formal master seeds remain:

```text
1001
1002
1003
1004
1005
```

Purpose names remain:

```text
generation
split
model
loader
probe
analysis
```

Derived seed rule:

```text
first 32 unsigned bits of SHA-256(
    "exp002|" + master_seed + "|" + purpose
)
```

Experiment number is part of the deterministic seed namespace.

Experiment 002 intentionally uses:

```text
exp002|
```

rather than:

```text
exp001|
```

so that Experiment 002 stochastic streams are deterministic but distinct from Experiment 001.

---

# 4. Dataset Domain

Image format remains:

```text
64 × 64 RGB
black background
```

Color classes remain:

```text
red   = [230, 25, 25]
green = [25, 230, 25]
blue  = [25, 25, 230]
```

Shape classes remain:

```text
circle
triangle
square
```

Unless explicitly overridden here, the following remain identical to Experiment 001:

- center distribution,
- size/circumradius distribution,
- channel noise,
- rotation rules,
- polygon construction,
- 4×4 supersampling,
- boundary semantics,
- clipping rules,
- image storage semantics.

All model inputs and all reconstruction-loss / reconstruction-metric calculations use RGB values normalized to:

```text
[0, 1]
```

---

# 5. Combination Hold-out

The 9 color×shape combinations are divided into 6 seen combinations and 3 held-out combinations.

## 5.1 Seen combinations

```text
red circle
red triangle

green triangle
green square

blue square
blue circle
```

## 5.2 Held-out combinations

```text
red square
green circle
blue triangle
```

Each color appears in exactly two seen combinations.

Each shape appears in exactly two seen combinations.

Each held-out sample therefore contains:

- a color already observed during training,
- a shape already observed during training,
- but a color×shape combination never observed during training.

This design tests recombination/generalization rather than unseen-class recognition.

---

# 6. Sample Count

Each of the 9 combinations contains:

```text
1000 generated samples
```

Total:

```text
9000 samples
```

Each sample receives a unique deterministic sample ID.

---

# 7. Deterministic Split Assignment

For every color×shape combination:

1. generate all 1000 samples,
2. preserve unique sample IDs,
3. deterministically shuffle the 1000 sample IDs using the derived `split_seed`,
4. assign split membership from the shuffled order.

The same deterministic per-combination procedure is used for both seen and held-out combinations.

---

# 8. Seen Split Structure

For each seen combination, after deterministic shuffle:

```text
positions   0–799   -> Train
positions 800–899   -> Validation
positions 900–999   -> Seen Test
```

Per seen combination:

```text
800 Train
100 Validation
100 Seen Test
```

Totals:

```text
Train      = 4800
Validation = 600
Seen Test  = 600
```

---

# 9. Held-out Split Structure

For each held-out combination, after deterministic shuffle:

```text
positions   0–99  -> Held-out Test
positions 100–999 -> Reserved
```

Per held-out combination:

```text
0 Train
0 Validation
100 Held-out Test
900 Reserved
```

Totals:

```text
Held-out Test = 300
Reserved      = 2700
```

---

# 10. Reserved Samples

Reserved samples are generated and assigned deterministic IDs but are excluded from all formal Experiment 002 analysis.

Reserved samples MUST NOT be used for:

- autoencoder training,
- autoencoder validation,
- probe training,
- probe validation,
- scaler fitting,
- C selection,
- threshold selection,
- reconstruction sanity classification,
- distance analysis,
- bootstrap analysis,
- experiment-level classification.

Reserved samples may only be used by a future separately preregistered experiment or exploratory analysis explicitly marked as non-formal.

---

# 11. Autoencoder Training Data

Autoencoder optimization uses only:

```text
Seen Train
```

Validation monitoring uses only:

```text
Seen Validation
```

Held-out Test and Reserved samples are never supplied to the autoencoder optimization process.

---

# 12. Reconstruction Loss

Experiment 001 global pixel MSE is replaced by foreground/background balanced MSE.

## 12.1 Foreground definition

For target pixel `p`:

```text
foreground if R + G + B > 0
background otherwise
```

using the normalized target image.

The foreground mask is derived from the reconstruction target.

The mask is used only for loss/evaluation calculations.

It is not passed as model input.

## 12.2 Per-image region MSE

For each image `i`:

```text
foreground_MSE_i
=
mean squared error over all foreground RGB elements
of image i
```

```text
background_MSE_i
=
mean squared error over all background RGB elements
of image i
```

RGB channels are included as separate squared-error elements in these means.

Each image is therefore assigned its own foreground and background region mean before aggregation across images.

## 12.3 Per-image balanced loss

For each image `i`:

```text
balanced_reconstruction_loss_i
=
0.5 * foreground_MSE_i
+
0.5 * background_MSE_i
```

## 12.4 Mini-batch training loss

For a mini-batch containing `B` images:

```text
batch_balanced_reconstruction_loss
=
(1 / B)
*
sum_i balanced_reconstruction_loss_i
```

Equivalently:

```text
batch_foreground_MSE
=
mean_i(foreground_MSE_i)

batch_background_MSE
=
mean_i(background_MSE_i)

batch_balanced_reconstruction_loss
=
0.5 * batch_foreground_MSE
+
0.5 * batch_background_MSE
```

Images are weighted equally regardless of foreground area.

Pooling all foreground pixels from multiple images into a single region mean before loss computation is prohibited.

Pooling all background pixels from multiple images into a single region mean before loss computation is prohibited.

No adaptive weighting is permitted during formal runs.

---

# 13. Reconstruction Evaluation Aggregation

Evaluation follows the same per-image-first semantics as training.

For an evaluation set containing `N` images:

```text
dataset_foreground_MSE
=
(1 / N)
*
sum_i foreground_MSE_i
```

```text
dataset_background_MSE
=
(1 / N)
*
sum_i background_MSE_i
```

```text
dataset_balanced_reconstruction_loss
=
(1 / N)
*
sum_i balanced_reconstruction_loss_i
```

and therefore:

```text
dataset_balanced_reconstruction_loss
=
0.5 * dataset_foreground_MSE
+
0.5 * dataset_background_MSE
```

Dataset-level `global_MSE` is also recorded.

For Initial and Final model states, record:

```text
global_MSE
foreground_MSE
background_MSE
balanced_reconstruction_loss
```

separately for:

```text
Seen Test
Held-out Test
```

Held-out reconstruction metrics are secondary generalization evidence.

---

# 14. Zero-output Reconstruction Baseline

For each evaluated image define the zero-output predictor:

```text
predicted RGB = 0 for every pixel
```

Zero-output metrics MUST use the same per-image-first aggregation semantics as model reconstruction metrics.

For each image `i`, compute:

```text
zero_global_MSE_i
zero_foreground_MSE_i
zero_background_MSE_i
zero_balanced_reconstruction_loss_i
```

Then average image-level metrics across the evaluation set.

Record dataset-level:

```text
zero_global_MSE
zero_foreground_MSE
zero_background_MSE
zero_balanced_reconstruction_loss
```

for:

```text
Seen Test
Held-out Test
```

No model is trained for this baseline.

---

# 15. Reconstruction Sanity Gate

The formal reconstruction sanity gate is evaluated using:

```text
Seen Test only
```

For each formal seed define:

```text
balanced_ratio
=
final_dataset_balanced_reconstruction_loss
/
zero_dataset_balanced_reconstruction_loss
```

```text
foreground_ratio
=
final_dataset_foreground_MSE
/
zero_dataset_foreground_MSE
```

The gate passes only if all conditions hold:

```text
1. balanced_ratio < 1.0
   in at least 4/5 seeds

2. foreground_ratio < 1.0
   in at least 4/5 seeds

3. median(balanced_ratio) <= 0.80

4. median(foreground_ratio) <= 0.80
```

The numerator and denominator MUST both use the same per-image-first aggregation semantics.

Failure of this gate does not make an otherwise technically valid run INVALID.

It affects Experiment-level classification as defined below.

---

# 16. Probe Representations

For each of:

```text
simple pixel statistics
raw pixels
initial encoder latent
final encoder latent
```

train separate classifiers for:

```text
color
shape
```

The probe model family remains identical to Experiment 001.

---

# 17. Probe Train / Validation / Test

Probe Train:

```text
Seen Train only
```

Probe Validation:

```text
Seen Validation only
```

C selection uses Seen Validation only.

The selected classifier is then evaluated separately on:

```text
Seen Test
Held-out Test
```

Held-out labels MUST NOT influence:

- fitting,
- scaler estimation,
- convergence selection,
- C selection,
- threshold selection.

---

# 18. Probe Standardization

For initial and final latent states separately:

```text
fit mean/std on Seen Train only
ddof = 0
exclude dimensions with std < 1e-8
```

Apply the resulting scaler unchanged to:

```text
Seen Validation
Seen Test
Held-out Test
```

The same Seen-only fitting principle applies to simple pixel and raw pixel baselines.

Held-out Test MUST NOT be used to fit any scaler.

---

# 19. Probe Metrics

For color and shape, record:

```text
Seen Test:
- accuracy
- balanced accuracy
- confusion matrix

Held-out Test:
- accuracy
- balanced accuracy
- confusion matrix

selected_C
convergence status
```

Chance level:

```text
1 / 3
```

---

# 20. Probe Derived Metrics

For attribute:

```text
A ∈ {color, shape}
```

define:

```text
seen_probe_delta_A
=
final_seen_accuracy_A
-
initial_seen_accuracy_A
```

Primary generalization delta:

```text
heldout_probe_delta_A
=
final_heldout_accuracy_A
-
initial_heldout_accuracy_A
```

Also record:

```text
initial_generalization_gap_A
=
initial_seen_accuracy_A
-
initial_heldout_accuracy_A
```

```text
final_generalization_gap_A
=
final_seen_accuracy_A
-
final_heldout_accuracy_A
```

Generalization gap is secondary and does not directly determine SUCCESS.

---

# 21. Pixel Baselines

Experiment 001 pixel controls are retained:

```text
simple image statistics
raw pixel linear classifier
```

Training and validation use seen data only.

Evaluate separately on:

```text
Seen Test
Held-out Test
```

Held-out data MUST NOT influence fitting or C selection.

Pixel baselines are control measurements only and do not directly determine Experiment-level SUCCESS.

---

# 22. Distance Standardization

Initial and Final latent distance analyses use separate scalers.

Each scaler is fitted only on:

```text
Seen Train latent
```

using:

```text
mean
std ddof=0
exclude dimensions with std < 1e-8
```

Apply the same scaler unchanged to:

```text
Seen Test
Held-out Test
```

Held-out data MUST NOT influence standardization.

---

# 23. Seen-only Distance Analysis

Seen Test contains:

```text
600 samples
```

Use all unique unordered pairs.

Total:

```text
C(600,2) = 179,700
```

Expected categories:

```text
same_color_same_shape           = 29,700
same_color_different_shape      = 30,000
different_color_same_shape      = 30,000
different_color_different_shape = 90,000
```

For each category record:

```text
count
mean
median
std ddof=0
95% bootstrap CI of mean
```

Seen-only distance is secondary and supports comparison with Experiment 001.

Its bootstrap procedure is explicitly defined below and replaces incompatible Experiment 001 900-Test-sample bootstrap assumptions.

---

# 24. Held-out-only Distance Analysis

Held-out Test contains:

```text
300 samples
```

Held-out-only pair geometry cannot independently separate color and shape effects because every held-out combination has a unique color-shape pairing.

Held-out-only distance is:

```text
secondary / descriptive only
```

Record deterministic descriptive statistics as appropriate.

Held-out-only distance:

```text
does NOT require a bootstrap CI
```

and does not directly contribute to Experiment-level SUCCESS.

---

# 25. Seen ↔ Held-out Cross-distance

This is the primary geometry generalization analysis.

Cross all:

```text
600 Seen Test samples
×
300 Held-out Test samples
```

Total:

```text
180,000 cross pairs
```

Expected categories:

```text
same_color / different_shape      = 60,000
different_color / same_shape      = 60,000
different_color / different_shape = 60,000
```

No same_color_same_shape cross category exists.

---

# 26. Cross-distance Contrast

For attribute:

```text
A ∈ {color, shape}
```

define:

```text
cross_contrast_A
=
mean(distance for different_A cross-pairs)
-
mean(distance for same_A cross-pairs)
```

Compute separately for:

```text
Initial
Final
```

Primary distance delta:

```text
cross_distance_delta_A
=
final_cross_contrast_A
-
initial_cross_contrast_A
```

Positive cross contrast means held-out samples are, on average, closer to seen samples sharing attribute A than to seen samples differing in A.

---

# 27. Raw Distance

Raw Euclidean distance is retained as secondary analysis.

Primary distance success uses only:

```text
Seen-Train-standardized Euclidean distance
```

Raw distance does not affect formal classification.

---

# 28. Distance Bootstrap Seed Derivation

Seen-only and Seen↔Held-out cross-distance bootstrap analyses MUST use independent deterministic RNG streams.

Both streams are derived from the run's already-derived `analysis_seed`.

Define:

```text
seen_bootstrap_seed
=
first 32 unsigned bits of SHA-256(
    "exp002|" + analysis_seed + "|seen_distance_bootstrap"
)
```

Define:

```text
cross_bootstrap_seed
=
first 32 unsigned bits of SHA-256(
    "exp002|" + analysis_seed + "|cross_distance_bootstrap"
)
```

`analysis_seed` in these strings is its canonical unsigned decimal integer representation with no whitespace, sign prefix, separators, or leading zero padding.

These bootstrap sub-seeds are analysis substreams.

They do not replace the formal `analysis_seed` derivation defined in §3.

The two bootstrap RNG streams MUST NOT share Generator state.

---

# 29. Bootstrap RNG API

For Seen-only bootstrap:

```python
rng_seen = numpy.random.Generator(
    numpy.random.PCG64(seen_bootstrap_seed)
)
```

For cross-distance bootstrap:

```python
rng_cross = numpy.random.Generator(
    numpy.random.PCG64(cross_bootstrap_seed)
)
```

Each Generator is initialized exactly once before its own iteration 0 and used continuously through iteration 999.

No reseeding or Generator recreation is permitted within a bootstrap analysis.

The Seen-only bootstrap MUST NOT consume values from `rng_cross`.

The cross-distance bootstrap MUST NOT consume values from `rng_seen`.

Adding, removing, or changing execution order of one bootstrap analysis therefore MUST NOT alter the random index stream of the other.

---

# 30. Seen-only Distance Bootstrap

Bootstrap iterations:

```text
1000
```

Population:

```text
Seen Test = 600 original samples
```

For each iteration, draw:

```python
indices = rng_seen.integers(
    low=0,
    high=600,
    size=600,
    endpoint=False,
    dtype=numpy.int64,
)
```

Each resampled occurrence is a distinct bootstrap instance.

Construct all unique unordered bootstrap-instance pairs.

If two bootstrap instances correspond to the same original sample ID, their pair is excluded.

Pairs corresponding to different original sample IDs are included with the multiplicity induced by resampling.

Pair rows themselves MUST NOT be directly resampled.

Fixed Test latents and the approved Seen Train scaler are reused.

No re-encoding, model re-fitting, or scaler re-fitting occurs inside bootstrap iterations.

For each required Seen-only distance category, compute the bootstrap category mean when that category contains at least one valid pair.

An iteration is valid for a category only when that category contains at least one valid pair.

Missing-category iterations are omitted for that category only.

If valid iterations for a required Seen-only category CI are:

```text
< 950
```

add:

```text
BOOTSTRAP_CI_FAILED
```

Seen-only bootstrap CI remains secondary evidence and does not directly determine SUCCESS.

---

# 31. Cross-distance Bootstrap Sampling

Bootstrap iterations:

```text
1000
```

Population:

```text
Seen Test     = 600 original samples
Held-out Test = 300 original samples
```

For each iteration, in exactly this order:

```text
1. draw 600 Seen Test indices with replacement
2. draw 300 Held-out Test indices with replacement
3. rebuild all Seen-instance × Held-out-instance cross pairs
4. compute color statistics
5. compute shape statistics
6. proceed to the next iteration using the same rng_cross instance
```

Seen draw:

```python
seen_indices = rng_cross.integers(
    low=0,
    high=600,
    size=600,
    endpoint=False,
    dtype=numpy.int64,
)
```

Held-out draw:

```python
heldout_indices = rng_cross.integers(
    low=0,
    high=300,
    size=300,
    endpoint=False,
    dtype=numpy.int64,
)
```

The Seen draw MUST occur before the Held-out draw in every iteration.

---

# 32. Cross-bootstrap Instance Semantics

Each resampled occurrence is a distinct bootstrap instance.

Repeated occurrences of the same original sample preserve multiplicity.

All Seen-instance × Held-out-instance cross pairs are reconstructed from the resampled instances.

Pair rows MUST NOT be bootstrapped directly.

No model re-fitting, latent re-encoding, or scaler re-fitting occurs inside bootstrap iterations.

---

# 33. Cross-bootstrap Valid Iteration

For attribute `A`, an iteration is valid for the cross-contrast CI only if both required categories contain at least one cross pair:

```text
same_A count > 0
different_A count > 0
```

For every valid iteration compute:

```text
same_A_mean
different_A_mean

contrast_A
=
different_A_mean
-
same_A_mean
```

Invalid iterations for one attribute are omitted only from that attribute's bootstrap statistic.

If valid iterations for a required cross-contrast CI are:

```text
< 950
```

add:

```text
BOOTSTRAP_CI_FAILED
```

---

# 34. Bootstrap CI Quantile Rule

All required bootstrap CIs use:

```text
95% percentile CI
```

with the same explicit linear interpolation rule:

```text
sort valid bootstrap values as y[0..n-1]

h = (n - 1) * q
i = floor(h)
f = h - i

if i < n - 1:
    Q(q) = (1-f) * y[i] + f * y[i+1]

if i = n - 1:
    Q(q) = y[n-1]
```

Use:

```text
lower = Q(0.025)
upper = Q(0.975)
```

Primary cross-distance CI targets include:

```text
cross_contrast_color
cross_contrast_shape
```

Category means may additionally be reported.

`BOOTSTRAP_CI_FAILED` alone does not prevent SUCCESS / INCONCLUSIVE / NO_EVIDENCE classification.

---

# 35. Reconstruction Representative Artifacts

Save exactly 9 preregistered representative samples.

Seen:

```text
red circle
red triangle
green triangle
green square
blue square
blue circle
```

Held-out:

```text
red square
green circle
blue triangle
```

For each combination select:

```text
minimum sample_id
within the relevant Test subset
```

No random or post-hoc representative selection is permitted.

---

# 36. Reconstruction Artifact Contents

For each representative save:

```text
input
initial reconstruction
final reconstruction
absolute error map
```

Also save per-sample:

```text
global_MSE
foreground_MSE
background_MSE
balanced_reconstruction_loss
zero-output baseline metrics
```

All reconstruction metrics use the same `[0,1]` RGB scale and per-image definitions specified above.

Artifacts must clearly identify whether the sample is:

```text
Seen
Held-out
```

---

# 37. Held-out Probe Success

For attribute `A`, Held-out Probe Success requires all:

```text
1. heldout_probe_delta_A > 0
   in at least 4/5 seeds

2. median(heldout_probe_delta_A) >= 0.05

3. median(final_heldout_accuracy_A) >= 0.70
```

All comparisons are exact.

No tolerance or post-hoc threshold change is permitted.

---

# 38. Cross-distance Success

For attribute `A`, Cross-distance Success requires all:

```text
1. final_cross_contrast_A > 0
   in at least 4/5 seeds

2. median(cross_distance_delta_A) > 0
```

---

# 39. Attribute Success

For:

```text
A ∈ {color, shape}
```

define:

```text
ATTRIBUTE_SUCCESS_A
=
HELDOUT_PROBE_SUCCESS_A
AND
CROSS_DISTANCE_SUCCESS_A
```

---

# 40. Experiment-level Aggregation Precedence

Experiment-level classification MUST follow this precedence exactly.

## Step 1 — Formal set validity

If the exact formal five-seed set does not exist as five same-commit, same-required-environment formal attempts, or if any selected formal run is:

```text
INVALID
```

then:

```text
NOT_EVALUATED
```

Stop classification.

## Step 2 — Experimental failure

If Step 1 passes but at least one formal run is:

```text
EXPERIMENTAL_FAILURE
```

then:

```text
INCONCLUSIVE
```

Stop classification.

## Step 3 — Missing required primary evidence

If all five runs are non-INVALID but required primary probe or required primary cross-distance metrics are unavailable because of:

```text
PROBE_FAILED
DISTANCE_FAILED
```

or equivalent missing/non-finite primary evidence, then:

```text
INCONCLUSIVE
```

Stop classification.

## Step 4 — Reconstruction sanity

If required primary evidence exists but the reconstruction sanity gate fails:

```text
INCONCLUSIVE
```

Stop classification.

## Step 5 — SUCCESS

If:

```text
ATTRIBUTE_SUCCESS_color
OR
ATTRIBUTE_SUCCESS_shape
```

then:

```text
SUCCESS
```

Stop classification.

## Step 6 — Positive-direction inconclusive evidence

If not SUCCESS, but for at least one attribute:

```text
median(heldout_probe_delta_A) > 0
```

OR:

```text
median(cross_distance_delta_A) > 0
```

then:

```text
INCONCLUSIVE
```

Stop classification.

## Step 7 — Otherwise

If all required evidence exists, reconstruction sanity passes, SUCCESS is false, and neither attribute has positive median held-out probe delta nor positive median cross-distance delta:

```text
NO_EVIDENCE
```

---

# 41. Secondary Evaluation Flags

The following flags do not independently block scientific tri-state classification:

```text
BOOTSTRAP_CI_FAILED
PIXEL_BASELINE_FAILED
```

Report them as warnings.

Recommended experiment-level warning labels:

```text
BOOTSTRAP_CI_FAILED
-> DISTANCE_CI_INCOMPLETE
```

```text
PIXEL_BASELINE_FAILED
-> CONTROL_INCOMPLETE
```

Multiple evaluation flags may coexist.

---

# 42. Run Execution Status

Run-level execution status remains separate from evaluation flags.

Execution statuses:

```text
VALID
INVALID
EXPERIMENTAL_FAILURE
```

A run that executes training and the evaluation pipeline normally remains:

```text
VALID
```

even if it contains:

```text
PROBE_FAILED
DISTANCE_FAILED
BOOTSTRAP_CI_FAILED
PIXEL_BASELINE_FAILED
```

These remain evaluation flags.

---

# 43. Experimental Failure

`EXPERIMENTAL_FAILURE` is reserved for scientific/numerical run failure such as:

```text
non-finite training loss
non-finite gradients
non-finite parameters
numerical training failure
```

It is not assigned merely because a downstream evaluation failed.

---

# 44. Performance Optimization

Experiment 002 permits implementation-level CPU performance optimization.

Allowed examples:

```text
OMP_NUM_THREADS tuning
MKL_NUM_THREADS tuning
torch.set_num_threads()
torch.set_num_interop_threads()
DataLoader num_workers
persistent_workers
in-memory dataset reuse
vectorization
chunk optimization
disk I/O reduction
```

These choices must not alter the mathematical experiment.

---

# 45. Prohibited Performance Changes

Performance optimization MUST NOT change:

```text
batch size
model architecture
latent dimension
optimizer
learning rate
training epochs
loss mathematics
dataset contents
split contents
probe mathematics
distance mathematics
bootstrap mathematics
success criteria
```

---

# 46. Performance Benchmarking

Performance benchmarking is permitted before formal execution only.

Rules:

```text
- benchmark runs are non-formal
- selection criterion is wall-clock performance only
- scientific metrics MUST NOT determine the chosen configuration
- no formal result may be used for tuning
- selected configuration is frozen before formal RUN
- all five formal seeds use the same configuration
```

The final selected performance configuration must be recorded in formal run artifacts.

---

# 47. Formal Run Consistency

All five formal runs must use the same:

```text
git commit
Python environment
required dependency versions
NumPy version
PyTorch version
device class
thread configuration
DataLoader worker configuration
scientific implementation
```

Cross-hardware bitwise equality is not required.

Same-environment reproducibility remains the target.

---

# 48. Secondary Analyses

The following are secondary and do not independently establish SUCCESS:

```text
Seen-only probe
generalization gap
Seen-only distance
Held-out-only distance
raw Euclidean distance
Pixel baselines
PCA
reconstruction visualizations
bootstrap CI presence
Held-out reconstruction quality
```

They may be used for scientific interpretation only.

---

# 49. Interpretation Boundary

A successful Experiment 002 may support evidence that:

> attribute-related latent structure learned from seen combinations is reusable on unseen combinations within this defined synthetic domain.

Experiment 002 alone does not establish:

```text
human-like concept formation
general multimodal concept formation
language-independent reasoning
general intelligence
universal concept cores
transfer to natural images
transfer outside the defined synthetic distribution
```

---

# 50. No Post-hoc Modification

After formal execution begins, do not change:

```text
held-out combinations
sample counts
split assignment rules
loss weights
loss aggregation semantics
probe thresholds
distance success rules
bootstrap seed derivation
bootstrap stream assignment
bootstrap sampling rules
reconstruction gate thresholds
formal seeds
performance configuration
```

Any such change requires a separately versioned experiment or new formal baseline.

---

# 51. Formal Scientific Question

Experiment 002 asks:

> When trivial reconstruction is discouraged and some color×shape combinations are excluded from training, does self-supervised autoencoder training produce attribute-related latent structure that improves from random initialization and transfers to unseen attribute combinations?

---

# 52. Formal Specification Status

This document status is:

```text
APPROVED_FORMAL_SPECIFICATION
```

The previously identified review blockers are addressed by explicit specification of:

```text
NB-002-01:
per-image-first foreground/background reconstruction aggregation

NB-002-02:
explicit Seen-only bootstrap design
independent deterministic Seen-only and cross-distance RNG streams
explicit Held-out-only no-CI policy
```

These resolutions passed final review and are approved.

Formal Experiment 002 execution may begin only after implementation against this specification and verification are complete.