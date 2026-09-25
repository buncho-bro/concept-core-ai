"""Seven-step Exp002 precedence; only this module classifies experiments."""
from fractions import Fraction
import json
from pathlib import Path
import numpy as np
from .config import FORMAL_SEEDS, SOURCE_COMMIT, configuration, seeds_for
from .performance import Performance
from .artifacts import check_integrity, read_json, write_json, new_directory, inventory
from .reconstruction import sanity_ratios


def _finite(value):
    return type(value) in (int, float) and np.isfinite(value)


def reconstruction_gate(records):
    result = {"passed": False, "conditions": {}, "ratios": {}}
    for name in ("balanced_ratio", "foreground_ratio"):
        values = [r.get("reconstruction_sanity", {}).get(name) for r in records]
        if len(values) != 5 or not all(_finite(v) and v >= 0 for v in values):
            result["reason"] = "Missing/non-finite reconstruction sanity evidence"
            return result
        result["ratios"][name] = values
        result["conditions"][f"{name}_below_one_at_least_four"] = sum(v < 1.0 for v in values) >= 4
        result["conditions"][f"{name}_median_at_most_080"] = bool(np.median(values) <= 0.80)
    result["passed"] = all(result["conditions"].values())
    return result


def _same_required_environment(records):
    for r in records:
        env = r.get("environment")
        perf = r.get("performance")
        if (not isinstance(env, dict) or not all(env.get(k) for k in ("python", "platform", "packages"))
                or not isinstance(perf, dict) or not r.get("device_class")):
            return False
        if not all(env["packages"].get(k) for k in ("numpy", "torch", "scipy", "scikit-learn", "matplotlib", "threadpoolctl")):
            return False
        try:
            if Performance(**perf).as_dict() != perf:
                return False
        except (ValueError, TypeError):
            return False
    return len({json.dumps({k: r[k] for k in ("environment", "performance", "device_class")}, sort_keys=True)
                for r in records}) == 1


def _accuracy(v, state):
    if f"{state}_correct" in v and f"{state}_total" in v:
        return Fraction(v[f"{state}_correct"], v[f"{state}_total"])
    return Fraction(str(v[f"{state}_accuracy"]))


def aggregate_records(records):
    warnings = sorted({warning for r in records for flag, warning in
        (("BOOTSTRAP_CI_FAILED", "DISTANCE_CI_INCOMPLETE"), ("PIXEL_BASELINE_FAILED", "CONTROL_INCOMPLETE"))
        if flag in r.get("evaluation_flags", [])})
    result = {"classification": "NOT_EVALUATED", "warnings": warnings, "attributes": {},
              "formal_master_seeds": list(FORMAL_SEEDS), "runs": records}
    commits = {r.get("git_commit") for r in records}
    eligible = (len(records) == 5 and {r.get("master_seed") for r in records} == set(FORMAL_SEEDS)
        and len(commits) == 1 and None not in commits and "" not in commits
        and all(r.get("experiment_id") == "exp002" and r.get("formal") is True and r.get("complete") is True
                and r.get("execution_status") in ("VALID", "EXPERIMENTAL_FAILURE")
                and r.get("seeds") == seeds_for(r["master_seed"]) for r in records)
        and _same_required_environment(records))
    if not eligible:
        return {**result, "step": 1, "reason": "Formal set, execution status, commit or required environment invalid"}
    records = sorted(records, key=lambda r: r["master_seed"])
    result.update(runs=records, git_commit=next(iter(commits)))
    if any(r["execution_status"] == "EXPERIMENTAL_FAILURE" for r in records):
        return {**result, "classification": "INCONCLUSIVE", "step": 2, "reason": "Scientific/numerical run failure"}
    for r in records:
        if any(f in r.get("evaluation_flags", []) for f in ("PROBE_FAILED", "DISTANCE_FAILED")):
            return {**result, "classification": "INCONCLUSIVE", "step": 3, "reason": "Missing primary evidence"}
        for attribute in ("color", "shape"):
            values = r.get("primary", {}).get(attribute, {})
            if not all(_finite(values.get(k)) for k in ("initial_accuracy", "final_accuracy", "initial_contrast", "final_contrast")):
                return {**result, "classification": "INCONCLUSIVE", "step": 3, "reason": "Missing/non-finite primary evidence"}
    gate = reconstruction_gate(records)
    result["reconstruction_gate"] = gate
    if not gate["passed"]:
        return {**result, "classification": "INCONCLUSIVE", "step": 4, "reason": "Reconstruction sanity gate failed"}
    for attribute in ("color", "shape"):
        values = [r["primary"][attribute] for r in records]
        accuracy = [_accuracy(v, "final") for v in values]
        probe_delta = [_accuracy(v, "final") - _accuracy(v, "initial") for v in values]
        final_contrast = [v["final_contrast"] for v in values]
        distance_delta = [v["final_contrast"] - v["initial_contrast"] for v in values]
        mp, ma, md = sorted(probe_delta)[2], sorted(accuracy)[2], sorted(distance_delta)[2]
        conditions = {"probe_positive_at_least_four": sum(v > 0 for v in probe_delta) >= 4,
            "median_heldout_delta_at_least_005": mp >= Fraction(1, 20),
            "median_final_heldout_accuracy_at_least_070": ma >= Fraction(7, 10),
            "final_cross_contrast_positive_at_least_four": sum(v > 0 for v in final_contrast) >= 4,
            "median_cross_distance_delta_positive": md > 0}
        arrays = {"heldout_probe_delta": list(map(float, probe_delta)), "final_heldout_accuracy": list(map(float, accuracy)),
                  "final_cross_contrast": final_contrast, "cross_distance_delta": distance_delta}
        result["attributes"][attribute] = {**arrays, "conditions": conditions, "success": all(conditions.values()),
            "medians": {"heldout_probe_delta": float(mp), "final_heldout_accuracy": float(ma), "cross_distance_delta": md},
            "between_run_std_ddof0": {k: float(np.std(v, ddof=0)) for k, v in arrays.items()}}
    if any(a["success"] for a in result["attributes"].values()):
        result.update(classification="SUCCESS", step=5)
    elif any(a["medians"]["heldout_probe_delta"] > 0 or a["medians"]["cross_distance_delta"] > 0 for a in result["attributes"].values()):
        result.update(classification="INCONCLUSIVE", step=6)
    else:
        result.update(classification="NO_EVIDENCE", step=7)
    return result


def record_from_run(path):
    path = Path(path)
    record = {"path": str(path.resolve()), "execution_status": "INVALID", "primary": {}}
    try:
        check_integrity(path)
        config, status = read_json(path / "configuration.json"), read_json(path / "status.json")
        record.update({k: config.get(k) for k in ("experiment_id", "master_seed", "git_commit", "formal", "seeds",
                                                "run_id", "environment", "performance", "device_class")})
        record.update(status)
        if any(config.get(k) != v for k, v in configuration().items()) or config.get("canonical_source_commit") != SOURCE_COMMIT:
            raise ValueError("Scientific configuration/source mismatch")
        if not status.get("complete"):
            raise ValueError("Incomplete attempt")
        if status["execution_status"] == "EXPERIMENTAL_FAILURE":
            return record
        if (path / "reconstruction_metrics.json").exists():
            recon = read_json(path / "reconstruction_metrics.json")
            record["reconstruction_sanity"] = sanity_ratios(recon["final"]["seen_test"], recon["zero"]["seen_test"])
        for attribute in ("color", "shape"):
            values = {}
            for state in ("initial", "final"):
                pp = path / "evaluation" / f"probe_{state}_{attribute}.json"
                dp = path / "evaluation" / f"distance_{state}.json"
                if pp.exists():
                    test = read_json(pp).get("heldout_test", {})
                    values[f"{state}_accuracy"] = test.get("accuracy")
                    if "confusion_matrix" in test:
                        matrix = np.asarray(test["confusion_matrix"])
                        if matrix.shape != (3, 3) or matrix.sum() != 300 or np.any(matrix < 0) or not np.equal(matrix, np.floor(matrix)).all():
                            raise ValueError("Malformed Held-out confusion matrix")
                        correct = int(np.trace(matrix))
                        if test.get("accuracy") != correct / 300:
                            raise ValueError("Accuracy/count mismatch")
                        values.update({f"{state}_correct": correct, f"{state}_total": 300})
                if dp.exists():
                    stats = read_json(dp).get("metrics", {}).get("standardized", {}).get("cross", {}).get("statistics", {})
                    same = stats.get(f"same_{attribute}", {}).get("mean_distance")
                    different = stats.get(f"different_{attribute}", {}).get("mean_distance")
                    values[f"{state}_contrast"] = different - same if _finite(same) and _finite(different) else None
            record["primary"][attribute] = values
        if (path / "evaluation" / "summary.json").exists():
            summary = read_json(path / "evaluation" / "summary.json")
            record["pixel_baseline_summary"] = summary.get("pixel", {})
            if summary.get("evaluation_flags") != status.get("evaluation_flags"):
                raise ValueError("Status/summary flags differ")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        record.update(execution_status="INVALID", integrity_error=str(exc))
    return record


def aggregate_paths(paths, output):
    records = [record_from_run(p) for p in paths]
    result = aggregate_records(records)
    output = new_directory(output)
    write_json(output / "baseline_manifest.json", {"experiment_id": "exp002", "formal_master_seeds": list(FORMAL_SEEDS),
                                                  "git_commit": result.get("git_commit"), "runs": records})
    write_json(output / "aggregate_metrics.json", result)
    (output / "report.md").write_text("# Experiment 002 aggregate\n\n" + result["classification"] +
        "\n\nWarnings: " + ", ".join(result["warnings"]) + "\n\nSee aggregate_metrics.json for observations, metrics and gate.\n", encoding="utf-8")
    write_json(output / "integrity.json", inventory(output))
    return result
