"""Frozen formal-baseline manifests and append-only attempt registration."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import torch

from .artifacts import (clean_commit, environment, implementation_fingerprint, read_json,
                        require_verification, require_versions, sha256_file, write_json)
from .config import FORMAL_SEEDS
from .performance import Performance


SCHEMA_VERSION = "exp002-formal-baseline-v1"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _now():
    return datetime.now(timezone.utc).isoformat()


def _hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _checked_identifier(value, name):
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Invalid {name}")
    return value


def _with_hash(value, field):
    result = dict(value)
    result[field] = _hash(result)
    return result


def _check_hash(value, field):
    expected = value.get(field)
    unhashed = {k: v for k, v in value.items() if k != field}
    if not isinstance(expected, str) or expected != _hash(unhashed):
        raise ValueError(f"{field} integrity mismatch")


def freeze_baseline(root, baseline, baseline_id, baseline_version, receipt_path, performance,
                    device="cpu", predecessor=None, reason=None):
    """Create, but never replace, a complete formal baseline freeze record."""
    root, baseline = Path(root), Path(baseline)
    baseline_id = _checked_identifier(baseline_id, "baseline_id")
    baseline_version = _checked_identifier(baseline_version, "baseline_version")
    if (predecessor is None) != (reason is None):
        raise ValueError("A successor baseline requires both predecessor and reason")
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        raise ValueError("A successor baseline requires a non-empty reason")
    predecessor_record = None
    if predecessor is not None:
        previous = load_manifest(predecessor)
        if (previous["baseline_id"], previous["baseline_version"]) == (baseline_id, baseline_version):
            raise ValueError("A successor baseline requires a new identity or version")
        predecessor_record = {k: previous[k] for k in ("baseline_id", "baseline_version", "manifest_hash")}
    runtime = require_versions()
    receipt = require_verification(root, receipt_path)
    perf = Performance(**performance).as_dict()
    device_class = torch.device(device).type
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "experiment": "exp002",
        "decision": "HD-002-01",
        "baseline_id": baseline_id,
        "baseline_version": baseline_version,
        "created_at": _now(),
        "freeze_provenance": {"operation": "freeze-baseline", "formal_results_consulted": False,
                              "performance_selection_criterion": "wall-clock-only",
                              "verification_predates_formal_run": True},
        "formal_master_seeds": list(FORMAL_SEEDS),
        "execution_commit": clean_commit(root),
        "implementation": implementation_fingerprint(root),
        "verification": {"identity": Path(receipt_path).name, "sha256": sha256_file(receipt_path),
                         "payload_hash": _hash(receipt), "receipt": receipt},
        "required_environment": runtime,
        "device": device,
        "device_class": device_class,
        "frozen_performance": perf,
        "canonical_attempt_registration": {
            "model": "first-registration-wins-append-only",
            "slots": {str(seed): None for seed in FORMAL_SEEDS},
        },
        "predecessor": predecessor_record,
        "new_baseline_reason": reason,
        "frozen": True,
    }
    manifest = _with_hash(manifest, "manifest_hash")
    baseline.mkdir(parents=True, exist_ok=False)
    write_json(baseline / "manifest.json", manifest)
    (baseline / "canonical").mkdir()
    (baseline / "retries").mkdir()
    return manifest


def load_manifest(baseline):
    baseline = Path(baseline)
    manifest = read_json(baseline / "manifest.json")
    _check_hash(manifest, "manifest_hash")
    if (manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("experiment") != "exp002"
            or manifest.get("decision") != "HD-002-01" or manifest.get("frozen") is not True
            or manifest.get("formal_master_seeds") != list(FORMAL_SEEDS)):
        raise ValueError("Invalid or unfrozen Exp002 baseline manifest")
    slots = manifest.get("canonical_attempt_registration", {}).get("slots")
    if slots != {str(seed): None for seed in FORMAL_SEEDS}:
        raise ValueError("Canonical slot declaration mismatch")
    Performance(**manifest.get("frozen_performance", {}))
    verification = manifest.get("verification", {})
    receipt = verification.get("receipt", {})
    if (verification.get("payload_hash") != _hash(receipt)
            or not re.fullmatch(r"[0-9a-f]{64}", str(verification.get("sha256", "")))
            or receipt.get("experiment_id") != "exp002" or receipt.get("exit_code") != 0
            or receipt.get("implementation") != manifest.get("implementation")
            or receipt.get("environment") != manifest.get("required_environment")):
        raise ValueError("Frozen verification binding is invalid")
    return manifest


def validate_runtime(root, baseline):
    manifest = load_manifest(baseline)
    if clean_commit(root) != manifest["execution_commit"]:
        raise ValueError("Execution commit differs from frozen baseline")
    if implementation_fingerprint(root) != manifest["implementation"]:
        raise ValueError("Implementation differs from frozen baseline")
    if require_versions() != manifest["required_environment"] or environment() != manifest["required_environment"]:
        raise ValueError("Runtime environment differs from frozen baseline")
    if torch.device(manifest["device"]).type != manifest["device_class"]:
        raise ValueError("Device identity differs from frozen baseline")
    return manifest


def _registration(value):
    return _with_hash(value, "registration_hash")


def _load_registration(path, manifest):
    record = read_json(path)
    _check_hash(record, "registration_hash")
    if record.get("manifest_hash") != manifest["manifest_hash"]:
        raise ValueError("Attempt registration belongs to another manifest")
    return record


def _all_registrations(baseline, manifest):
    paths = list((Path(baseline) / "canonical").glob("*.json")) + list((Path(baseline) / "retries").glob("*.json"))
    return [_load_registration(p, manifest) for p in paths]


def register_attempt(baseline, master_seed, attempt_id, output, retry_of=None, reason=None):
    """Register before execution. Exclusive creation makes the first seed attempt canonical."""
    baseline, output = Path(baseline), Path(output)
    manifest = load_manifest(baseline)
    if master_seed not in FORMAL_SEEDS:
        raise ValueError("Formal execution requires an approved master seed")
    attempt_id = _checked_identifier(attempt_id, "attempt_id")
    if output.exists():
        raise FileExistsError("Attempt output already exists")
    existing = _all_registrations(baseline, manifest)
    if attempt_id in {r["attempt_id"] for r in existing}:
        raise FileExistsError("Attempt ID already registered")
    if str(output.resolve()) in {r["output"] for r in existing}:
        raise FileExistsError("Attempt output already registered")
    canonical_path = baseline / "canonical" / f"{master_seed}.json"
    common = {"schema_version": SCHEMA_VERSION, "manifest_hash": manifest["manifest_hash"],
              "baseline_id": manifest["baseline_id"], "baseline_version": manifest["baseline_version"],
              "master_seed": master_seed, "attempt_id": attempt_id, "registered_at": _now(),
              "output": str(output.resolve())}
    if retry_of is None:
        if reason is not None:
            raise ValueError("Retry reason is only valid for a retry")
        record = _registration({**common, "attempt_kind": "canonical", "parent_canonical_attempt_id": None,
                                "reason": None})
        write_json(canonical_path, record)
        return record
    canonical = _load_registration(canonical_path, manifest)
    if retry_of != canonical["attempt_id"]:
        raise ValueError("Retry parent must be this seed's canonical attempt")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Retry requires a non-empty reason")
    record = _registration({**common, "attempt_kind": "retry", "parent_canonical_attempt_id": retry_of,
                            "reason": reason})
    write_json(baseline / "retries" / f"{attempt_id}.json", record)
    return record


def canonical_registrations(baseline, require_complete=True):
    baseline = Path(baseline)
    manifest = load_manifest(baseline)
    records = []
    for seed in FORMAL_SEEDS:
        path = baseline / "canonical" / f"{seed}.json"
        if not path.is_file():
            if require_complete:
                raise ValueError(f"Canonical attempt is not registered for seed {seed}")
            continue
        record = _load_registration(path, manifest)
        if (record.get("attempt_kind") != "canonical" or record.get("master_seed") != seed
                or record.get("parent_canonical_attempt_id") is not None):
            raise ValueError("Malformed canonical attempt registration")
        records.append(record)
    if len({r["attempt_id"] for r in records}) != len(records) or len({r["output"] for r in records}) != len(records):
        raise ValueError("Duplicate canonical attempt identity or output")
    return manifest, records


def retry_registrations(baseline):
    baseline = Path(baseline)
    manifest = load_manifest(baseline)
    result = []
    for path in sorted((baseline / "retries").glob("*.json")):
        record = _load_registration(path, manifest)
        canonical = _load_registration(baseline / "canonical" / f"{record['master_seed']}.json", manifest)
        if (record.get("attempt_kind") != "retry" or record.get("parent_canonical_attempt_id") != canonical["attempt_id"]):
            raise ValueError("Malformed retry registration")
        result.append(record)
    return result
