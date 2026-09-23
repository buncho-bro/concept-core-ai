"""Runner status regressions using mocked work, never a formal baseline run."""
from unittest.mock import Mock

import numpy as np
import pytest
import torch

from exp001 import runner
from exp001.artifacts import check_integrity, read_json, write_json
from exp001.config import configuration


@pytest.fixture
def runner_fixture(tmp_path, monkeypatch):
    # Allow one non-formal fixture seed only inside this isolated test harness.
    monkeypatch.setattr(runner, "FORMAL_SEEDS", (77,))
    monkeypatch.setattr(runner, "clean_commit", lambda root: "status-fixture")
    monkeypatch.setattr(runner, "require_verification", lambda *args: {"fixture": True})
    rows = [{"sample_id": i, "split": split} for i, split in enumerate(("train", "validation", "test"))]
    monkeypatch.setattr(runner, "generate_metadata", lambda seed: rows)
    monkeypatch.setattr(runner, "assign_splits", lambda rows, seed: rows)
    monkeypatch.setattr(runner, "generate_images", lambda *args: np.zeros((3, 64, 64, 3), dtype=np.float32))
    monkeypatch.setattr(runner, "Autoencoder", lambda seed: torch.nn.Linear(1, 1))
    training = Mock(return_value=[])
    export = Mock(return_value={})
    evaluation = Mock(return_value={"evaluation_flags": []})
    monkeypatch.setattr(runner, "train", training)
    monkeypatch.setattr(runner, "export_states", export)
    monkeypatch.setattr(runner, "evaluate_saved", evaluation)
    return tmp_path / "status-fixture", training, export, evaluation


@pytest.mark.parametrize("flags", [
    [],
    ["PROBE_FAILED"],
    ["DISTANCE_FAILED"],
    ["PROBE_FAILED", "DISTANCE_FAILED"],
], ids=["A-no-flags", "B-probe-failed", "C-distance-failed", "D-both-failed"])
def test_completed_runner_keeps_valid_with_evaluation_flags(runner_fixture, tmp_path, flags):
    output, training, export, evaluation = runner_fixture
    evaluation.return_value = {"evaluation_flags": flags}
    status = runner.run_one(77, output, tmp_path, "fixture-receipt")
    assert status == {"execution_status": "VALID", "evaluation_flags": flags, "complete": True, "reason": None}
    assert read_json(output / "status.json") == status
    assert read_json(output / "report.json")["WARNINGS"] == status
    assert not (output / "failure.json").exists()
    training.assert_called_once()
    export.assert_called_once()
    evaluation.assert_called_once()
    check_integrity(output)


def test_training_experimental_failure_remains_experimental_failure(runner_fixture, tmp_path):
    output, training, export, evaluation = runner_fixture
    training.side_effect = runner.ExperimentalFailure("non-finite loss fixture")
    status = runner.run_one(77, output, tmp_path, "fixture-receipt")
    assert status["execution_status"] == "EXPERIMENTAL_FAILURE"
    assert status["complete"] is True and status["evaluation_flags"] == []
    assert status["reason"] == "non-finite loss fixture"
    assert read_json(output / "status.json") == status
    assert read_json(output / "failure.json")["type"] == "ExperimentalFailure"
    training.assert_called_once()
    export.assert_not_called()
    evaluation.assert_not_called()
    check_integrity(output)


def test_training_technical_exception_remains_invalid(runner_fixture, tmp_path):
    output, training, export, evaluation = runner_fixture
    training.side_effect = RuntimeError("technical fixture")
    with pytest.raises(RuntimeError, match="technical fixture"):
        runner.run_one(77, output, tmp_path, "fixture-receipt")
    status = read_json(output / "status.json")
    assert status["execution_status"] == "INVALID"
    assert status["complete"] is False and status["evaluation_flags"] == []
    assert status["reason"] == "technical fixture"
    assert read_json(output / "failure.json")["type"] == "RuntimeError"
    training.assert_called_once()
    export.assert_not_called()
    evaluation.assert_not_called()
    check_integrity(output)


def test_rotation_metadata_explicitly_excludes_upper_bound(tmp_path):
    config = configuration()
    write_json(tmp_path / "configuration.json", config)
    saved = read_json(tmp_path / "configuration.json")
    assert saved["dataset"]["rotation_degrees"] == {"low": 0.0, "high": 360.0, "high_inclusive": False}
    assert saved["dataset"]["circle_rotation"] == 0.0
