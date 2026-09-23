"""All-pair distances and the approved sample-instance percentile bootstrap."""
import numpy as np
from scipy.spatial.distance import pdist
from .evaluation import TrainScaler

CATEGORIES = ("same_color_same_shape", "same_color_different_shape",
              "different_color_same_shape", "different_color_different_shape")
GROUPS = {**{name: (i,) for i, name in enumerate(CATEGORIES)},
          "same_color": (0, 1), "different_color": (2, 3),
          "same_shape": (0, 2), "different_shape": (1, 3)}


def pair_layout(colors, shapes, sample_ids):
    if len(set(sample_ids)) != len(sample_ids):
        raise ValueError("Test sample IDs must be unique before resampling")
    i, j = np.triu_indices(len(sample_ids), k=1)
    colors, shapes = np.asarray(colors), np.asarray(shapes)
    category = 2 * (colors[i] != colors[j]).astype(np.int8) + (shapes[i] != shapes[j]).astype(np.int8)
    return i, j, category


def pair_statistics(distances, category):
    result = {}
    for name, codes in GROUPS.items():
        values = distances[np.isin(category, codes)]
        result[name] = {"count": len(values), "mean_distance": float(values.mean()) if len(values) else None,
                        "median_distance": float(np.median(values)) if len(values) else None,
                        "standard_deviation": float(values.std(ddof=0)) if len(values) else None}
    return result


def bootstrap_indices(analysis_seed):
    rng = np.random.Generator(np.random.PCG64(analysis_seed))
    for iteration in range(1000):
        yield rng.integers(low=0, high=900, size=900, endpoint=False, dtype=np.int64)


def linear_quantile(values, q):
    y = np.sort(np.asarray(values, dtype=np.float64))
    if not len(y) or not 0 <= q <= 1:
        raise ValueError("Invalid quantile input")
    h = (len(y) - 1) * q
    i = int(np.floor(h))
    f = h - i
    return float(y[i] if i == len(y)-1 else (1-f)*y[i] + f*y[i+1])


def confidence_interval(means):
    valid = np.asarray(means, dtype=np.float64)
    valid = valid[np.isfinite(valid)]
    if len(valid) < 950:
        return {"valid_iterations": len(valid), "CI": None, "flag": "BOOTSTRAP_CI_FAILED"}
    return {"valid_iterations": len(valid), "CI": [linear_quantile(valid, 0.025), linear_quantile(valid, 0.975)]}


def instance_means(indices, i, j, category, distances, n_samples):
    # Counts are an exact compressed representation of distinct sampled instances.
    # Only i<j original pairs exist; same-original and self-instance pairs cannot enter.
    counts = np.bincount(indices, minlength=n_samples)
    weights = counts[i] * counts[j]
    denominators = np.bincount(category, weights=weights, minlength=4)
    numerators = np.bincount(category, weights=weights * distances, minlength=4)
    result = []
    for codes in GROUPS.values():
        denom = denominators[list(codes)].sum()
        result.append(numerators[list(codes)].sum()/denom if denom else np.nan)
    return np.asarray(result)


def bootstrap(distances, i, j, category, analysis_seed):
    if len(i) != 404550 or int(max(i.max(), j.max())) != 899:
        raise ValueError("Formal bootstrap requires all 900 Test samples")
    indices = np.empty((1000, 900), dtype=np.int64)
    means = np.empty((1000, len(GROUPS)), dtype=np.float64)
    for iteration, vector in enumerate(bootstrap_indices(analysis_seed)):
        indices[iteration] = vector
        means[iteration] = instance_means(vector, i, j, category, distances, 900)
    summaries = {name: confidence_interval(means[:, k]) for k, name in enumerate(GROUPS)}
    return {"indices": indices, "means": means, "group_order": list(GROUPS), "summaries": summaries}


def analyze_distance(train, test, colors, shapes, sample_ids, analysis_seed):
    if len(test) != 900:
        raise ValueError("Expected exactly 900 Test latent rows")
    scaler = TrainScaler.fit(train)
    if not np.isfinite(test).all():
        return {"flag": "DISTANCE_FAILED", "reason": "Non-finite Test latent"}
    i, j, category = pair_layout(colors, shapes, sample_ids)
    result = {"scaler": scaler.as_dict(), "sample_ids": np.asarray(sample_ids),
              "pair_i": i, "pair_j": j, "category": category, "metrics": {}, "flags": []}
    for kind, features in (("standardized", scaler.transform(test)), ("raw", np.asarray(test, dtype=np.float64))):
        distances = pdist(features, metric="euclidean")
        if not np.isfinite(distances).all():
            result["flags"].append("DISTANCE_FAILED")
            continue
        stats = pair_statistics(distances, category)
        boot = bootstrap(distances, i, j, category, analysis_seed)
        for name in GROUPS:
            stats[name]["bootstrap_95_percent_CI_for_mean"] = boot["summaries"][name]["CI"]
            stats[name]["bootstrap_valid_iterations"] = boot["summaries"][name]["valid_iterations"]
        if any("flag" in v for v in boot["summaries"].values()):
            result["flags"].append("BOOTSTRAP_CI_FAILED")
        contrast = {a: stats[f"different_{a}"]["mean_distance"] - stats[f"same_{a}"]["mean_distance"] for a in ("color", "shape")}
        result["metrics"][kind] = {"distances": distances, "statistics": stats, "contrast": contrast, "bootstrap": boot}
    result["flags"] = sorted(set(result["flags"]))
    return result
