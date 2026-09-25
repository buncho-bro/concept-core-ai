"""Approved overrides only; inherited conditions are copied without mutation."""
from hashlib import sha256
from exp001.config import (COLORS, SHAPES, FORMAL_SEEDS, PURPOSES, NUMPY_VERSION,
                           configuration as inherited_configuration)

SOURCE_COMMIT = "be87d3bbc02c1c19253396a6fa131ed938fb647e"
SEEN = (("red", "circle"), ("red", "triangle"), ("green", "triangle"),
        ("green", "square"), ("blue", "square"), ("blue", "circle"))
HELDOUT = (("red", "square"), ("green", "circle"), ("blue", "triangle"))
ACTIVE_SPLITS = ("train", "validation", "seen_test", "heldout_test")
SPLITS = (*ACTIVE_SPLITS, "reserved")
SPLIT_COUNTS = dict(zip(SPLITS, (4800, 600, 600, 300, 2700)))
BOOTSTRAP_PURPOSES = ("seen_distance_bootstrap", "cross_distance_bootstrap")


def _seed(value, purpose):
    if type(value) is not int or value < 0:
        raise ValueError("Seed must be an unsigned integer")
    return int.from_bytes(sha256(f"exp002|{value}|{purpose}".encode("ascii")).digest()[:4], "big")


def derive_seed(master_seed, purpose):
    if purpose not in PURPOSES:
        raise ValueError("Unknown seed purpose")
    return _seed(master_seed, purpose)


def bootstrap_seed(analysis_seed, purpose):
    if purpose not in BOOTSTRAP_PURPOSES or type(analysis_seed) is not int or not 0 <= analysis_seed < 2**32:
        raise ValueError("Expected unsigned 32-bit analysis seed and bootstrap purpose")
    return _seed(analysis_seed, purpose)


def seeds_for(master_seed):
    seeds = {"master_seed": master_seed, **{f"{p}_seed": derive_seed(master_seed, p) for p in PURPOSES}}
    seeds.update({f"{p}_seed": bootstrap_seed(seeds["analysis_seed"], p) for p in BOOTSTRAP_PURPOSES})
    return seeds


def configuration():
    config = inherited_configuration()
    config["experiment_id"] = "exp002"
    config["dataset"].pop("split_per_combination")
    config["dataset"].update(seen_combinations=[list(c) for c in SEEN],
        heldout_combinations=[list(c) for c in HELDOUT],
        seen_split_per_combination=[800, 100, 100], heldout_split_per_combination=[100, 900],
        split_counts=SPLIT_COUNTS.copy())
    config["training"]["loss"] = "per_image_mean(0.5*foreground_MSE+0.5*background_MSE)"
    config["analysis"].pop("bootstrap_size")
    config["analysis"].update(scaler_fit="seen_train_only", seen_bootstrap_size=600,
        cross_bootstrap_sizes=[600, 300], bootstrap_streams=list(BOOTSTRAP_PURPOSES),
        primary_probe="heldout_test", primary_distance="seen_heldout_cross_standardized",
        reconstruction_gate={"split": "seen_test", "ratio_lt_1_minimum_seeds": 4, "median_ratio_max": 0.80},
        success={"probe_positive_minimum_seeds": 4, "median_probe_delta_minimum": 0.05,
                 "median_final_accuracy_minimum": 0.70, "positive_final_contrast_minimum_seeds": 4,
                 "median_distance_delta_strict_minimum": 0.0})
    return config
