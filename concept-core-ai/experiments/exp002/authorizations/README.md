# Experiment 002 successor authorizations

This directory is reserved for Human-approved successor-baseline authorization records under `HD-002-01`.

One committed JSON record authorizes exactly one predecessor manifest hash, successor baseline ID/version, and reason. The record must contain:

```text
schema_version = exp002-successor-authorization-v1
experiment = exp002
authorization_type = successor_baseline
decision = HD-002-01
authorization_id
predecessor {baseline_id, baseline_version, manifest_hash}
successor {baseline_id, baseline_version}
reason
integrity_hash
```

`integrity_hash` is SHA-256 over canonical JSON of all other fields (UTF-8, sorted keys, compact separators). Preparing or generating a candidate file is not approval. Approval requires the exact record to be reviewed and committed through the repository workflow before `freeze-baseline` consumes it. Do not put runtime-generated approvals or run results here.

No successor transition is authorized by this README.
