# Baseline 001 archived results

See [RUN_SUMMARY.md](RUN_SUMMARY.md) for execution status and the preregistered classification, and [RUN_MANIFEST.json](RUN_MANIFEST.json) for provenance.

The five archives in `artifacts/` contain all original run files, including images, metadata, splits, initial/final checkpoints, all 50 training epochs, latent arrays, evaluations, bootstrap samples, figures, configuration, verification receipt and integrity hashes. Each ZIP contains a single directory named `exp001-seed-<seed>-attempt-01`. Extract into a new, empty `runs/` directory beside this README to restore the relative manifest paths. Do not extract over an existing attempt.

`PUBLICATION_INTEGRITY.json` gives SHA-256 hashes for every published file except itself. Archive SHA-256 hashes and byte counts also appear in `RUN_MANIFEST.json`. Inside each restored run, `integrity.json` gives the original file hashes. All archived file hashes were checked against these original manifests during packaging.

`aggregate/` holds the original aggregate measurements and classification with only directory paths made portable. `verification/` holds the fresh pre-RUN receipt, test log and JUnit results; public log paths are sanitized and the JUnit hostname is omitted. `audit/` holds portable preflight/environment records, per-seed checks and execution logs. The original unredacted records remain in the local experiment checkout.

The execution commit is e9791b236e2c2618ed77e031e667c58b24e76e01. The later publication commit only adds results; it was not used to execute the baseline. Scientific implementation, research conditions and success rules were not changed.
