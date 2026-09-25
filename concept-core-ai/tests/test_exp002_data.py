from collections import Counter
from copy import deepcopy
from hashlib import sha256
import numpy as np
import pytest
from exp001 import data as inherited
from exp001.config import configuration as old_configuration, derive_seed as old_seed
from exp002.config import (configuration, seeds_for, derive_seed, bootstrap_seed, FORMAL_SEEDS, PURPOSES,
                           BOOTSTRAP_PURPOSES, SEEN, HELDOUT, SPLITS, SPLIT_COUNTS)
from exp002.data import (generate_metadata, rasterize, assign_splits, validate_splits, split_indices,
                         representative_indices, SplitDataset)


@pytest.fixture(scope="module")
def rows002():
    seeds = seeds_for(77)
    return assign_splits(generate_metadata(seeds["generation_seed"]), seeds["split_seed"])


@pytest.mark.parametrize("master", [77, *FORMAL_SEEDS])
def test_seed_namespace_and_unsigned_sha(master):
    # Seed arithmetic only; no artifacts or training with formal master seeds.
    for purpose in PURPOSES:
        expected = int(sha256(f"exp002|{master}|{purpose}".encode("ascii")).hexdigest()[:8], 16)
        assert derive_seed(master, purpose) == expected != old_seed(master, purpose)
    seeds = seeds_for(master)
    for purpose in BOOTSTRAP_PURPOSES:
        expected = int(sha256(f"exp002|{seeds['analysis_seed']}|{purpose}".encode("ascii")).hexdigest()[:8], 16)
        assert seeds[f"{purpose}_seed"] == bootstrap_seed(seeds["analysis_seed"], purpose) == expected
    assert len({seeds[f"{p}_seed"] for p in (*PURPOSES, *BOOTSTRAP_PURPOSES)}) == 8


@pytest.mark.parametrize("value", [-1, 2**32, "0077", 1.5, True])
def test_bootstrap_seed_rejects_noncanonical_values(value):
    with pytest.raises(ValueError):
        bootstrap_seed(value, "seen_distance_bootstrap")


def test_overrides_leave_inherited_science_unchanged():
    before = old_configuration()
    new = configuration()
    assert new["model"] == before["model"]
    assert {k: v for k, v in new["training"].items() if k != "loss"} == {k: v for k, v in before["training"].items() if k != "loss"}
    assert new["dataset"]["samples_per_combination"] == 1000
    new["model"]["latent_dim"] = 0
    assert old_configuration() == before and configuration()["model"]["latent_dim"] == 32
    assert generate_metadata is inherited.generate_metadata and rasterize is inherited.rasterize


def test_generation_and_split_determinism_exact_shuffled_positions(rows002):
    seeds = seeds_for(77)
    raw = generate_metadata(seeds["generation_seed"])
    assert raw == generate_metadata(seeds["generation_seed"])
    assert rows002 == assign_splits(raw, seeds["split_seed"])
    indices = split_indices(rows002)
    assert {s: len(ids) for s, ids in indices.items()} == SPLIT_COUNTS
    assert sorted(np.concatenate(list(indices.values())).tolist()) == list(range(9000))
    rng = np.random.Generator(np.random.PCG64(seeds["split_seed"]))
    for color in ("red", "green", "blue"):
        for shape in ("circle", "triangle", "square"):
            group = [r["sample_id"] for r in raw if (r["color"], r["shape"]) == (color, shape)]
            shuffled = rng.permutation(group)
            expect = ["train"]*800 + ["validation"]*100 + ["seen_test"]*100 if (color, shape) in SEEN else ["heldout_test"]*100 + ["reserved"]*900
            assert [rows002[i]["split"] for i in shuffled] == expect
    validate_splits(rows002, seeds["split_seed"])
    for i in range(0, 9000, 1000):
        np.testing.assert_array_equal(rasterize(raw[i]), rasterize(generate_metadata(seeds["generation_seed"])[i]))
        assert rasterize(raw[i]).dtype == np.float32
    assert all(rows002[i]["sample_id"] < rows002[j]["sample_id"] for ids in indices.values() for i, j in zip(ids, ids[1:]))


def test_leakage_and_reserved_guards(rows002):
    indices = split_indices(rows002)
    images = np.broadcast_to(np.zeros((64, 64, 3), np.float32), (9000, 64, 64, 3))
    for split in SPLITS[:-1]:
        dataset = SplitDataset(images, rows002, indices[split], split)
        assert tuple(dataset[0].shape) == (3, 64, 64)
        if split in ("train", "validation"):
            assert {(rows002[i]["color"], rows002[i]["shape"]) for i in dataset.indices} <= set(SEEN)
    for bad in ("heldout_test", "reserved", "validation"):
        with pytest.raises(ValueError):
            SplitDataset(images, rows002, indices[bad], "train")
    with pytest.raises(ValueError):
        SplitDataset(images, rows002, indices["reserved"], "reserved")
    corrupted = deepcopy(rows002)
    a, b = indices["train"][0], indices["heldout_test"][0]
    corrupted[a]["split"], corrupted[b]["split"] = corrupted[b]["split"], corrupted[a]["split"]
    with pytest.raises(ValueError):
        validate_splits(corrupted)


def test_tampered_shuffled_membership_detected(rows002):
    corrupted = deepcopy(rows002)
    a = next(i for i, r in enumerate(corrupted) if r["split"] == "train")
    b = next(i for i, r in enumerate(corrupted) if r["split"] == "validation" and (r["color"], r["shape"]) == (corrupted[a]["color"], corrupted[a]["shape"]))
    corrupted[a]["split"], corrupted[b]["split"] = corrupted[b]["split"], corrupted[a]["split"]
    validate_splits(corrupted)  # Counts alone cannot catch this.
    with pytest.raises(ValueError, match="shuffle"):
        validate_splits(corrupted, seeds_for(77)["split_seed"])


def test_representatives_nine_combinations_minimum_test_ids(rows002):
    ids = representative_indices(rows002)
    assert len(ids) == len(set(ids)) == 9
    assert [(rows002[i]["color"], rows002[i]["shape"]) for i in ids] == list((*SEEN, *HELDOUT))
    assert Counter(rows002[i]["split"] for i in ids) == {"seen_test": 6, "heldout_test": 3}
    for i in ids:
        row = rows002[i]
        assert row["sample_id"] == min(r["sample_id"] for r in rows002 if all(r[k] == row[k] for k in ("color", "shape", "split")))
    reversed_rows = list(reversed(rows002))
    assert [reversed_rows[i]["sample_id"] for i in representative_indices(reversed_rows)] == [rows002[i]["sample_id"] for i in ids]
