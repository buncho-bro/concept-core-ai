# Future Test and VERIFY Plan

> **NEW HUMAN-REVIEWED CANDIDATE CREATED AFTER NON-PERSISTENCE OF THE PREVIOUS UNTRACKED CANDIDATE**

This plan applies after normative promotion and implementation. Running these tests or any benchmark is outside this review task.

## A. Scientific and CPU regression

1. Run the full existing suite on CPU and prove unchanged seed fixed vectors, generated metadata/images, split membership, parameter count, objective, checkpoint structure, evaluation calculations, and aggregation logic.
2. Assert architecture, latent dimension, optimizer, learning rate, epochs=50, batch size=128, probe C grid, bootstrap count/mathematics, thresholds, master seeds, and purpose names are unchanged.
3. Confirm the CPU path remains usable and does not require CUDA libraries or GPU provenance fields that are irrelevant to a CPU baseline.

## B. CUDA structural and precision behavior

1. Exercise device movement for model, batches, reconstruction metrics, latent export, visualization, and checkpoint load using synthetic fixtures only.
2. Assert all scientific tensors/parameters/optimizer state and outputs use float32 where required.
3. Assert TF32 is disabled for every applicable matmul/cuDNN backend and the observed state is recorded.
4. Reject AMP, enabled autocast, GradScaler, FP16, BF16, quantization, automatic batch reduction, automatic precision changes, and silent CPU fallback.
5. Exercise deterministic-algorithm and backend settings; an unsupported/nondeterministic operation must fail rather than relax the policy.

## C. Process-start and provenance

1. Validate the reviewed `CUBLAS_WORKSPACE_CONFIG` value is in the environment before PyTorch/CUDA/native scientific imports. Test missing, wrong, and late values.
2. Validate fresh-process capture of GPU UUID/model, NVIDIA driver, PyTorch build/version, `torch.version.cuda`, actual runtime/interface, cuDNN, device capability, precision, TF32, and deterministic settings.
3. Distinguish an unused system CUDA toolkit as provenance-only; changing it alone must not masquerade as a change to the runtime used by PyTorch.
4. Reject GPU UUID/model, driver, PyTorch/CUDA, cuDNN, backend, precision, and process-start mismatches against a frozen original-set manifest.

## D. Seed-free fresh preflight and sequencing

1. Launch preflight in a fresh subprocess and prove no relevant CUDA/native state was inherited through earlier scientific imports.
2. Assert preflight accepts no formal master seed, does not call seed derivation, generate data, instantiate the formal model, train, evaluate, or compute scientific metrics.
3. Test CUDA unavailable, allocation failure, operation/synchronization failure, OOM, identity mismatch, and policy mismatch.
4. For every failed preflight, assert no canonical/retry registration and no scientific output directory are created.
5. On success, assert order: preflight receipt -> registration -> separate fresh formal worker -> worker revalidation -> scientific execution.

## E. Registration, worker revalidation, and immutable status

1. After registration, inject each identity/policy mismatch into worker revalidation and assert technical `INVALID` is recorded with the original registration intact.
2. Test worker start failure and revalidation crash artifacts for integrity and append-only audit behavior.
3. Assert retry records remain non-canonical and cannot replace a technical `INVALID` canonical attempt.
4. Assert formal aggregation refuses incomplete, mismatched, or substituted canonical sets and preserves §40 classification mathematics unchanged.

## F. Memory and failure behavior

1. Reset and record peak allocated and peak reserved memory around the approved workload using documented device synchronization boundaries.
2. Verify successful workload completion without OOM is required for candidate eligibility.
3. Verify there is no fixed VRAM-percentage rule.
4. Inject OOM before registration and during registered execution; confirm respectively no registration and immutable technical `INVALID`.
5. Confirm OOM never triggers smaller batch size, lower precision, CPU fallback, or continuation with altered work.

## G. Benchmark and selection governance

1. Validate that each complete eligible candidate is immutable before measurement and that distinct OMP/MKL/CUDA process-start configurations use fresh processes.
2. Require exactly five initial measured repetitions, preserving execution order and all wall-clock seconds; independently recompute min, max, and median.
3. Test non-overlapping ranges: no extra repetitions.
4. Test overlapping relevant ranges: exactly five additional repetitions for every relevant candidate; reject partial expansion and recompute from all ten.
5. Test persistent overlap: record `PERFORMANCE_TIE_OR_UNCERTAIN`, retain CPU incumbent, and prohibit CPU-superiority wording.
6. Verify technical reliability is an eligibility gate and ineligible candidates are disclosed but not assigned fake timings.
7. Prove selection input/ranking uses wall-clock data only. Training/validation loss, reconstruction, probe, distance, bootstrap, and other scientific metrics must be absent from the selector input or ignored and rejected by audit validation.

## H. Baseline-003 and lineage

1. Freeze only a test fixture identity representing `exp002-baseline-003/v1`; assert no baseline-001/002 runtime manifest is generated.
2. Validate governance-history fields separately from an optional real runtime-manifest predecessor field.
3. Assert baseline-003 can truthfully be first persistent runtime baseline and that its identity does not imply CUDA selection.
4. Require the complete selected configuration, benchmark evidence, VERIFY receipt, exact environment/device identity, and zero prior formal use before real freeze.

## I. Checkpoint portability and analysis

1. Save a CUDA-created synthetic checkpoint and load it on CPU using explicit map-location semantics; compare keys, shapes, dtypes, epoch, losses, and optimizer state structure.
2. Run CPU reanalysis/visualization against CUDA-generated synthetic artifacts without retraining or changing calculations.
3. Verify analysis artifacts retain source run/baseline/device provenance and cannot be mistaken for a new formal run.

## VERIFY acceptance record

A successful GPU-capable VERIFY must record:

- authoritative normative commit and implementation fingerprint;
- pinned Python/PyTorch/CUDA/cuDNN and driver observations;
- target GPU UUID/model;
- reviewed CUDA process-start value and proof it preceded native imports;
- FP32/TF32/deterministic state;
- preflight freshness and seed-free evidence;
- test inventory/results, including CPU regression;
- checkpoint portability result;
- scientific-condition diff showing no change;
- formal attempts and runs still zero.

VERIFY does not select CPU/CUDA, run the performance benchmark, freeze baseline-003, or execute formal seeds.

