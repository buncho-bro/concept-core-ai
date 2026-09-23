"""Artifact-first formal execution; all scientific classification lives elsewhere."""
import csv
import os
from pathlib import Path
import traceback
import numpy as np
import torch
from .config import COLORS, SHAPES, SPLITS, NUMPY_VERSION, FORMAL_SEEDS, SOURCE_COMMIT, configuration, seeds_for
from .artifacts import (new_directory, write_json, read_json, save_npz, inventory, environment,
                        implementation_fingerprint, clean_commit, check_integrity)
from .data import generate_metadata, assign_splits, generate_images, split_indices, ImageDataset
from .model import Autoencoder, configure_precision
from .training import train, load_checkpoint, extract_latent, reconstruction_loss, make_loader, ExperimentalFailure
from .evaluation import evaluate_classifier, pixel_features
from .distance import analyze_distance
from .visualization import pca_artifacts, reconstruction_artifact


def write_metadata(path, rows):
    with Path(path).open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_metadata(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for r in rows:
        for key in ("sample_id", "x", "y", "size", "r", "g", "b", "generation_seed"):
            r[key] = int(r[key])
        r["rotation"] = float(r["rotation"])
    return rows


def save_distance(result, output, state):
    if "flag" in result:
        write_json(output / f"distance_{state}.json", result)
        return [result["flag"]]
    pair_arrays = {key: result.pop(key) for key in ("sample_ids", "pair_i", "pair_j", "category")}
    for kind, values in result["metrics"].items():
        boot = values["bootstrap"]
        save_npz(output / f"bootstrap_{state}_{kind}.npz", indices=boot.pop("indices"), means=boot.pop("means"),
                 sample_ids=pair_arrays["sample_ids"], group_order=np.asarray(boot["group_order"]))
        pair_arrays[f"{kind}_distance"] = values.pop("distances")
    save_npz(output / f"pairs_{state}.npz", **pair_arrays)
    write_json(output / f"distance_{state}.json", result)
    return result["flags"]


def evaluate_saved(run, output):
    """Reanalyze saved latent and image artifacts without executing the encoder."""
    run, output = Path(run), new_directory(output)
    config = read_json(run / "configuration.json")
    rows = read_metadata(run / "metadata.csv")
    indices = split_indices(rows)
    labels = {a: {s: np.array([rows[i][a] for i in indices[s]]) for s in SPLITS} for a in ("color", "shape")}
    flags, summary = [], {"probe": {}, "distance": {}, "pixel": {}}
    for state in ("initial", "final"):
        latent = {}
        for split in SPLITS:
            with np.load(run / "latent" / f"{state}_{split}.npz", allow_pickle=False) as stored:
                expected_ids = np.array([rows[i]["sample_id"] for i in indices[split]])
                if not np.array_equal(stored["sample_ids"], expected_ids):
                    raise ValueError("Saved latent sample order mismatch")
                latent[split] = stored["latent"].copy()
        test_ids = np.array([rows[i]["sample_id"] for i in indices["test"]])
        pca_artifacts(latent["test"], test_ids, {a: labels[a]["test"] for a in labels}, output / f"pca_{state}")
        summary["probe"][state] = {}
        for attribute, classes in (("color", COLORS), ("shape", SHAPES)):
            result = evaluate_classifier(latent, labels[attribute], classes, config["seeds"]["probe_seed"])
            write_json(output / f"probe_{state}_{attribute}.json", result)
            summary["probe"][state][attribute] = {key: result[key] for key in ("test_accuracy", "selected_C", "flag") if key in result}
            if "flag" in result:
                flags.append(result["flag"])
        distance = analyze_distance(latent["train"], latent["test"], labels["color"]["test"], labels["shape"]["test"],
                                    test_ids, config["seeds"]["analysis_seed"])
        summary["distance"][state] = {kind: v["contrast"] for kind, v in distance.get("metrics", {}).items()}
        flags.extend(save_distance(distance, output, state))
    images = np.load(run / "images.npy", mmap_mode="r", allow_pickle=False)
    for kind in ("simple_image_statistics", "raw_pixel_linear"):
        # Calculate split features in chunks to avoid a full float64 image duplicate.
        features = {}
        for split, ids in indices.items():
            features[split] = np.concatenate([pixel_features(images[ids[start:start+128]], kind)
                                              for start in range(0, len(ids), 128)])
        summary["pixel"][kind] = {}
        for attribute, classes in (("color", COLORS), ("shape", SHAPES)):
            result = evaluate_classifier(features, labels[attribute], classes, config["seeds"]["probe_seed"], "PIXEL_BASELINE_FAILED")
            write_json(output / f"pixel_{kind}_{attribute}.json", result)
            summary["pixel"][kind][attribute] = {key: result[key] for key in ("test_accuracy", "test_balanced_accuracy", "selected_C", "flag") if key in result}
            if "flag" in result:
                flags.append(result["flag"])
        del features
    summary["evaluation_flags"] = sorted(set(flags))
    write_json(output / "summary.json", summary)
    return summary


def require_verification(root, receipt_path):
    receipt = read_json(receipt_path)
    if receipt.get("exit_code") != 0 or receipt.get("implementation") != implementation_fingerprint(root):
        raise ValueError("Successful verification of this implementation is required")
    if receipt.get("environment") != environment():
        raise ValueError("Verification environment does not match runtime")
    return receipt


def export_states(model, datasets, indices, rows, loader_seed, output, device="cpu"):
    """Save all six latent states and reconstruction losses in fixed sample order."""
    output = Path(output)
    latent_dir = new_directory(output / "latent")
    losses = {}
    for state in ("initial", "final"):
        checkpoint = load_checkpoint(model, output / f"{state}.pt", device)
        if checkpoint["epoch"] != (0 if state == "initial" else 50):
            raise ValueError("Checkpoint epoch violates approved initial/final semantics")
        losses[state] = {}
        for split in SPLITS:
            latent = extract_latent(model, datasets[split], loader_seed, device)
            save_npz(latent_dir / f"{state}_{split}.npz", latent=latent,
                     sample_ids=np.array([rows[i]["sample_id"] for i in indices[split]]))
            losses[state][split] = reconstruction_loss(model, make_loader(datasets[split], loader_seed), device)
    write_json(output / "reconstruction_losses.json", losses)
    reconstruction_artifact(model, datasets["test"], [rows[i]["sample_id"] for i in indices["test"]], output, device)
    return losses


def run_one(master_seed, output, root, receipt_path, device="cpu"):
    if master_seed not in FORMAL_SEEDS:
        raise ValueError("Only the five approved master seeds are formal")
    if np.__version__ != NUMPY_VERSION:
        raise ValueError("Pinned NumPy version is required")
    commit = clean_commit(root)
    receipt = require_verification(root, receipt_path)
    # This must be set before initializing CUDA's BLAS context.
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    configure_precision()
    output = new_directory(output)
    config = {**configuration(), "run_id": output.name, "formal": True, "master_seed": master_seed,
              "seeds": seeds_for(master_seed), "git_commit": commit, "numpy_version": np.__version__,
              "canonical_source_commit": SOURCE_COMMIT, "environment": environment(),
              "implementation": implementation_fingerprint(root), "device": device}
    status = {"execution_status": "INVALID", "evaluation_flags": [], "complete": False,
              "reason": "Run has not completed; an interrupted attempt remains INVALID"}
    write_json(output / "configuration.json", config)
    write_json(output / "verification.json", receipt)
    write_json(output / "status.json", status)
    try:
        rows = assign_splits(generate_metadata(config["seeds"]["generation_seed"]), config["seeds"]["split_seed"])
        write_metadata(output / "metadata.csv", rows)
        indices = split_indices(rows)
        save_npz(output / "split.npz", **indices)
        images = generate_images(rows, output / "images.npy")
        datasets = {split: ImageDataset(images, ids) for split, ids in indices.items()}
        model = Autoencoder(config["seeds"]["model_seed"])
        config["parameter_count"] = sum(p.numel() for p in model.parameters())
        write_json(output / "configuration.json", config, replace=True)
        train(model, datasets["train"], datasets["validation"], config["seeds"]["loader_seed"], output, device)
        export_states(model, datasets, indices, rows, config["seeds"]["loader_seed"], output, device)
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
        report = {"OBSERVATIONS": "Recorded execution and measurements only; no run-level scientific classification.",
                  "METRICS": "training.csv; reconstruction_losses.json; evaluation/summary.json (when produced)",
                  "WARNINGS": status, "ARTIFACTS": sorted(inventory(output)),
                  "conditions": "configuration.json", "learning": "training.csv",
                  "linear_probe": "evaluation/probe_*.json", "distance": "evaluation/distance_*.json",
                  "pixel_baseline": "evaluation/pixel_*.json", "PCA": "evaluation/pca_initial; evaluation/pca_final"}
        write_json(output / "report.json", report)
        write_json(output / "integrity.json", inventory(output))
    return status


def reanalyze(run, output):
    check_integrity(run)
    config = read_json(Path(run) / "configuration.json")
    if config["numpy_version"] != np.__version__:
        raise ValueError("Reanalysis requires the original NumPy version")
    result = evaluate_saved(run, output)
    write_json(Path(output) / "provenance.json", {"source_run": str(Path(run).resolve()), "source_configuration": config,
                                               "environment": environment()})
    write_json(Path(output) / "integrity.json", inventory(output))
    return result
