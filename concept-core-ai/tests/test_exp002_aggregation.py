from copy import deepcopy
import numpy as np
import pytest
from exp002.aggregation import aggregate_records, reconstruction_gate, record_from_run
from exp002.config import FORMAL_SEEDS, seeds_for
from exp002.performance import Performance


def records002():
    # In-memory classification fixtures only. No formal seed artifacts or runs.
    environment = {"python": "3.12.fixture", "platform": "synthetic-fixture", "packages": {
        p: "fixture" for p in ("numpy", "torch", "scipy", "scikit-learn", "matplotlib", "threadpoolctl")}}
    return [{"experiment_id": "exp002", "master_seed": seed, "formal": True, "complete": True,
        "execution_status": "VALID", "evaluation_flags": [], "git_commit": "synthetic-fixture", "seeds": seeds_for(seed),
        "environment": deepcopy(environment), "performance": Performance().as_dict(), "device_class": "cpu",
        "reconstruction_sanity": {"balanced_ratio": .8, "foreground_ratio": .8},
        "primary": {a: {"initial_accuracy": .65, "final_accuracy": .70, "initial_contrast": 0., "final_contrast": .1}
                    for a in ("color", "shape")}} for seed in FORMAL_SEEDS]


def test_exact_five_seed_success_boundaries_and_fraction_counts():
    records = records002()
    for r in records:
        for p in r["primary"].values():
            p.update(initial_correct=195, initial_total=300, final_correct=210, final_total=300)
    result = aggregate_records(records)
    assert result["classification"] == "SUCCESS" and result["step"] == 5
    assert result["attributes"]["color"]["medians"]["heldout_probe_delta"] == .05
    assert result["reconstruction_gate"]["passed"]
    assert result == aggregate_records(list(reversed(records)))


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "invalid", "incomplete", "nonformal", "commit", "python", "numpy", "device", "workers", "threads", "missing_environment", "seed_namespace"])
def test_formal_set_validity_has_first_precedence(mutation):
    records = records002()
    records[0]["execution_status"] = "EXPERIMENTAL_FAILURE"
    r = records[-1]
    if mutation == "missing": records.pop()
    elif mutation == "duplicate": records[-1] = deepcopy(records[0])
    elif mutation == "invalid": r["execution_status"] = "INVALID"
    elif mutation == "incomplete": r["complete"] = False
    elif mutation == "nonformal": r["formal"] = False
    elif mutation == "commit": r["git_commit"] = "other"
    elif mutation == "python": r["environment"]["python"] = "other"
    elif mutation == "numpy": r["environment"]["packages"]["numpy"] = "other"
    elif mutation == "device": r["device_class"] = "cuda"
    elif mutation == "workers": r["performance"]["num_workers"] = 1
    elif mutation == "threads": r["performance"]["torch_threads"] = 2
    elif mutation == "missing_environment": r.pop("environment")
    elif mutation == "seed_namespace":
        from exp001.config import seeds_for as old
        r["seeds"] = old(r["master_seed"])
    result = aggregate_records(records)
    assert result["classification"] == "NOT_EVALUATED" and result["step"] == 1


def test_experimental_failure_precedes_missing_evidence_and_gate():
    records = records002()
    records[0]["execution_status"] = "EXPERIMENTAL_FAILURE"
    records[1]["primary"] = {}
    records[2]["evaluation_flags"] = ["PROBE_FAILED"]
    records[3]["reconstruction_sanity"]["balanced_ratio"] = 50
    result = aggregate_records(records)
    assert result["classification"] == "INCONCLUSIVE" and result["step"] == 2


@pytest.mark.parametrize("bad", ["PROBE_FAILED", "DISTANCE_FAILED", "missing", "nan", "inf"])
def test_missing_required_primary_evidence(bad):
    records = records002()
    if bad in ("PROBE_FAILED", "DISTANCE_FAILED"): records[0]["evaluation_flags"] = [bad]
    elif bad == "missing": records[0]["primary"]["color"].pop("final_contrast")
    else: records[0]["primary"]["color"]["final_accuracy"] = float(bad)
    result = aggregate_records(records)
    assert result["classification"] == "INCONCLUSIVE" and result["step"] == 3
    assert records[0]["execution_status"] == "VALID"


@pytest.mark.parametrize("name", ["balanced_ratio", "foreground_ratio"])
@pytest.mark.parametrize("values,passed", [([.8]*5, True), ([.8]*4+[1.0], True), ([.8]*3+[1.0]*2, False),
    ([float(np.nextafter(.8, 1.))]*5, False), ([float(np.nextafter(.8, 0.))]*5, True), ([None]*5, False), ([float("inf")]*5, False)])
def test_reconstruction_gate_exact_boundaries(name, values, passed):
    records = records002()
    for r, v in zip(records, values): r["reconstruction_sanity"][name] = v
    assert reconstruction_gate(records)["passed"] is passed
    result = aggregate_records(records)
    assert result["classification"] == ("SUCCESS" if passed else "INCONCLUSIVE")
    assert result["step"] == (5 if passed else 4)


@pytest.mark.parametrize("condition", ["four_positive", "three_positive", "below_delta", "below_accuracy", "zero_final_contrast", "zero_distance_delta"])
def test_success_exact_thresholds(condition):
    records = records002()
    for attribute in ("color", "shape"):
        if condition in ("four_positive", "three_positive"):
            for r in records[4 if condition == "four_positive" else 3:]:
                r["primary"][attribute].update(initial_accuracy=.70, final_contrast=0)
        else:
            for r in records:
                v = r["primary"][attribute]
                if condition == "below_delta": v.update(initial_accuracy=.7000000000000001, final_accuracy=.75)
                elif condition == "below_accuracy": v.update(initial_accuracy=.64, final_accuracy=.6999999999999999)
                elif condition == "zero_final_contrast": v.update(initial_contrast=-.1, final_contrast=0.)
                elif condition == "zero_distance_delta": v.update(initial_contrast=.1)
    result = aggregate_records(records)
    assert result["classification"] == ("SUCCESS" if condition == "four_positive" else "INCONCLUSIVE")


@pytest.mark.parametrize("trend", ["probe", "distance", "none"])
def test_positive_direction_else_no_evidence(trend):
    records = records002()
    for r in records:
        for v in r["primary"].values():
            v.update(initial_accuracy=.70, final_accuracy=.71 if trend == "probe" else .70,
                     initial_contrast=0, final_contrast=.01 if trend == "distance" else 0)
    result = aggregate_records(records)
    assert result["classification"] == ("NO_EVIDENCE" if trend == "none" else "INCONCLUSIVE")
    assert result["step"] == (7 if trend == "none" else 6)


@pytest.mark.parametrize("classification", ["SUCCESS", "INCONCLUSIVE", "NO_EVIDENCE"])
def test_secondary_flags_do_not_block_classification(classification):
    records = records002()
    for r in records:
        r["evaluation_flags"] = ["BOOTSTRAP_CI_FAILED", "PIXEL_BASELINE_FAILED"]
        if classification != "SUCCESS":
            for v in r["primary"].values():
                v.update(initial_accuracy=.70, final_accuracy=.71 if classification == "INCONCLUSIVE" else .70,
                         initial_contrast=.1)
    result = aggregate_records(records)
    assert result["classification"] == classification
    assert result["warnings"] == ["CONTROL_INCOMPLETE", "DISTANCE_CI_INCOMPLETE"]


def test_one_successful_attribute_suffices():
    records = records002()
    for r in records:
        r["primary"]["shape"].update(initial_accuracy=.70, initial_contrast=.1)
    result = aggregate_records(records)
    assert result["classification"] == "SUCCESS"
    assert not result["attributes"]["shape"]["success"]


def test_missing_artifact_set_is_invalid(tmp_path):
    assert record_from_run(tmp_path)["execution_status"] == "INVALID"
