"""Seen/held-out geometry and exactly specified independent sample bootstraps."""
import numpy as np
from scipy.spatial.distance import cdist, pdist
from exp001.distance import (CATEGORIES, GROUPS, pair_layout, pair_statistics,
                             instance_means, linear_quantile, confidence_interval)
from exp001.evaluation import TrainScaler
from .config import bootstrap_seed

SEEN_COUNTS = (29700, 30000, 30000, 90000)
CROSS_COUNTS = (0, 60000, 60000, 60000)


def seen_bootstrap_indices(analysis_seed):
    rng = np.random.Generator(np.random.PCG64(bootstrap_seed(analysis_seed, "seen_distance_bootstrap")))
    for _ in range(1000):
        yield rng.integers(low=0, high=600, size=600, endpoint=False, dtype=np.int64)


def cross_bootstrap_indices(analysis_seed):
    rng = np.random.Generator(np.random.PCG64(bootstrap_seed(analysis_seed, "cross_distance_bootstrap")))
    for _ in range(1000):
        seen = rng.integers(low=0, high=600, size=600, endpoint=False, dtype=np.int64)
        heldout = rng.integers(low=0, high=300, size=300, endpoint=False, dtype=np.int64)
        yield seen, heldout


def bootstrap_draws(analysis_seed):
    seen = np.asarray(list(seen_bootstrap_indices(analysis_seed)))
    cross = list(cross_bootstrap_indices(analysis_seed))
    return {"seen": seen, "cross_seen": np.asarray([v[0] for v in cross]),
            "cross_heldout": np.asarray([v[1] for v in cross])}


def cross_layout(seen_colors, seen_shapes, seen_ids, heldout_colors, heldout_shapes, heldout_ids):
    if len(set(seen_ids)) != len(seen_ids) or len(set(heldout_ids)) != len(heldout_ids) or set(seen_ids) & set(heldout_ids):
        raise ValueError("Seen/Held-out sample IDs must be unique and disjoint")
    i, j = np.repeat(np.arange(len(seen_ids)), len(heldout_ids)), np.tile(np.arange(len(heldout_ids)), len(seen_ids))
    category = (2 * (np.asarray(seen_colors)[i] != np.asarray(heldout_colors)[j]).astype(np.int8)
                + (np.asarray(seen_shapes)[i] != np.asarray(heldout_shapes)[j]).astype(np.int8))
    if np.any(category == 0):
        raise ValueError("Seen/Held-out combinations overlap")
    return i, j, category


def cross_instance_contrasts(seen_indices, heldout_indices, i, j, category, distances, n_seen, n_heldout):
    # A sampled occurrence is a distinct instance. Counts multiply across the
    # two disjoint populations, exactly retaining all cross-pair multiplicities.
    weights = np.bincount(seen_indices, minlength=n_seen)[i] * np.bincount(heldout_indices, minlength=n_heldout)[j]
    denominators = np.bincount(category, weights=weights, minlength=4)
    numerators = np.bincount(category, weights=weights * distances, minlength=4)
    contrasts = []
    for attribute in ("color", "shape"):
        same, different = list(GROUPS[f"same_{attribute}"]), list(GROUPS[f"different_{attribute}"])
        ns, nd = denominators[same].sum(), denominators[different].sum()
        contrasts.append(numerators[different].sum() / nd - numerators[same].sum() / ns if ns > 0 and nd > 0 else np.nan)
    return np.asarray(contrasts)


def contrast_statistics(distances, category):
    stats = pair_statistics(distances, category)
    contrast = {}
    for attribute in ("color", "shape"):
        same, different = stats[f"same_{attribute}"]["mean_distance"], stats[f"different_{attribute}"]["mean_distance"]
        contrast[attribute] = different - same if same is not None and different is not None else None
    return stats, contrast


def bootstrap_seen(distances, i, j, category, draws):
    if len(i) != 179700 or np.bincount(category, minlength=4).tolist() != list(SEEN_COUNTS) or draws.shape != (1000, 600):
        raise ValueError("Expected approved Seen-only pair population and draws")
    means = np.asarray([instance_means(v, i, j, category, distances, 600) for v in draws])
    summaries = {name: confidence_interval(means[:, k]) for k, name in enumerate(GROUPS)}
    return {"values": means, "statistic_order": list(GROUPS), "summaries": summaries}


def bootstrap_cross(distances, i, j, category, seen_draws, heldout_draws):
    if len(i) != 180000 or np.bincount(category, minlength=4).tolist() != list(CROSS_COUNTS):
        raise ValueError("Expected approved cross-pair population")
    if seen_draws.shape != (1000, 600) or heldout_draws.shape != (1000, 300):
        raise ValueError("Expected approved cross-bootstrap draws")
    values = np.asarray([cross_instance_contrasts(s, h, i, j, category, distances, 600, 300)
                         for s, h in zip(seen_draws, heldout_draws)])
    return {"values": values, "statistic_order": ["color", "shape"],
            "summaries": {a: confidence_interval(values[:, k]) for k, a in enumerate(("color", "shape"))}}


def analyze_distance(train, seen, heldout, labels, sample_ids, analysis_seed, draws=None):
    if len(seen) != 600 or len(heldout) != 300:
        raise ValueError("Expected 600 Seen Test and 300 Held-out Test latents")
    result = {"flags": [], "metrics": {}, "sample_ids": sample_ids}
    if not all(np.isfinite(x).all() for x in (train, seen, heldout)):
        return {**result, "flags": ["DISTANCE_FAILED"], "reason": "Non-finite latent"}
    scaler = TrainScaler.fit(train)
    result["scaler"] = {**scaler.as_dict(), "fit_split": "seen_train"}
    if not scaler.keep.any():
        return {**result, "flags": ["DISTANCE_FAILED"], "reason": "No retained dimensions"}
    si, sj, sc = pair_layout(labels["seen_test"]["color"], labels["seen_test"]["shape"], sample_ids["seen_test"])
    hi, hj, hc = pair_layout(labels["heldout_test"]["color"], labels["heldout_test"]["shape"], sample_ids["heldout_test"])
    ci, cj, cc = cross_layout(labels["seen_test"]["color"], labels["seen_test"]["shape"], sample_ids["seen_test"],
        labels["heldout_test"]["color"], labels["heldout_test"]["shape"], sample_ids["heldout_test"])
    if tuple(np.bincount(sc, minlength=4)) != SEEN_COUNTS or tuple(np.bincount(cc, minlength=4)) != CROSS_COUNTS:
        raise ValueError("Pair category counts violate approved split design")
    result["pairs"] = {"seen": (si, sj, sc), "heldout": (hi, hj, hc), "cross": (ci, cj, cc)}
    draws = bootstrap_draws(analysis_seed) if draws is None else draws
    for kind, s, h in (("standardized", scaler.transform(seen), scaler.transform(heldout)),
                       ("raw", np.asarray(seen, dtype=np.float64), np.asarray(heldout, dtype=np.float64))):
        sd, hd, cd = pdist(s), pdist(h), cdist(s, h).ravel()
        if not all(np.isfinite(x).all() for x in (sd, hd, cd)):
            if kind == "standardized":
                result["flags"].append("DISTANCE_FAILED")
            result.setdefault("secondary_warnings", []).append(f"Non-finite {kind} distances")
            continue
        seen_boot = bootstrap_seen(sd, si, sj, sc, draws["seen"])
        cross_boot = bootstrap_cross(cd, ci, cj, cc, draws["cross_seen"], draws["cross_heldout"])
        ss, _ = contrast_statistics(sd, sc)
        cs, contrast = contrast_statistics(cd, cc)
        for name in GROUPS:
            ss[name].update(bootstrap=seen_boot["summaries"][name])
        required = [seen_boot["summaries"][name] for name in CATEGORIES] + list(cross_boot["summaries"].values())
        if any("flag" in summary for summary in required):
            result["flags"].append("BOOTSTRAP_CI_FAILED")
        result["metrics"][kind] = {
            "seen": {"statistics": ss, "distances": sd, "bootstrap": seen_boot},
            "heldout": {"statistics": pair_statistics(hd, hc), "distances": hd, "descriptive_only": True},
            "cross": {"statistics": cs, "contrast": contrast, "distances": cd, "bootstrap": cross_boot}}
    result["flags"] = sorted(set(result["flags"]))
    return result
