from copy import deepcopy
import numpy as np
import pytest
from exp001.evaluation import TrainScaler, select_classifier, pixel_features
from exp002 import evaluation
from exp002.config import ACTIVE_SPLITS


def probe_fixture():
    rng = np.random.Generator(np.random.PCG64(75))
    labels = {s: np.tile(["red", "green", "blue"], 8) for s in ACTIVE_SPLITS}
    features = {s: np.tile(np.eye(3), (8, 1)) + rng.normal(0, .05, (24, 3)) for s in ACTIVE_SPLITS}
    for s in features:
        features[s] = np.column_stack([features[s], np.zeros(24), np.arange(24)*1e-12])
    return features, labels


def test_seen_only_scaler_fit_selection_and_heldout_is_evaluation_only(monkeypatch):
    features, labels = probe_fixture()
    calls = []
    def selection(train, y, val, vy, seed):
        calls.append((train.copy(), y.copy(), val.copy(), vy.copy()))
        return select_classifier(train, y, val, vy, seed)
    monkeypatch.setattr(evaluation, "select_classifier", selection)
    before = deepcopy(features)
    result = evaluation.evaluate_classifier(features, labels, ("red", "green", "blue"), 76)
    changed, changed_labels = deepcopy(features), deepcopy(labels)
    changed["heldout_test"] = np.full_like(changed["heldout_test"], 12345.)
    changed_labels["heldout_test"] = np.roll(changed_labels["heldout_test"], 1)
    changed["seen_test"] *= -1e3
    again = evaluation.evaluate_classifier(changed, changed_labels, ("red", "green", "blue"), 76)
    for key in ("coefficients", "intercept"):
        np.testing.assert_array_equal(result[key], again[key])
    assert result["selected_C"] == again["selected_C"]
    assert result["candidates"] == again["candidates"]
    for x, y in zip(calls[0], calls[1]): np.testing.assert_array_equal(x, y)
    np.testing.assert_array_equal(result["scaler"]["mean"], features["train"].mean(0))
    np.testing.assert_array_equal(result["scaler"]["std"], features["train"].std(0, ddof=0))
    assert result["scaler"]["keep"].tolist() == [True, True, True, False, False]
    assert result["scaler"]["fit_split"] == "seen_train"
    assert result["converged"] and len(result["candidates"]) == 5
    for split in ("seen_test", "heldout_test"):
        assert result[split]["confusion_matrix"].shape == (3, 3)
        assert result[split]["confusion_matrix"].sum() == 24
        assert result[split]["accuracy"] == result[split]["balanced_accuracy"] == 1
    for split in ACTIVE_SPLITS: np.testing.assert_array_equal(features[split], before[split])


def test_train_scaler_std_boundary_and_initial_final_independence():
    a = TrainScaler.fit(np.array([[-1e-8, -1e-9, -1], [1e-8, 1e-9, 1]]))
    assert a.keep.tolist() == [True, False, True]
    b = TrainScaler.fit(np.array([[-2e-8, -2e-9, -2], [2e-8, 2e-9, 2]]))
    assert not np.array_equal(a.std, b.std)
    unchanged = a.mean.copy()
    a.transform(np.full((300, 3), 1e12))
    np.testing.assert_array_equal(a.mean, unchanged)


@pytest.mark.parametrize("failure_flag", ["PROBE_FAILED", "PIXEL_BASELINE_FAILED"])
def test_no_converged_classifier_and_nonfinite_flags(monkeypatch, failure_flag):
    features, labels = probe_fixture()
    monkeypatch.setattr(evaluation, "select_classifier", lambda *args: (None, [{"converged": False}]))
    r = evaluation.evaluate_classifier(features, labels, ("red", "green", "blue"), 78, failure_flag)
    assert r["flag"] == failure_flag and not r["converged"]
    features["heldout_test"][:] = np.nan
    r = evaluation.evaluate_classifier(features, labels, ("red", "green", "blue"), 78, failure_flag)
    assert r["flag"] == failure_flag


def test_reserved_argument_is_rejected():
    features, labels = probe_fixture()
    features["reserved"] = features["train"]
    with pytest.raises(ValueError, match="Reserved"):
        evaluation.evaluate_classifier(features, labels, ("red", "green", "blue"), 77)


def test_pixel_controls_are_exact_inherited_implementation():
    assert evaluation.pixel_features is pixel_features
    image = np.zeros((2, 64, 64, 3), dtype=np.float32)
    image[:, :2, :3, 0] = 230
    assert pixel_features(image, "simple_image_statistics").shape == (2, 7)
    raw = pixel_features(image, "raw_pixel_linear")
    assert raw.shape == (2, 12288)
    assert raw.max() == 230/255
