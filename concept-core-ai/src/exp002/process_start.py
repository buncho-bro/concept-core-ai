"""Stdlib-only guard for formal worker process-start thread settings."""
import hashlib
import json
import os
from pathlib import Path


_NATIVE_ROOTS = frozenset(("numpy", "torch", "scipy", "sklearn"))


def _hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_process_start_requirements(baseline):
    manifest = json.loads((Path(baseline) / "manifest.json").read_text(encoding="utf-8"))
    expected_hash = manifest.get("manifest_hash")
    if expected_hash != _hash({k: v for k, v in manifest.items() if k != "manifest_hash"}):
        raise ValueError("Baseline manifest integrity mismatch before worker launch")
    if manifest.get("schema_version") != "exp002-formal-baseline-v1" or manifest.get("frozen") is not True:
        raise ValueError("Formal worker requires a frozen Exp002 baseline")
    performance = manifest.get("frozen_performance", {})
    values = {"OMP_NUM_THREADS": performance.get("omp_threads"),
              "MKL_NUM_THREADS": performance.get("mkl_threads")}
    if any(type(value) is not int or value < 1 for value in values.values()):
        raise ValueError("Frozen process-start thread settings are invalid")
    return {name: str(value) for name, value in values.items()}


def validate_process_start(baseline, observed=None, loaded_modules=()):
    loaded_native = sorted({name.split(".", 1)[0] for name in loaded_modules} & _NATIVE_ROOTS)
    if loaded_native:
        raise ValueError("Scientific native modules loaded before process-start guard: " + ", ".join(loaded_native))
    required = load_process_start_requirements(baseline)
    observed = observed or {name: os.environ.get(name) for name in required}
    mismatches = {name: {"required": value, "observed": observed.get(name)}
                  for name, value in required.items() if observed.get(name) != value}
    if mismatches:
        raise ValueError("Formal worker process-start environment mismatch: " + json.dumps(mismatches, sort_keys=True))
    return {"required": required, "observed": {name: observed[name] for name in required},
            "validated_before_scientific_imports": True, "native_modules_loaded_before_guard": []}
