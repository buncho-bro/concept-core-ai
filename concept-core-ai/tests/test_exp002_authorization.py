from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from exp001.artifacts import write_json
from exp002 import baseline
from exp002.performance import Performance


ENVIRONMENT = {"python": "3.12.fixture", "platform": "fixture", "packages": {}}
IMPLEMENTATION = {"fixture": "implementation"}
REASON = "Human-approved restart after canonical evidence review"


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, text=True,
                          capture_output=True).stdout.strip()


def repository(tmp_path):
    root = tmp_path / "repository"
    authorization_dir = root / "experiments" / "exp002" / "authorizations"
    authorization_dir.mkdir(parents=True)
    (root / "README.md").write_text("fixture\n", encoding="utf-8")
    git(root, "init")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "Fixture Human")
    git(root, "add", "README.md")
    git(root, "commit", "-m", "fixture root")
    return root, authorization_dir


def authorization_record(predecessor, version="v2", reason=REASON):
    return baseline._with_hash({
        "schema_version": baseline.AUTHORIZATION_SCHEMA_VERSION,
        "experiment": "exp002",
        "authorization_type": "successor_baseline",
        "decision": "HD-002-01",
        "authorization_id": "AUTH-EXP002-V1-V2",
        "predecessor": {k: predecessor[k] for k in ("baseline_id", "baseline_version", "manifest_hash")},
        "successor": {"baseline_id": "baseline", "baseline_version": version},
        "reason": reason,
    }, "integrity_hash")


def commit_authorization(root, directory, predecessor):
    path = directory / "AUTH-EXP002-V1-V2.json"
    write_json(path, authorization_record(predecessor))
    git(root, "add", path.relative_to(root).as_posix())
    git(root, "commit", "-m", "Human authorize Exp002 baseline v1 to v2")
    return path


def predecessor():
    return {"baseline_id": "baseline", "baseline_version": "v1", "manifest_hash": "1" * 64}


def test_untracked_authorization_is_rejected(tmp_path):
    root, directory = repository(tmp_path)
    path = directory / "untracked.json"
    write_json(path, authorization_record(predecessor()))
    with pytest.raises(ValueError, match="tracked|committed"):
        baseline.validate_successor_authorization(root, path, predecessor(), "baseline", "v2", REASON)


@pytest.mark.parametrize("change", ["predecessor", "predecessor_hash", "successor", "reason"])
def test_authorization_cannot_be_reused_for_a_different_transition(tmp_path, change):
    root, directory = repository(tmp_path)
    approved = predecessor()
    path = commit_authorization(root, directory, approved)
    actual, version, reason = deepcopy(approved), "v2", REASON
    if change == "predecessor": actual["baseline_version"] = "vX"
    elif change == "predecessor_hash": actual["manifest_hash"] = "2" * 64
    elif change == "successor": version = "v3"
    elif change == "reason": reason = "different reason"
    with pytest.raises(ValueError, match="exact transition"):
        baseline.validate_successor_authorization(root, path, actual, "baseline", version, reason)


@pytest.mark.parametrize("field", ["reason", "predecessor", "successor", "decision"])
def test_committed_authorization_tampering_is_rejected(tmp_path, field):
    root, directory = repository(tmp_path)
    approved = predecessor()
    path = commit_authorization(root, directory, approved)
    record = baseline.read_json(path)
    record[field] = "tampered" if field in ("reason", "decision") else {"tampered": True}
    write_json(path, record, replace=True)
    with pytest.raises(ValueError, match="integrity|committed|transition"):
        baseline.validate_successor_authorization(root, path, approved, "baseline", "v2", REASON)


def test_valid_committed_authorization_freezes_successor_and_initial_baseline_needs_none(tmp_path, monkeypatch):
    root, directory = repository(tmp_path)
    receipt_path = tmp_path / "verification.json"
    receipt = {"experiment_id": "exp002", "exit_code": 0, "environment": ENVIRONMENT,
               "implementation": IMPLEMENTATION, "formal_runs_executed": 0}
    write_json(receipt_path, receipt)
    monkeypatch.setattr(baseline, "require_versions", lambda: deepcopy(ENVIRONMENT))
    monkeypatch.setattr(baseline, "environment", lambda: deepcopy(ENVIRONMENT))
    monkeypatch.setattr(baseline, "implementation_fingerprint", lambda root: deepcopy(IMPLEMENTATION))
    monkeypatch.setattr(baseline, "require_verification", lambda root, path: deepcopy(receipt))
    v1 = tmp_path / "baseline-v1"
    original = baseline.freeze_baseline(root, v1, "baseline", "v1", receipt_path, Performance().as_dict())
    baseline.register_attempt(v1, 1001, "v1-first", tmp_path / "v1-run")
    unauthorized = tmp_path / "unauthorized-v2"
    with pytest.raises(ValueError, match="authorization"):
        baseline.freeze_baseline(root, unauthorized, "baseline", "v2", receipt_path, Performance().as_dict(),
                                 predecessor=v1, reason=REASON)
    assert not unauthorized.exists()
    authorization = commit_authorization(root, directory, original)
    v2 = tmp_path / "baseline-v2"
    successor = baseline.freeze_baseline(root, v2, "baseline", "v2", receipt_path, Performance().as_dict(),
        predecessor=v1, reason=REASON, authorization=authorization)
    assert baseline.load_manifest(v1) == original
    assert successor["predecessor"]["manifest_hash"] == original["manifest_hash"]
    assert successor["successor_authorization"]["authorization_id"] == "AUTH-EXP002-V1-V2"
    assert successor["successor_authorization"]["source_commit"] == git(root, "rev-parse", "HEAD")
    assert successor["successor_authorization"]["git_blob"]
    assert list((v2 / "canonical").glob("*.json")) == []
    baseline.validate_frozen_authorization(root, successor)


def test_successor_without_authorization_is_rejected_before_creation(tmp_path):
    target = tmp_path / "baseline-v2"
    with pytest.raises(ValueError, match="authorization"):
        baseline.freeze_baseline(tmp_path, target, "baseline", "v2", "receipt", Performance().as_dict(),
                                 predecessor=tmp_path / "v1", reason=REASON)
    assert not target.exists()
