# Experiment 002 — Decisions

## 0. Purpose

This document records the research decisions behind Experiment 002.

The normative experimental definition is `spec.md`.

If this document conflicts with `spec.md`, `spec.md` takes precedence.

This document exists to preserve:

- why Experiment 002 was introduced,
- why its design differs from Experiment 001,
- which alternatives were considered,
- which decisions are scientific rather than implementation details,
- which questions remain outside the scope of Experiment 002.

---

# 1. Starting Point: Experiment 001

Experiment 002 is motivated by the results and limitations of Experiment 001.

Experiment 001 produced useful evidence about latent structure, but it did not provide sufficient evidence to conclude that the tested autoencoder learned reusable concept-like representations.

Two observations were especially important.

First, some attributes were already highly readable from the randomly initialized encoder.

In particular, color probe performance was already near ceiling before training.

Therefore:

> high final probe accuracy alone is not sufficient evidence that training created an attribute-related representation.

Second, the Experiment 001 reconstruction objective admitted a trivial solution.

The dataset contained a large black background, and global pixel MSE strongly rewarded reconstructing that background.

The trained decoder therefore produced nearly black reconstructions while still obtaining substantially lower global MSE.

Therefore:

> lower global reconstruction MSE did not establish that the model learned meaningful reconstruction of the objects.

Experiment 002 is designed primarily around these two lessons.

---

# 2. Decision: Test Reusability, Not Only Readability

## Decision

Experiment 002 evaluates whether attribute-related structure learned from some color×shape combinations transfers to combinations excluded from training.

## Reason

A representation can make an attribute linearly readable without having learned a reusable abstraction.

Experiment 001 demonstrated this problem directly through strong initial random-feature probe performance.

Therefore Experiment 002 asks a harder question:

> Can a representation learned from known attributes in seen combinations be reused when those attributes appear in a new combination?

This is closer to the intended concept-core research direction than measuring readability on the same combination distribution used during learning.

## Not claimed

Successful transfer does not by itself prove that the model has formed a concept core.

It is evidence for reusable internal structure within the synthetic domain.

---

# 3. Decision: Use Combination Hold-out

## Decision

The nine color×shape combinations are divided into six seen combinations and three held-out combinations.

Seen:

```text id="f7w61g"
red circle
red triangle
green triangle
green square
blue square
blue circle
```

Held-out:

```text id="8qu7e8"
red square
green circle
blue triangle
```

## Reason

Every color must remain observable during training.

Every shape must remain observable during training.

At the same time, the held-out pair itself must remain unseen.

The selected arrangement gives every color and every shape exactly two seen combinations.

Thus a held-out sample contains known components in a novel combination.

This distinguishes combination generalization from unseen-class recognition.

---

# 4. Decision: Held-out Data Must Not Influence Representation or Probe Selection

## Decision

Held-out samples are excluded from:

- autoencoder training,
- autoencoder validation,
- probe training,
- probe validation,
- scaler fitting,
- C selection,
- threshold selection.

## Reason

The held-out set is intended to measure transfer to an unseen combination.

Allowing held-out information to influence model fitting or model-selection decisions would weaken that interpretation.

The held-out labels are therefore evaluation-only.

---

# 5. Decision: Generate 1000 Samples for Every Combination

## Decision

All nine combinations retain the Experiment 001 scale of 1000 generated samples per combination.

Seen combinations use:

```text id="d91p5w"
800 Train
100 Validation
100 Seen Test
```

Held-out combinations use:

```text id="w2zgke"
100 Held-out Test
900 Reserved
```

## Reason

Keeping 1000 generated samples per combination preserves the basic dataset structure inherited from Experiment 001 while allowing Experiment 002 to introduce a combination hold-out without redefining the underlying generation scale.

The unused held-out samples are explicitly Reserved rather than silently discarded.

---

# 6. Decision: Reserved Samples Are Outside Formal Experiment 002

## Decision

The 2700 Reserved samples are not used in formal Experiment 002 analysis.

## Reason

Using them after inspecting formal results would create an additional unregistered evaluation set and increase opportunities for post-hoc analysis.

They are therefore generated for structural consistency but excluded from the formal experiment.

Future use requires a separately defined experiment or explicitly exploratory analysis.

---

# 7. Decision: Replace Global Training MSE with Foreground/Background Balanced MSE

## Decision

Experiment 002 replaces Experiment 001 global reconstruction MSE with:

```text id="rbj4l6"
balanced_loss
=
0.5 * foreground_MSE
+
0.5 * background_MSE
```

## Reason

Experiment 001 showed that global MSE was dominated by the black background.

A nearly black decoder output could therefore obtain a low loss without reconstructing the object meaningfully.

Equal foreground/background weighting prevents background pixel count from dominating the objective.

## Trade-off

The target-derived foreground mask introduces an inductive bias.

The model is not given the mask as input, but the learning objective explicitly distinguishes foreground from background.

This must therefore not be interpreted as fully unconstrained emergence of object structure.

---

# 8. Decision: Foreground Is Defined from the Target

## Decision

A target pixel is foreground when:

```text id="e4m3st"
R + G + B > 0
```

## Reason

The synthetic dataset provides an exact black background.

This gives a deterministic definition that also includes anti-aliased boundary pixels whenever their target RGB value is nonzero.

No learned segmentation or additional annotation system is required.

---

# 9. Decision: Reconstruction Aggregation Is Per-image-first

## Decision

Foreground and background MSE are calculated separately for each image.

The two region losses are combined 0.5/0.5 for that image.

Images are then averaged with equal weight.

## Reason

The initial review identified two mathematically different interpretations:

1. pool foreground/background pixels across the entire batch,
2. compute region losses per image and then average images.

Because shape area varies between samples, pooled-region averaging would give images with larger foreground regions greater influence on the foreground gradient.

Experiment 002 does not intend foreground area to determine sample importance.

Therefore every image receives equal weight.

## Rejected alternative

Batch-wide pooling of foreground or background RGB elements was rejected because it implicitly weights images by region area.

---

# 10. Decision: Use a Zero-output Reconstruction Baseline

## Decision

Experiment 002 explicitly evaluates an all-zero reconstruction baseline.

## Reason

Experiment 001 demonstrated that apparently low reconstruction loss can be misleading when the dataset admits a trivial background-dominated prediction.

The zero-output baseline provides a direct reference for whether the trained model is doing materially more than predicting black.

---

# 11. Decision: Reconstruction Sanity Is a Gate, Not the Main Success Metric

## Decision

The reconstruction sanity gate requires, on Seen Test:

```text id="2mq8o5"
median balanced_ratio <= 0.80
median foreground_ratio <= 0.80
```

and both ratios must be below `1.0` in at least four of five seeds.

## Reason

Experiment 002 is primarily about reusable latent structure, not reconstruction quality.

However, latent conclusions should not be interpreted as arising from the intended learning objective if reconstruction has again collapsed to a trivial solution.

Therefore reconstruction quality acts as a prerequisite for SUCCESS rather than as the main research outcome.

## Consequence

Failure of the gate produces `INCONCLUSIVE`, not `NO_EVIDENCE`.

This separates:

> the representation hypothesis was tested and unsupported

from:

> the intended learning setup itself did not function adequately.

---

# 12. Decision: Reconstruction Gate Uses Seen Test Only

## Decision

Held-out reconstruction quality does not participate in the reconstruction sanity gate.

## Reason

The gate asks whether the autoencoder meaningfully learned its reconstruction objective on the seen distribution.

Held-out reconstruction asks a different question: whether reconstruction itself generalizes to unseen combinations.

That is scientifically interesting but secondary to the formal gate.

---

# 13. Decision: Compare Initial and Final Representations

## Decision

Primary representation metrics compare the initial random encoder against the final trained encoder.

## Reason

Experiment 001 showed that random neural features can already make attributes highly readable.

Therefore:

```text id="wzj39g"
final performance
```

alone is insufficient.

Experiment 002 focuses on:

```text id="3b9g1w"
final - initial
```

to measure training-associated representational change.

---

# 14. Decision: Held-out Probe Is the Primary Probe Metric

## Decision

Probe classifiers are trained and selected using seen data and then evaluated on Held-out Test.

The primary probe change is:

```text id="p91h44"
heldout_probe_delta
=
final_heldout_accuracy
-
initial_heldout_accuracy
```

## Reason

Seen-Test probe accuracy primarily measures readability within combinations drawn from the training combination distribution.

Held-out accuracy instead asks whether the learned decision structure transfers to an unseen attribute combination.

This is more directly aligned with Experiment 002's research question.

---

# 15. Decision: Keep Seen Probe as Secondary Evidence

## Decision

Seen Test probe results are still recorded.

## Reason

They provide continuity with Experiment 001 and help distinguish several possible outcomes.

For example:

- improvement on seen and held-out,
- improvement on seen but not held-out,
- no improvement on either,
- held-out improvement without large seen improvement.

However, seen performance alone cannot establish Experiment 002 success.

---

# 16. Decision: Keep Pixel Baselines

## Decision

Simple pixel statistics and raw-pixel linear probes remain as controls.

## Reason

They indicate how much of the task can be solved directly from the input representation.

Experiment 001 showed that such controls materially affect interpretation.

## Limitation

Pixel baselines do not directly determine Experiment-level SUCCESS.

They are controls for interpretation.

---

# 17. Decision: Use Cross-distance as the Primary Geometry Test

## Decision

The primary geometry analysis compares Seen Test samples against Held-out Test samples.

For attribute `A`:

```text id="9i9h5d"
cross_contrast_A
=
mean(distance | different A)
-
mean(distance | same A)
```

## Reason

The key geometry question is whether an unseen combination is positioned closer to seen examples that share an attribute.

This directly tests whether attribute-related organization extends across the seen/held-out boundary.

---

# 18. Decision: Require Both Probe and Geometry Evidence

## Decision

Attribute success requires:

```text id="b4wd1f"
Held-out Probe Success
AND
Cross-distance Success
```

## Reason

Experiment 001 showed that different representation metrics can disagree.

A linear probe measures linear decodability.

Distance contrast measures latent geometry.

Neither alone should be treated as a complete description of the representation.

Experiment 002 therefore requires convergence of both forms of evidence before declaring an attribute successful.

---

# 19. Decision: Held-out-only Distance Is Descriptive

## Decision

Held-out-only distance analysis is secondary and does not require bootstrap confidence intervals.

## Reason

The three held-out combinations are:

```text id="n0l4sf"
red square
green circle
blue triangle
```

Within this subset, color and shape are confounded by combination identity.

Held-out-only geometry therefore cannot cleanly isolate color and shape effects.

The Seen↔Held-out cross-distance design is better suited to the primary question.

---

# 20. Decision: Standardization Uses Seen Train Only

## Decision

Latent and applicable pixel scalers are fitted using Seen Train only.

Initial and final latent states receive separate scalers.

## Reason

Held-out information must not influence representation normalization.

Separate initial/final scalers preserve the Experiment 001 interpretation of standardized geometry within each representation state.

---

# 21. Decision: Standardized Distance Is Primary, Raw Distance Is Secondary

## Decision

Primary distance success uses Seen-Train-standardized Euclidean distance.

Raw Euclidean distance is recorded only as secondary evidence.

## Reason

Experiment 001 showed that raw and standardized distance analyses can lead to materially different impressions.

Standardization reduces domination by latent dimensions solely because of scale.

Raw geometry remains useful for interpretation but does not determine success.

---

# 22. Decision: Seen-only and Cross Bootstrap Use Independent RNG Streams

## Decision

Seen-only distance bootstrap and Seen↔Held-out cross-distance bootstrap use independently derived deterministic sub-seeds.

## Reason

The initial review identified an ambiguity in how Experiment 001's 900-sample bootstrap should interact with Experiment 002's new 600/300 structure.

Sharing one RNG stream would also make the random draws of one analysis depend on whether another analysis ran first or consumed additional random values.

Independent streams ensure:

> changing the execution order of one bootstrap analysis does not alter the random samples used by the other.

This improves reproducibility and auditability.

---

# 23. Decision: Seen-only Bootstrap Resamples Samples, Not Pair Rows

## Decision

Seen-only bootstrap draws 600 sample instances with replacement from the 600 Seen Test samples.

Pairs are reconstructed from those instances.

## Reason

The observational unit is the sample, not an independently generated distance row.

Distances sharing a sample are statistically dependent.

Direct pair-row resampling would ignore that dependency structure.

This follows the sample-bootstrap principle established in Experiment 001 while adapting it to the new Seen Test size.

---

# 24. Decision: Cross Bootstrap Resamples Seen and Held-out Samples Separately

## Decision

Each cross bootstrap iteration draws:

```text id="fg3d8e"
600 Seen instances
then
300 Held-out instances
```

with replacement.

All cross pairs are reconstructed afterward.

## Reason

Seen and Held-out are distinct sample populations in the formal design.

Resampling them separately preserves this structure while estimating variation in the cross-distance statistic.

The draw order is fixed solely for deterministic reproducibility.

---

# 25. Decision: Use Five Formal Seeds

## Decision

Formal master seeds remain:

```text id="8t2g7x"
1001
1002
1003
1004
1005
```

## Reason

Keeping the same master-seed set preserves continuity with Experiment 001 and avoids changing replication count at the same time as the substantive experimental design.

Experiment 002 uses a distinct `exp002|` namespace so that its derived random streams are not identical to Experiment 001.

---

# 26. Decision: Held-out Probe Success Thresholds

## Decision

For an attribute, Held-out Probe Success requires:

```text id="93xumc"
positive delta in >= 4/5 seeds
median delta >= 0.05
median final held-out accuracy >= 0.70
```

## Reason

The criteria jointly require:

- seed consistency,
- nontrivial improvement over the random encoder,
- meaningful absolute held-out performance.

The `0.05` delta threshold is specific to the harder Experiment 002 transfer task.

It is not a reinterpretation or retroactive relaxation of the Experiment 001 `0.10` criterion.

---

# 27. Decision: Cross-distance Success Thresholds

## Decision

For an attribute, Cross-distance Success requires:

```text id="jue3t8"
final cross contrast > 0 in >= 4/5 seeds
median cross-distance delta > 0
```

## Reason

The standardized distance metric has no sufficiently justified domain-specific effect-size threshold.

Experiment 002 therefore preregisters directional consistency rather than inventing an arbitrary magnitude cutoff.

---

# 28. Decision: One Successful Attribute Is Sufficient for Experiment SUCCESS

## Decision

Experiment-level SUCCESS requires:

```text id="l37e4x"
reconstruction sanity gate passes
```

and at least one of:

```text id="qps6qk"
ATTRIBUTE_SUCCESS_color
ATTRIBUTE_SUCCESS_shape
```

## Reason

The experiment asks whether reusable attribute-related structure can emerge.

It does not require color and shape to be equally learnable under the chosen architecture and objective.

Success for one preregistered attribute is therefore scientifically informative.

Results for both attributes must still be reported.

---

# 29. Decision: Preserve INCONCLUSIVE as a Distinct Outcome

## Decision

Experiment 002 retains:

```text id="6o6hjm"
SUCCESS
INCONCLUSIVE
NO_EVIDENCE
NOT_EVALUATED
```

with the exact precedence defined in `spec.md`.

## Reason

Several outcomes should not be collapsed into `NO_EVIDENCE`, including:

- reconstruction gate failure,
- numerical experimental failure,
- missing required primary evidence,
- positive directional changes that do not satisfy preregistered success thresholds.

This prevents a technically weak or partially positive experiment from being interpreted as clean negative evidence.

---

# 30. Decision: Keep Run Status Separate from Evaluation Flags

## Decision

Run execution status remains separate from evaluation flags.

## Reason

Experiment 001 review established that a completed scientific run should not become `EXPERIMENTAL_FAILURE` merely because a downstream probe or distance evaluation failed.

Experiment 002 preserves this distinction.

---

# 31. Decision: Allow CPU Performance Optimization Without Scientific Changes

## Decision

Threading, DataLoader workers, vectorization, chunking, caching, and similar implementation-level performance changes are permitted under the constraints in `spec.md`.

## Reason

Experiment 001 execution showed that CPU utilization could be substantially improved.

Runtime engineering should therefore be allowed without forcing a new scientific experiment.

## Boundary

Performance optimization must not alter:

- batch size,
- optimizer,
- model architecture,
- learning rate,
- epochs,
- loss mathematics,
- dataset,
- evaluation mathematics,
- success criteria.

Performance configuration is selected before formal execution using wall-clock performance only and is then frozen across all five formal runs.

---

# 32. Decision: Keep the Basic Autoencoder Architecture

## Decision

Experiment 002 does not change the Experiment 001 autoencoder architecture, latent dimension, optimizer, batch size, or epoch count.

## Reason

Experiment 002 is intended to test the effects of:

1. repairing the reconstruction objective, and
2. introducing combination-generalization evaluation.

Changing the model simultaneously would make comparison with Experiment 001 harder to interpret.

Architecture changes can be tested in later experiments if necessary.

---

# 33. Decision: Do Not Tune After Formal Results

## Decision

Once formal Experiment 002 execution begins, preregistered scientific conditions are frozen.

## Reason

Changing thresholds, loss weights, hold-out combinations, bootstrap rules, or other scientific conditions after inspecting formal results would compromise the confirmatory interpretation.

Any such change requires a separately versioned experiment or new formal baseline.

---

# 34. Decision: Keep the Claim Narrow

## Decision

Even a successful Experiment 002 will be interpreted only as evidence for reusable attribute-related latent structure within the defined synthetic domain.

## Reason

Experiment 002 uses:

- simple synthetic images,
- two known attribute families,
- a target-derived foreground mask,
- a small autoencoder,
- explicitly selected evaluation attributes.

It therefore cannot establish general concept formation.

In particular, Experiment 002 does not establish:

- multimodal concepts,
- natural-image concepts,
- language-independent reasoning,
- autonomous discovery of arbitrary concepts,
- general intelligence,
- universal concept cores.

---

# 35. Relationship to the Long-term Research Direction

Experiment 002 is one incremental test within a broader concept-core research direction.

The long-term question is whether internal structures can emerge that are:

- reusable across experiences,
- less dependent on surface representation,
- compositional,
- eventually shareable across modalities,
- useful for reasoning rather than merely classification.

Experiment 002 tests only a small part of that idea:

> reuse of attribute-related internal structure across unseen combinations in a controlled visual environment.

The experiment is intentionally narrower than the long-term hypothesis.

---

# 36. Review History

The initial Experiment 002 review identified two blocking ambiguities.

```text id="u8zzhh"
NB-002-01
Balanced reconstruction loss aggregation unit
```

Resolution:

```text id="5j7a1c"
per-image-first region aggregation
with equal image weighting
```

```text id="j83vyu"
NB-002-02
Seen-only distance bootstrap design and RNG semantics
```

Resolution:

```text id="ugyyb6"
600-from-600 sample bootstrap
independent Seen-only and cross bootstrap RNG streams
Held-out-only distance remains descriptive without required CI
```

The subsequent final-candidate review classified both blockers as:

```text id="tck2io"
RESOLVED
```

and reported:

```text id="4pyzfr"
READINESS: READY_FOR_IMPLEMENTATION
NEW_BLOCKERS: NONE
AMBIGUITIES: NONE
CONFLICTS: NONE
```

---

# 37. Approval Boundary

The final-candidate review verified that the proposed specification is sufficiently complete and internally consistent for implementation.

Human approval has been granted for these reviewed Experiment 002 research decisions, and they are recorded in the formal decisions document.

Formal Experiment 002 execution requires:

```text id="l2s9kp"
1. implementation against the approved formal specification
2. verification before formal RUN
```

---

# 38. Decision State

The decisions recorded here correspond to the Experiment 002 Final Candidate that passed final review and received Human approval. These decisions are:

```text id="0jvhkh"
FROZEN_FOR_IMPLEMENTATION
```

Any scientific change after approval must be documented as a new decision and, when it can affect formal results, requires a new experiment version or formal baseline.