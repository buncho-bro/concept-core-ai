"""Inherited generation; explicit Exp002 split assignment and leakage guards."""
from collections import Counter
import numpy as np
from exp001.data import generate_metadata, generate_images, rasterize, ImageDataset
from .config import COLORS, SHAPES, SEEN, HELDOUT, SPLITS, ACTIVE_SPLITS, SPLIT_COUNTS


def assign_splits(rows, split_seed):
    if len(rows) != 9000 or len({r["sample_id"] for r in rows}) != 9000:
        raise ValueError("Expected 9000 unique samples")
    result = [dict(r) for r in rows]
    rng = np.random.Generator(np.random.PCG64(split_seed))
    for color in COLORS:
        for shape in SHAPES:
            group = sorted((i for i, r in enumerate(rows) if (r["color"], r["shape"]) == (color, shape)),
                           key=lambda i: rows[i]["sample_id"])
            if len(group) != 1000:
                raise ValueError("Expected 1000 samples per combination")
            group = rng.permutation(np.asarray(group, dtype=np.int64))
            parts = (("train", group[:800]), ("validation", group[800:900]), ("seen_test", group[900:])) \
                if (color, shape) in SEEN else (("heldout_test", group[:100]), ("reserved", group[100:]))
            for split, ids in parts:
                for i in ids:
                    result[int(i)]["split"] = split
    validate_splits(result)
    return result


def validate_splits(rows, split_seed=None):
    if len(rows) != 9000 or len({r["sample_id"] for r in rows}) != 9000:
        raise ValueError("Expected 9000 unique samples")
    counts = Counter((r["color"], r["shape"], r["split"]) for r in rows)
    expected = {}
    for combo in SEEN:
        expected.update({(*combo, s): n for s, n in (("train", 800), ("validation", 100), ("seen_test", 100))})
    for combo in HELDOUT:
        expected.update({(*combo, s): n for s, n in (("heldout_test", 100), ("reserved", 900))})
    if counts != expected or Counter(r["split"] for r in rows) != SPLIT_COUNTS:
        raise ValueError("Split counts or seen/held-out isolation violated")
    if split_seed is not None:
        expected_rows = assign_splits(rows, split_seed)
        if any(a["split"] != b["split"] for a, b in zip(rows, expected_rows)):
            raise ValueError("Split assignment does not match the registered shuffle")


def split_indices(rows):
    validate_splits(rows)
    return {s: np.asarray(sorted((i for i, r in enumerate(rows) if r["split"] == s),
                                 key=lambda i: rows[i]["sample_id"]), dtype=np.int64) for s in SPLITS}


class SplitDataset(ImageDataset):
    """Only return pixels; reject Reserved and incorrectly routed metadata upfront."""
    def __init__(self, images, rows, indices, split):
        if split not in ACTIVE_SPLITS or not len(indices) or len(set(indices)) != len(indices):
            raise ValueError("Invalid active split selection")
        combos = SEEN if split != "heldout_test" else HELDOUT
        if any(rows[i]["split"] != split or (rows[i]["color"], rows[i]["shape"]) not in combos for i in indices):
            raise ValueError("Held-out/Reserved leakage or split mismatch")
        self.split = split
        super().__init__(images, indices)


def representative_indices(rows):
    result = []
    for combo in (*SEEN, *HELDOUT):
        split = "seen_test" if combo in SEEN else "heldout_test"
        eligible = [i for i, r in enumerate(rows) if (r["color"], r["shape"], r["split"]) == (*combo, split)]
        if not eligible:
            raise ValueError("Missing representative Test combination")
        result.append(min(eligible, key=lambda i: rows[i]["sample_id"]))
    return np.asarray(result, dtype=np.int64)
