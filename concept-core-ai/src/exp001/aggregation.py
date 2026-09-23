"""Experiment-only classification, with explicit eligibility and precedence."""
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import numpy as np
from .config import FORMAL_SEEDS, seeds_for
from .artifacts import check_integrity, read_json, write_json, new_directory


def aggregate_records(records):
    warnings = sorted({warning for r in records for flag, warning in
        (("BOOTSTRAP_CI_FAILED", "DISTANCE_CI_INCOMPLETE"), ("PIXEL_BASELINE_FAILED", "CONTROL_INCOMPLETE"))
        if flag in r.get("evaluation_flags", [])})
    result = {"classification": "NOT_EVALUATED", "warnings": warnings, "attributes": {},
              "formal_master_seeds": list(FORMAL_SEEDS), "runs": records}
    seeds = [r.get("master_seed") for r in records]
    commits = {r.get("git_commit") for r in records}
    versions = {r.get("numpy_version") for r in records}
    eligible = (len(records) == 5 and set(seeds) == set(FORMAL_SEEDS)
        and len(commits) == 1 and None not in commits and "" not in commits
        and len(versions) == 1 and None not in versions and "" not in versions
        and all(r.get("formal") is True and r.get("execution_status") in ("VALID", "EXPERIMENTAL_FAILURE")
                and r.get("seeds") == seeds_for(r["master_seed"]) for r in records))
    if not eligible:
        result["reason"] = "Formal seed set, non-INVALID status, provenance or common commit/NumPy requirement not met"
        return result
    result.update(git_commit=next(iter(commits)), numpy_version=next(iter(versions)))
    records = sorted(records, key=lambda r: r["master_seed"])
    result["runs"] = records
    for r in records:
        if any(f in r.get("evaluation_flags", []) for f in ("PROBE_FAILED", "DISTANCE_FAILED")):
            result.update(classification="INCONCLUSIVE", reason="Missing primary evidence")
            return result
        for attribute in ("color", "shape"):
            values = r.get("primary", {}).get(attribute, {})
            for key in ("initial_accuracy", "final_accuracy", "initial_contrast", "final_contrast"):
                value = values.get(key)
                if not isinstance(value, (int, float)) or not np.isfinite(value):
                    result.update(classification="INCONCLUSIVE", reason="Missing primary evidence")
                    return result
    for attribute in ("color", "shape"):
        values = [r["primary"][attribute] for r in records]
        # Use exact correct/total ratios when confusion matrices supply counts.
        # This preserves the approved 90/900 == .10 boundary without a tolerance.
        probe_delta = [float(Fraction(v["final_correct"], v["final_total"]) - Fraction(v["initial_correct"], v["initial_total"]))
                       if all(k in v for k in ("final_correct", "final_total", "initial_correct", "initial_total"))
                       else float(Decimal(str(v["final_accuracy"])) - Decimal(str(v["initial_accuracy"]))) for v in values]
        accuracy = [v["final_accuracy"] for v in values]
        initial_contrast = [v["initial_contrast"] for v in values]
        final_contrast = [v["final_contrast"] for v in values]
        distance_delta = [f-i for f, i in zip(final_contrast, initial_contrast)]
        p_count = int(np.count_nonzero(np.asarray(probe_delta) > 0))
        d_count = int(np.count_nonzero(np.asarray(final_contrast) > 0))
        medians = {"probe_delta": float(np.median(probe_delta)), "final_accuracy": float(np.median(accuracy)),
                   "distance_delta": float(np.median(distance_delta)), "final_contrast": float(np.median(final_contrast))}
        conditions = {"probe_positive_at_least_4": p_count >= 4,
            "median_probe_delta_at_least_010": medians["probe_delta"] >= 0.10,
            "median_final_accuracy_at_least_070": medians["final_accuracy"] >= 0.70,
            "final_contrast_positive_at_least_4": d_count >= 4,
            "median_distance_delta_positive": medians["distance_delta"] > 0}
        result["attributes"][attribute] = {"probe_delta": probe_delta, "final_accuracy": accuracy,
            "initial_contrast": initial_contrast, "final_contrast": final_contrast, "distance_delta": distance_delta,
            "probe_positive_count": p_count, "final_contrast_positive_count": d_count,
            "medians": medians, "conditions": conditions, "success": all(conditions.values()),
            "between_run_std_ddof0": {name: float(np.std(array, ddof=0)) for name, array in
                (("probe_delta", probe_delta), ("final_accuracy", accuracy), ("distance_delta", distance_delta))}}
    if any(v["success"] for v in result["attributes"].values()):
        result["classification"] = "SUCCESS"
    elif any(v["medians"]["probe_delta"] > 0 or v["medians"]["distance_delta"] > 0 for v in result["attributes"].values()):
        result["classification"] = "INCONCLUSIVE"
    else:
        result["classification"] = "NO_EVIDENCE"
    return result


def record_from_run(path):
    path = Path(path)
    config = read_json(path / "configuration.json")
    status = read_json(path / "status.json")
    record = {**{k: config.get(k) for k in ("master_seed", "git_commit", "numpy_version", "formal", "seeds", "run_id")},
              **status, "primary": {}, "path": str(path.resolve())}
    try:
        check_integrity(path)
        if not status.get("complete"):
            raise ValueError("Run did not complete")
    except (ValueError, OSError):
        record.update(execution_status="INVALID", integrity_error=True)
        return record
    evaluation_path = path / "evaluation" / "summary.json"
    if evaluation_path.exists():
        evaluation = read_json(evaluation_path)
        record["pixel_baseline_summary"] = evaluation.get("pixel", {})
        for attribute in ("color", "shape"):
            values = {}
            for state in ("initial", "final"):
                probe_path = path / "evaluation" / f"probe_{state}_{attribute}.json"
                distance_path = path / "evaluation" / f"distance_{state}.json"
                if probe_path.exists():
                    probe = read_json(probe_path)
                    values[f"{state}_accuracy"] = probe.get("test_accuracy")
                    if "test_confusion_matrix" in probe:
                        matrix = np.asarray(probe["test_confusion_matrix"])
                        if matrix.shape != (3, 3) or matrix.sum() != 900 or np.any(matrix < 0) or not np.equal(matrix, np.floor(matrix)).all():
                            record.update(execution_status="INVALID", metric_error="Invalid confusion matrix")
                            return record
                        correct, total = int(np.trace(matrix)), int(matrix.sum())
                        if values[f"{state}_accuracy"] != correct / total:
                            record.update(execution_status="INVALID", metric_error="Accuracy/count mismatch")
                            return record
                        values[f"{state}_correct"], values[f"{state}_total"] = correct, total
                if distance_path.exists():
                    stats = read_json(distance_path).get("metrics", {}).get("standardized", {}).get("statistics", {})
                    same = stats.get(f"same_{attribute}", {}).get("mean_distance")
                    different = stats.get(f"different_{attribute}", {}).get("mean_distance")
                    values[f"{state}_contrast"] = different-same if same is not None and different is not None else None
            record["primary"][attribute] = values
    return record


def aggregate_paths(paths, output):
    # Caller selects exactly which attempts to include; never choose a favorable rerun.
    records = [record_from_run(p) for p in paths]
    result = aggregate_records(records)
    output = new_directory(output)
    write_json(output / "baseline_manifest.json", {"experiment_id": "exp001",
        "formal_master_seeds": list(FORMAL_SEEDS), "git_commit": result.get("git_commit"),
        "numpy_version": result.get("numpy_version"), "runs": records})
    write_json(output / "aggregate_metrics.json", result)
    (output / "report.md").write_text("# Experiment-level report\n\n" + result["classification"] +
        "\n\nWarnings: " + ", ".join(result["warnings"]) +
        "\n\nMetrics, run variability and control summaries: aggregate_metrics.json\n", encoding="utf-8")
    return result
