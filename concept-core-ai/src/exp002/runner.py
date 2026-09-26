"""Independent Exp002 execution and saved-artifact evaluation; never classify a run."""
import os
from pathlib import Path
import traceback
import numpy as np
import torch
from exp001.runner import write_metadata, read_metadata
from exp001.model import Autoencoder, configure_precision
from exp001.training import ExperimentalFailure, load_checkpoint
from .config import ACTIVE_SPLITS, COLORS, SHAPES, FORMAL_SEEDS, SOURCE_COMMIT, configuration, seeds_for
from .data import generate_metadata, assign_splits, generate_images, split_indices, validate_splits, SplitDataset
from .training import train, extract_latent, make_loader
from .performance import Performance
from .artifacts import (new_directory, write_json, read_json, save_npz, inventory, environment,
                        implementation_fingerprint, check_integrity)
from .baseline import register_attempt, validate_runtime
from .reconstruction import reconstruction_metrics, sanity_ratios
from .evaluation import evaluate_classifier, pixel_features
from .distance import analyze_distance, bootstrap_draws
from .visualization import reconstruction_artifacts, pca_artifacts


def save_distance(result, output, state):
    for population, (i, j, category) in result.pop("pairs", {}).items():
        arrays = {"i": i, "j": j, "category": category}
        for kind, metrics in result["metrics"].items():
            arrays[f"{kind}_distance"] = metrics[population].pop("distances")
            if "bootstrap" in metrics[population]:
                boot = metrics[population]["bootstrap"]
                save_npz(output / f"bootstrap_{state}_{kind}_{population}.npz",
                    values=boot.pop("values"), statistic_order=np.asarray(boot["statistic_order"]))
        save_npz(output / f"pairs_{state}_{population}.npz", **arrays)
    write_json(output / f"distance_{state}.json", result)
    return result["flags"]


def _probe_summary(result):
    return {k: result[k] for k in ("seen_test", "heldout_test", "selected_C", "converged", "flag", "reason") if k in result}


def evaluate_saved(run, output):
    run = Path(run)
    config = read_json(run / "configuration.json")
    if any(config.get(k) != v for k, v in configuration().items()):
        raise ValueError("Saved scientific configuration is not Exp002")
    rows = read_metadata(run / "metadata.csv")
    validate_splits(rows, config["seeds"]["split_seed"])
    indices = split_indices(rows)
    with np.load(run / "split.npz", allow_pickle=False) as stored:
        if set(stored.files) != set(indices) or any(not np.array_equal(stored[s], indices[s]) for s in indices):
            raise ValueError("Saved split membership/order mismatch")
    labels = {s: {a: np.asarray([rows[i][a] for i in indices[s]]) for a in ("color", "shape")} for s in ACTIVE_SPLITS}
    sample_ids = {s: np.asarray([rows[i]["sample_id"] for i in indices[s]]) for s in ACTIVE_SPLITS}
    output = new_directory(output)
    draws = bootstrap_draws(config["seeds"]["analysis_seed"])
    save_npz(output / "bootstrap_indices.npz", **draws, seen_sample_ids=sample_ids["seen_test"],
             heldout_sample_ids=sample_ids["heldout_test"])
    flags, summary = [], {"probe": {}, "distance": {}, "pixel": {}, "derived": {}}
    for state in ("initial", "final"):
        latent = {}
        for split in ACTIVE_SPLITS:
            with np.load(run / "latent" / f"{state}_{split}.npz", allow_pickle=False) as stored:
                if not np.array_equal(stored["sample_ids"], sample_ids[split]) or stored["latent"].shape != (len(indices[split]), 32):
                    raise ValueError("Saved latent identity/shape mismatch")
                latent[split] = stored["latent"].copy()
        summary["probe"][state] = {}
        for attribute, classes in (("color", COLORS), ("shape", SHAPES)):
            result = evaluate_classifier(latent, {s: labels[s][attribute] for s in ACTIVE_SPLITS}, classes, config["seeds"]["probe_seed"])
            write_json(output / f"probe_{state}_{attribute}.json", result)
            summary["probe"][state][attribute] = _probe_summary(result)
            if "flag" in result:
                flags.append(result["flag"])
        distance = analyze_distance(latent["train"], latent["seen_test"], latent["heldout_test"],
                                    labels, sample_ids, config["seeds"]["analysis_seed"], draws)
        summary["distance"][state] = {kind: values["cross"]["contrast"] for kind, values in distance["metrics"].items()}
        flags.extend(save_distance(distance, output, state))
        # Exploratory PCA only; no Held-out fitting is used by probes/distances.
        for split in ("seen_test", "heldout_test"):
            if np.isfinite(latent[split]).all():
                pca_artifacts(latent[split], sample_ids[split], labels[split], output / f"pca_{state}_{split}")
    images = np.load(run / "images.npy", mmap_mode="r", allow_pickle=False)
    if images.shape != (9000, 64, 64, 3) or images.dtype != np.float32:
        raise ValueError("Image artifact shape/precision mismatch")
    for kind in ("simple_image_statistics", "raw_pixel_linear"):
        features = {s: np.concatenate([pixel_features(images[indices[s][start:start+128]], kind)
                    for start in range(0, len(indices[s]), 128)]) for s in ACTIVE_SPLITS}
        summary["pixel"][kind] = {}
        for attribute, classes in (("color", COLORS), ("shape", SHAPES)):
            result = evaluate_classifier(features, {s: labels[s][attribute] for s in ACTIVE_SPLITS}, classes,
                                         config["seeds"]["probe_seed"], "PIXEL_BASELINE_FAILED")
            write_json(output / f"pixel_{kind}_{attribute}.json", result)
            summary["pixel"][kind][attribute] = _probe_summary(result)
            if "flag" in result:
                flags.append(result["flag"])
        del features
    for attribute in ("color", "shape"):
        derived = {}
        for split, prefix in (("seen_test", "seen"), ("heldout_test", "heldout")):
            a = summary["probe"]["initial"][attribute].get(split, {}).get("accuracy")
            b = summary["probe"]["final"][attribute].get(split, {}).get("accuracy")
            derived[f"{prefix}_probe_delta"] = b-a if a is not None and b is not None else None
        for state in ("initial", "final"):
            probe = summary["probe"][state][attribute]
            a, b = probe.get("seen_test", {}).get("accuracy"), probe.get("heldout_test", {}).get("accuracy")
            derived[f"{state}_generalization_gap"] = a-b if a is not None and b is not None else None
        a = summary["distance"]["initial"].get("standardized", {}).get(attribute)
        b = summary["distance"]["final"].get("standardized", {}).get(attribute)
        derived["cross_distance_delta"] = b-a if a is not None and b is not None else None
        summary["derived"][attribute] = derived
    summary["evaluation_flags"] = sorted(set(flags))
    write_json(output / "summary.json", summary)
    return summary


def export_states(model, images, datasets, indices, rows, loader_seed, output, device="cpu", performance=None):
    output = Path(output)
    latent_dir = new_directory(output / "latent")
    metrics = {"zero": {}}
    for state in ("initial", "final"):
        checkpoint = load_checkpoint(model, output / f"{state}.pt", device)
        if checkpoint["epoch"] != (0 if state == "initial" else 50):
            raise ValueError("Checkpoint violates initial/final semantics")
        metrics[state] = {}
        for split in ACTIVE_SPLITS:
            values = extract_latent(model, datasets[split], loader_seed, device, performance)
            save_npz(latent_dir / f"{state}_{split}.npz", latent=values,
                     sample_ids=np.asarray([rows[i]["sample_id"] for i in indices[split]]))
            if split in ("seen_test", "heldout_test"):
                loader = make_loader(datasets[split], loader_seed, performance=performance)
                metrics[state][split] = reconstruction_metrics(model, loader, device)
                if state == "initial":
                    metrics["zero"][split] = reconstruction_metrics(None, loader, device)
    metrics["sanity_inputs"] = sanity_ratios(metrics["final"]["seen_test"], metrics["zero"]["seen_test"])
    write_json(output / "reconstruction_metrics.json", metrics)
    reconstruction_artifacts(model, images, rows, output, device)
    return metrics


def _execute_attempt(config, output, receipt, performance):
    """Shared orchestration seam; tests supply explicitly non-formal fixture config."""
    output = new_directory(output)
    status = {"execution_status": "INVALID", "evaluation_flags": [], "complete": False,
              "reason": "An interrupted attempt remains INVALID"}
    write_json(output / "configuration.json", config)
    write_json(output / "verification.json", receipt)
    write_json(output / "status.json", status)
    try:
        rows = assign_splits(generate_metadata(config["seeds"]["generation_seed"]), config["seeds"]["split_seed"])
        write_metadata(output / "metadata.csv", rows)
        indices = split_indices(rows)
        save_npz(output / "split.npz", **indices)
        images = generate_images(rows, output / "images.npy")
        datasets = {s: SplitDataset(images, rows, indices[s], s) for s in ACTIVE_SPLITS}
        model = Autoencoder(config["seeds"]["model_seed"])
        config["parameter_count"] = sum(p.numel() for p in model.parameters())
        write_json(output / "configuration.json", config, replace=True)
        train(model, datasets["train"], datasets["validation"], config["seeds"]["loader_seed"], output, config["device"], performance)
        export_states(model, images, datasets, indices, rows, config["seeds"]["loader_seed"], output, config["device"], performance)
        evaluation = evaluate_saved(output, output / "evaluation")
        status.update(execution_status="VALID", evaluation_flags=evaluation["evaluation_flags"], complete=True, reason=None)
    except ExperimentalFailure as exc:
        status.update(execution_status="EXPERIMENTAL_FAILURE", complete=True, reason=str(exc))
        write_json(output / "failure.json", {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
    except BaseException as exc:
        status.update(execution_status="INVALID", complete=False, reason=str(exc))
        write_json(output / "failure.json", {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
        raise
    finally:
        write_json(output / "status.json", status, replace=True)
        write_json(output / "report.json", {"OBSERVATIONS": "Execution and measurements only; classification is experiment-level.",
            "METRICS": ["training.csv", "reconstruction_metrics.json", "evaluation/summary.json"], "WARNINGS": status,
            "ARTIFACTS": sorted(inventory(output)), "formal": config["formal"]})
        write_json(output / "integrity.json", inventory(output))
    return status


def run_one(master_seed, output, root, baseline, attempt_id, retry_of=None, retry_reason=None):
    if master_seed not in FORMAL_SEEDS:
        raise ValueError("Formal execution requires an approved master seed")
    manifest = validate_runtime(root, baseline)
    perf = Performance(**manifest["frozen_performance"])
    registration = register_attempt(baseline, master_seed, attempt_id, output, retry_of, retry_reason)
    perf.apply()
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    configure_precision()
    config = {**configuration(), "run_id": Path(output).name, "formal": True, "master_seed": master_seed,
        "seeds": seeds_for(master_seed), "git_commit": manifest["execution_commit"],
        "canonical_source_commit": SOURCE_COMMIT, "environment": manifest["required_environment"],
        "performance": perf.as_dict(), "device": manifest["device"], "device_class": manifest["device_class"],
        "implementation": manifest["implementation"], "baseline_id": manifest["baseline_id"],
        "baseline_version": manifest["baseline_version"], "baseline_manifest_hash": manifest["manifest_hash"],
        "verification_receipt_sha256": manifest["verification"]["sha256"], "attempt_id": attempt_id,
        "attempt_kind": registration["attempt_kind"],
        "parent_canonical_attempt_id": registration["parent_canonical_attempt_id"]}
    return _execute_attempt(config, output, manifest["verification"]["receipt"], perf)


def reanalyze(run, output, root):
    check_integrity(run)
    config = read_json(Path(run) / "configuration.json")
    if config["environment"] != environment() or config["implementation"] != implementation_fingerprint(root):
        raise ValueError("Reanalysis requires the original environment and implementation")
    Performance(**config["performance"]).apply()
    result = evaluate_saved(run, output)
    write_json(Path(output) / "provenance.json", {"source_run": str(Path(run).resolve()), "source_configuration": config})
    write_json(Path(output) / "integrity.json", inventory(output))
    return result
