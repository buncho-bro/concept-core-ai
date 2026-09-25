from unittest.mock import Mock
import numpy as np
import pytest
import torch
from exp001.artifacts import check_integrity, read_json, write_json
from exp002 import runner
from exp002.config import configuration, seeds_for
from exp002.performance import Performance


@pytest.fixture
def status_fixture(tmp_path, monkeypatch):
    config = {**configuration(), "formal": False, "master_seed": 77, "seeds": seeds_for(77),
              "device": "cpu", "run_id": "synthetic-status-fixture"}
    # No formal seed and no model optimization. This tests orchestration states.
    monkeypatch.setattr(runner, "generate_images", lambda *args: np.broadcast_to(np.zeros((64, 64, 3), np.float32), (9000, 64, 64, 3)))
    monkeypatch.setattr(runner, "Autoencoder", lambda seed: torch.nn.Linear(1, 1))
    training, export, evaluation = Mock(), Mock(), Mock(return_value={"evaluation_flags": []})
    monkeypatch.setattr(runner, "train", training)
    monkeypatch.setattr(runner, "export_states", export)
    monkeypatch.setattr(runner, "evaluate_saved", evaluation)
    return config, tmp_path / "synthetic-status-fixture", training, export, evaluation


@pytest.mark.parametrize("flags", [[], ["PROBE_FAILED"], ["DISTANCE_FAILED"], ["PROBE_FAILED", "DISTANCE_FAILED"],
                                    ["BOOTSTRAP_CI_FAILED", "PIXEL_BASELINE_FAILED"]])
def test_evaluation_flags_never_change_execution_status(status_fixture, flags):
    config, output, training, export, evaluation = status_fixture
    evaluation.return_value = {"evaluation_flags": flags}
    status = runner._execute_attempt(config, output, {"fixture": True}, Performance())
    assert status == {"execution_status": "VALID", "evaluation_flags": flags, "complete": True, "reason": None}
    assert read_json(output / "configuration.json")["formal"] is False
    assert read_json(output / "status.json") == status
    training.assert_called_once(); export.assert_called_once(); evaluation.assert_called_once()
    check_integrity(output)


def test_numerical_training_failure_status_and_preserved_artifacts(status_fixture):
    config, output, training, export, evaluation = status_fixture
    training.side_effect = runner.ExperimentalFailure("Non-finite training fixture")
    status = runner._execute_attempt(config, output, {"fixture": True}, Performance())
    assert status["execution_status"] == "EXPERIMENTAL_FAILURE" and status["complete"]
    assert read_json(output / "failure.json")["type"] == "ExperimentalFailure"
    export.assert_not_called(); evaluation.assert_not_called()
    check_integrity(output)


@pytest.mark.parametrize("stage", ["training", "export", "evaluation"])
def test_technical_exception_is_invalid(status_fixture, stage):
    config, output, training, export, evaluation = status_fixture
    {"training": training, "export": export, "evaluation": evaluation}[stage].side_effect = RuntimeError("technical fixture")
    with pytest.raises(RuntimeError):
        runner._execute_attempt(config, output, {"fixture": True}, Performance())
    status = read_json(output / "status.json")
    assert status["execution_status"] == "INVALID" and not status["complete"]
    check_integrity(output)


def test_verify_cli_cannot_dispatch_run(tmp_path, monkeypatch):
    from exp002 import cli
    monkeypatch.setattr(runner, "run_one", lambda *args, **kwargs: pytest.fail("Formal execution is forbidden in tests"))
    calls = []
    monkeypatch.setattr(cli, "verify", lambda output, root: calls.append(output) or 0)
    assert cli.main(["verify", "--output", str(tmp_path / "verification")]) == 0
    assert len(calls) == 1
    with pytest.raises(SystemExit):
        cli.main(["run-one", "--master-seed", "77", "--output", str(tmp_path)])


def test_verification_fingerprint_includes_exp002_sources_and_environment(tmp_path, monkeypatch):
    from exp002 import artifacts
    root = tmp_path / "project"
    (root / "src" / "exp002").mkdir(parents=True)
    source = root / "src" / "exp002" / "sample.py"
    source.write_text("pass\n")
    monkeypatch.setattr(artifacts, "environment", lambda: {"fixture": True})
    receipt = tmp_path / "receipt.json"
    value = {"experiment_id": "exp002", "exit_code": 0, "environment": {"fixture": True},
             "implementation": artifacts.implementation_fingerprint(root)}
    write_json(receipt, value)
    assert artifacts.require_verification(root, receipt) == value
    source.write_text("raise RuntimeError\n")
    with pytest.raises(ValueError, match="verification"):
        artifacts.require_verification(root, receipt)


def test_formal_run_guards_reject_test_seed_before_creating_artifacts(tmp_path):
    with pytest.raises(ValueError, match="approved master seed"):
        runner.run_one(77, tmp_path / "forbidden", tmp_path, "none", Performance().as_dict())
    assert not (tmp_path / "forbidden").exists()
