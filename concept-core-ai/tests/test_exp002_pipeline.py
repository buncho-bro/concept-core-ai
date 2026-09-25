"""Synthetic saved-artifact integration. No formal optimization or baseline run."""
import numpy as np
import pytest
from exp002.artifacts import (write_json, read_json, save_npz, inventory, check_integrity,
                             environment, implementation_fingerprint)
from exp002.config import configuration, seeds_for, ACTIVE_SPLITS, COLORS, SHAPES, SOURCE_COMMIT
from exp002.data import generate_metadata, assign_splits, split_indices
from exp002.distance import cross_instance_contrasts
from exp002.performance import Performance
from exp002.runner import write_metadata, evaluate_saved, reanalyze
from exp002.aggregation import record_from_run, aggregate_records


def test_saved_artifact_pipeline_counts_bootstrap_and_reserved_exclusion(tmp_path):
    run = tmp_path / "NONFORMAL-synthetic-evaluation-77"
    run.mkdir()
    seeds = seeds_for(77)
    rows = assign_splits(generate_metadata(seeds["generation_seed"]), seeds["split_seed"])
    indices = split_indices(rows)
    config = {**configuration(), "formal": False, "master_seed": 77, "seeds": seeds,
        "canonical_source_commit": SOURCE_COMMIT, "environment": environment(),
        "device_class": "cpu", "performance": Performance().as_dict(), "git_commit": "synthetic-fixture"}
    write_json(run / "configuration.json", config)
    write_metadata(run / "metadata.csv", rows)
    save_npz(run / "split.npz", **indices)
    rng = np.random.Generator(np.random.PCG64(78))
    latent = rng.normal(0, .15, size=(9000, 32)).astype(np.float32)
    colors = np.array([COLORS.index(r["color"]) for r in rows])
    shapes = np.array([SHAPES.index(r["shape"]) for r in rows])
    latent[:, :3] += np.eye(3)[colors]
    latent[:, 3:6] += np.eye(3)[shapes]
    latent[:, -1] = 0  # Excluded dimension. Not silently added back to standardized distance.
    (run / "latent").mkdir()
    for state in ("initial", "final"):
        for split in ACTIVE_SPLITS:
            ids = indices[split]
            save_npz(run / "latent" / f"{state}_{split}.npz", latent=latent[ids], sample_ids=np.asarray([rows[i]["sample_id"] for i in ids]))
    images = np.lib.format.open_memmap(run / "images.npy", mode="w+", dtype=np.float32, shape=(9000, 64, 64, 3))
    images[:] = 0
    for i in range(9000):
        images[i, 0, :shapes[i]+1, colors[i]] = 230
    # A tripwire: Reserved is not even read into a scaler or pixel evaluation.
    images[indices["reserved"]] = np.nan
    images.flush(); del images
    summary = evaluate_saved(run, run / "evaluation")
    assert summary["evaluation_flags"] == [] and "classification" not in summary
    for attribute in ("color", "shape"):
        assert summary["derived"][attribute]["heldout_probe_delta"] == 0
        assert summary["derived"][attribute]["cross_distance_delta"] == 0
    output = run / "evaluation"
    with np.load(output / "bootstrap_indices.npz") as draws:
        assert draws["seen"].shape == draws["cross_seen"].shape == (1000, 600)
        assert draws["cross_heldout"].shape == (1000, 300)
        assert not np.array_equal(draws["seen"], draws["cross_seen"])
        for state in ("initial", "final"):
            distance = read_json(output / f"distance_{state}.json")
            np.testing.assert_allclose(distance["scaler"]["mean"], latent[indices["train"]].astype(np.float64).mean(0), rtol=0, atol=0)
            assert not distance["scaler"]["keep"][-1]
            assert distance["scaler"]["fit_split"] == "seen_train"
            for population, count in (("seen", 179700), ("cross", 180000), ("heldout", 44850)):
                with np.load(output / f"pairs_{state}_{population}.npz") as pairs:
                    assert len(pairs["i"]) == len(pairs["j"]) == count
                    for kind in ("standardized", "raw"):
                        assert len(pairs[f"{kind}_distance"]) == count
                        if population == "cross":
                            for k, a in enumerate(("color", "shape")):
                                codes = pairs["category"]
                                same = codes == (1 if a == "color" else 2)
                                values = pairs[f"{kind}_distance"]
                                expected = values[~same].mean() - values[same].mean()
                                assert distance["metrics"][kind]["cross"]["contrast"][a] == pytest.approx(expected)
                            boot = np.load(output / f"bootstrap_{state}_{kind}_cross.npz")
                            assert boot["values"].shape == (1000, 2)
                            expected = cross_instance_contrasts(draws["cross_seen"][17], draws["cross_heldout"][17],
                                pairs["i"], pairs["j"], pairs["category"], pairs[f"{kind}_distance"], 600, 300)
                            np.testing.assert_array_equal(boot["values"][17], expected)
                            assert all(v["valid_iterations"] == 1000 for v in distance["metrics"][kind]["cross"]["bootstrap"]["summaries"].values())
            for attribute in ("color", "shape"):
                probe = read_json(output / f"probe_{state}_{attribute}.json")
                assert len(probe["candidates"]) == 5 and probe["converged"]
                for split, n in (("seen_test", 600), ("heldout_test", 300)):
                    assert len(probe[split]["predictions"]) == n
                    assert np.array(probe[split]["confusion_matrix"]).sum() == n
    # Same saved latents, same seed/analysis: all numerical JSON and bootstrap arrays repeat.
    assert read_json(output / "distance_initial.json") == read_json(output / "distance_final.json")
    for kind in ("standardized", "raw"):
        for population in ("seen", "cross"):
            with np.load(output / f"bootstrap_initial_{kind}_{population}.npz") as a, np.load(output / f"bootstrap_final_{kind}_{population}.npz") as b:
                np.testing.assert_array_equal(a["values"], b["values"])
    for kind in ("simple_image_statistics", "raw_pixel_linear"):
        for attribute in ("color", "shape"):
            pixel = read_json(output / f"pixel_{kind}_{attribute}.json")
            assert len(pixel["heldout_test"]["predictions"]) == 300
            assert pixel["scaler"]["fit_split"] == "seen_train"
    write_json(run / "status.json", {"execution_status": "VALID", "evaluation_flags": [], "complete": True})
    write_json(run / "integrity.json", inventory(run))
    check_integrity(run)
    record = record_from_run(run)
    assert record["execution_status"] == "VALID" and record["formal"] is False
    assert record["primary"]["color"]["initial_total"] == 300
    assert aggregate_records([record])["classification"] == "NOT_EVALUATED"
    with pytest.raises(FileExistsError): evaluate_saved(run, output)
    # Artifact corruption cannot be silently aggregated.
    (run / "metadata.csv").write_text("tampered", encoding="utf-8")
    assert record_from_run(run)["execution_status"] == "INVALID"


def test_reanalysis_environment_and_integrity_guard(tmp_path):
    run = tmp_path / "nonformal-fixture"; run.mkdir()
    write_json(run / "configuration.json", {"environment": {"different": True}, "implementation": {}})
    write_json(run / "integrity.json", inventory(run))
    with pytest.raises(ValueError, match="original environment"):
        reanalyze(run, tmp_path / "new-evaluation", tmp_path)
    assert not (tmp_path / "new-evaluation").exists()
