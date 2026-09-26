from copy import deepcopy
from pathlib import Path

import pytest

from exp001.artifacts import read_json, write_json
from exp002 import aggregation, baseline, runner
from exp002.config import FORMAL_SEEDS, seeds_for
from exp002.performance import Performance


ENVIRONMENT = {"python": "3.12.fixture", "platform": "fixture", "packages": {
    name: "fixture" for name in ("numpy", "torch", "scipy", "scikit-learn", "matplotlib", "threadpoolctl")}}
IMPLEMENTATION = {"src/exp002/fixture.py": "f" * 64}


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    receipt_path = tmp_path / "verification.json"
    receipt = {"experiment_id": "exp002", "exit_code": 0, "environment": ENVIRONMENT,
               "implementation": IMPLEMENTATION, "formal_runs_executed": 0}
    write_json(receipt_path, receipt)
    monkeypatch.setattr(baseline, "require_versions", lambda: deepcopy(ENVIRONMENT))
    monkeypatch.setattr(baseline, "environment", lambda: deepcopy(ENVIRONMENT))
    monkeypatch.setattr(baseline, "clean_commit", lambda root: "commit-fixture")
    monkeypatch.setattr(baseline, "implementation_fingerprint", lambda root: deepcopy(IMPLEMENTATION))
    monkeypatch.setattr(baseline, "require_verification", lambda root, path: deepcopy(receipt))
    path = tmp_path / "baseline-v1"
    manifest = baseline.freeze_baseline(root, path, "baseline", "v1", receipt_path, Performance().as_dict())
    return root, path, manifest, receipt_path


def register_all(path, tmp_path):
    return [baseline.register_attempt(path, seed, f"canonical-{seed}", tmp_path / f"run-{seed}")
            for seed in FORMAL_SEEDS]


def scientific_record(seed, *, positive=True, status="VALID"):
    initial = .65 if positive else .70
    return {"experiment_id": "exp002", "master_seed": seed, "formal": True, "complete": True,
            "execution_status": status, "evaluation_flags": [], "git_commit": "commit-fixture",
            "seeds": seeds_for(seed), "environment": deepcopy(ENVIRONMENT),
            "performance": Performance().as_dict(), "device": "cpu", "device_class": "cpu",
            "implementation": deepcopy(IMPLEMENTATION), "baseline_id": "baseline", "baseline_version": "v1",
            "verification_receipt_sha256": None, "attempt_kind": "canonical",
            "parent_canonical_attempt_id": None,
            "reconstruction_sanity": {"balanced_ratio": .8, "foreground_ratio": .8},
            "primary": {a: {"initial_accuracy": initial, "final_accuracy": .70,
                            "initial_contrast": 0., "final_contrast": .1}
                        for a in ("color", "shape")}}


def bind_record(record, registration, manifest):
    record.update(path=registration["output"], attempt_id=registration["attempt_id"],
                  baseline_manifest_hash=manifest["manifest_hash"],
                  verification_receipt_sha256=manifest["verification"]["sha256"])
    return record


def test_first_registration_is_canonical_and_retry_never_replaces_it(frozen, tmp_path):
    _, path, _, _ = frozen
    first = baseline.register_attempt(path, 1001, "first", tmp_path / "first")
    (tmp_path / "first").mkdir()
    write_json(tmp_path / "first" / "status.json", {"execution_status": "VALID"})
    with pytest.raises(FileExistsError):
        baseline.register_attempt(path, 1001, "second", tmp_path / "second")
    retry = baseline.register_attempt(path, 1001, "retry-1", tmp_path / "retry", "first", "diagnosis")
    assert read_json(path / "canonical" / "1001.json")["attempt_id"] == "first"
    assert retry["attempt_kind"] == "retry" and retry["parent_canonical_attempt_id"] == "first"
    assert first["registered_at"] <= retry["registered_at"]


def test_baseline_freeze_requires_successful_preexisting_verification(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    receipt = tmp_path / "failed-verification.json"
    write_json(receipt, {"experiment_id": "exp002", "exit_code": 1})
    monkeypatch.setattr(baseline, "require_versions", lambda: deepcopy(ENVIRONMENT))
    monkeypatch.setattr(baseline, "require_verification",
                        lambda root, path: (_ for _ in ()).throw(ValueError("verification required")))
    target = tmp_path / "must-not-freeze"
    with pytest.raises(ValueError, match="verification"):
        baseline.freeze_baseline(root, target, "baseline", "v1", receipt, Performance().as_dict())
    assert not target.exists()


@pytest.mark.parametrize("knob,value", [
    ("torch_threads", 2), ("torch_interop_threads", 2), ("omp_threads", 2), ("mkl_threads", 2),
    ("num_workers", 1), ("persistent_workers", True),
])
def test_frozen_performance_cannot_be_changed(frozen, knob, value):
    _, path, manifest, _ = frozen
    assert manifest["frozen_performance"] == Performance().as_dict()
    tampered = read_json(path / "manifest.json")
    tampered["frozen_performance"][knob] = value
    write_json(path / "manifest.json", tampered, replace=True)
    with pytest.raises(ValueError, match="integrity"):
        baseline.load_manifest(path)


def test_new_baseline_preserves_predecessor_without_inheriting_attempts(frozen, tmp_path):
    root, v1, old, receipt = frozen
    baseline.register_attempt(v1, 1001, "v1-first", tmp_path / "v1-run")
    v2 = tmp_path / "baseline-v2"
    new = baseline.freeze_baseline(root, v2, "baseline", "v2", receipt, Performance().as_dict(),
                                   predecessor=v1, reason="Human-authorized restart")
    assert baseline.load_manifest(v1) == old
    assert new["manifest_hash"] != old["manifest_hash"]
    assert new["predecessor"] == {"baseline_id": "baseline", "baseline_version": "v1",
                                  "manifest_hash": old["manifest_hash"]}
    assert new["new_baseline_reason"] == "Human-authorized restart"
    assert list((v2 / "canonical").glob("*.json")) == []


def test_arbitrary_attempt_cherry_picking_cannot_change_formal_classification(frozen, tmp_path, monkeypatch):
    _, path, manifest, _ = frozen
    registrations = register_all(path, tmp_path)
    canonical = {}
    for index, registration in enumerate(registrations):
        canonical[registration["output"]] = bind_record(scientific_record(registration["master_seed"],
            positive=index < 4), registration, manifest)
    alternate = bind_record(scientific_record(1001, positive=False), registrations[0], manifest)
    alternate["path"] = str((tmp_path / "unregistered-favorable-or-unfavorable").resolve())
    caller_selected = [alternate if record["master_seed"] == 1001 else deepcopy(record)
                       for record in canonical.values()]
    assert aggregation.aggregate_records(caller_selected)["classification"] == "INCONCLUSIVE"
    monkeypatch.setattr(aggregation, "record_from_run", lambda p: deepcopy(canonical[str(Path(p).resolve())]))
    result = aggregation.aggregate_baseline(path, tmp_path / "aggregate")
    assert result["classification"] == "SUCCESS"
    assert result["canonical_attempt_ids"] == [f"canonical-{seed}" for seed in FORMAL_SEEDS]
    assert alternate["path"] not in [r["path"] for r in result["runs"]]


@pytest.mark.parametrize("canonical_status,expected", [("INVALID", "NOT_EVALUATED"),
                                                         ("EXPERIMENTAL_FAILURE", "INCONCLUSIVE")])
def test_valid_retry_does_not_replace_failed_canonical(frozen, tmp_path, monkeypatch,
                                                        canonical_status, expected):
    _, path, manifest, _ = frozen
    registrations = register_all(path, tmp_path)
    baseline.register_attempt(path, 1001, "retry-valid", tmp_path / "retry-valid",
                              "canonical-1001", "diagnostic retry")
    records = {}
    for registration in registrations:
        status = canonical_status if registration["master_seed"] == 1001 else "VALID"
        records[registration["output"]] = bind_record(scientific_record(registration["master_seed"], status=status),
                                                       registration, manifest)
    records[str((tmp_path / "retry-valid").resolve())] = {"execution_status": "VALID", "complete": True}
    monkeypatch.setattr(aggregation, "record_from_run", lambda p: deepcopy(records[str(Path(p).resolve())]))
    result = aggregation.aggregate_baseline(path, tmp_path / f"aggregate-{canonical_status}")
    assert result["classification"] == expected
    assert result["runs"][0]["execution_status"] == canonical_status
    assert result["retries"][0]["execution_status"] == "VALID"


def test_runner_requires_preexisting_frozen_manifest_and_registers_before_execution(frozen, tmp_path, monkeypatch):
    root, path, manifest, _ = frozen
    observed = {}
    def fake_execute(config, output, receipt, performance):
        observed["registration"] = read_json(path / "canonical" / "1001.json")
        observed["config"] = config
        return {"execution_status": "VALID", "complete": True}
    monkeypatch.setattr(runner, "_execute_attempt", fake_execute)
    monkeypatch.setattr(runner.Performance, "apply", lambda self: None)
    monkeypatch.setattr(runner, "configure_precision", lambda: None)
    runner.run_one(1001, tmp_path / "run", root, path, "first")
    assert observed["registration"]["attempt_id"] == "first"
    assert observed["config"]["performance"] == manifest["frozen_performance"]
    assert observed["config"]["baseline_manifest_hash"] == manifest["manifest_hash"]
    with pytest.raises((FileNotFoundError, ValueError)):
        runner.run_one(1002, tmp_path / "no-run", root, tmp_path / "missing", "never")
    assert not (tmp_path / "no-run").exists()


def test_incomplete_canonical_set_is_step_one_not_evaluated(frozen, tmp_path, monkeypatch):
    _, path, manifest, _ = frozen
    registration = baseline.register_attempt(path, 1001, "only-one", tmp_path / "run-1001")
    record = bind_record(scientific_record(1001), registration, manifest)
    monkeypatch.setattr(aggregation, "record_from_run", lambda p: deepcopy(record))
    result = aggregation.aggregate_baseline(path, tmp_path / "aggregate-incomplete")
    assert result["classification"] == "NOT_EVALUATED" and result["step"] == 1
    assert result["canonical_attempt_ids"] == ["only-one"]


def test_all_canonical_attempts_must_match_frozen_performance(frozen, tmp_path, monkeypatch):
    _, path, manifest, _ = frozen
    registrations = register_all(path, tmp_path)
    records = {}
    for registration in registrations:
        record = bind_record(scientific_record(registration["master_seed"]), registration, manifest)
        records[registration["output"]] = record
    records[registrations[-1]["output"]]["performance"]["torch_threads"] = 2
    monkeypatch.setattr(aggregation, "record_from_run", lambda p: deepcopy(records[str(Path(p).resolve())]))
    result = aggregation.aggregate_baseline(path, tmp_path / "aggregate-mismatch")
    assert result["classification"] == "NOT_EVALUATED" and result["step"] == 1
    assert "performance" in result["runs"][-1]["integrity_error"]


def test_formal_cli_has_no_arbitrary_paths_or_per_run_performance():
    from exp002 import cli
    with pytest.raises(SystemExit):
        cli.main(["aggregate", "one", "two", "three", "four", "five", "--output", "unused"])
    with pytest.raises(SystemExit):
        cli.main(["run-one", "--mode", "RUN", "--master-seed", "1001", "--baseline", "b",
                  "--attempt-id", "a", "--output", "o", "--performance", "p"])
