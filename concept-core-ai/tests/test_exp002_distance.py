from itertools import combinations, product
import numpy as np
import pytest
from exp001.distance import GROUPS, pair_layout, instance_means, pair_statistics
from exp002.config import SEEN, HELDOUT, bootstrap_seed
from exp002.distance import (seen_bootstrap_indices, cross_bootstrap_indices, bootstrap_draws,
    cross_layout, cross_instance_contrasts, contrast_statistics, linear_quantile, confidence_interval,
    analyze_distance, SEEN_COUNTS, CROSS_COUNTS)


def populations():
    def labels(combos):
        return {"color": np.repeat([c for c, s in combos], 100), "shape": np.repeat([s for c, s in combos], 100)}
    return {"seen_test": labels(SEEN), "heldout_test": labels(HELDOUT)}, {"seen_test": np.arange(600), "heldout_test": np.arange(600, 900)}


def test_pair_counts_exact_and_no_same_combination_cross_pairs():
    labels, ids = populations()
    i, j, category = pair_layout(*labels["seen_test"].values(), ids["seen_test"])
    assert len(i) == 179700 and np.all(i < j)
    assert tuple(np.bincount(category)) == SEEN_COUNTS
    a, b, cross = cross_layout(*labels["seen_test"].values(), ids["seen_test"], *labels["heldout_test"].values(), ids["heldout_test"])
    assert len(a) == 180000 and len(set(zip(a, b))) == 180000
    assert tuple(np.bincount(cross)) == CROSS_COUNTS
    stats = pair_statistics(np.ones(179700), category)
    assert stats["same_color_same_shape"]["standard_deviation"] == 0


def test_exact_rng_draw_order_and_independent_streams():
    analysis_seed = 7789
    expected_seen = np.random.Generator(np.random.PCG64(bootstrap_seed(analysis_seed, "seen_distance_bootstrap")))
    expected_cross = np.random.Generator(np.random.PCG64(bootstrap_seed(analysis_seed, "cross_distance_bootstrap")))
    a = bootstrap_draws(analysis_seed)
    assert a["seen"].shape == (1000, 600)
    for iteration in range(1000):
        np.testing.assert_array_equal(a["seen"][iteration], expected_seen.integers(low=0, high=600, size=600, endpoint=False, dtype=np.int64))
        np.testing.assert_array_equal(a["cross_seen"][iteration], expected_cross.integers(low=0, high=600, size=600, endpoint=False, dtype=np.int64))
        np.testing.assert_array_equal(a["cross_heldout"][iteration], expected_cross.integers(low=0, high=300, size=300, endpoint=False, dtype=np.int64))
    # Reverse execution order; also consume unrelated global RNG values.
    np.random.seed(123); np.random.random(10)
    cross_first = list(cross_bootstrap_indices(analysis_seed))
    seen_second = np.asarray(list(seen_bootstrap_indices(analysis_seed)))
    np.testing.assert_array_equal(seen_second, a["seen"])
    np.testing.assert_array_equal([p[0] for p in cross_first], a["cross_seen"])
    np.testing.assert_array_equal([p[1] for p in cross_first], a["cross_heldout"])
    assert not np.array_equal(a["seen"], a["cross_seen"])


def test_seen_instance_multiplicity_matches_literal_instance_pairs():
    colors, shapes, ids = np.array(["r", "r", "g", "g"]), np.array(["c", "c", "c", "s"]), [10, 11, 12, 13]
    i, j, category = pair_layout(colors, shapes, ids)
    distance = np.array([abs(x-y) for x, y in zip([0, 0, 0, 2, 2, 5], [2, 5, 9, 5, 9, 9])], dtype=float)
    sampled = np.array([0, 0, 1, 2, 3, 3, 3])
    actual = instance_means(sampled, i, j, category, distance, 4)
    lookup = {(int(a), int(b)): (int(c), d) for a, b, c, d in zip(i, j, category, distance)}
    literal = []
    for a, b in combinations(sampled, 2):
        if a != b:  # exclude two distinct instances of the same original ID
            literal.append(lookup[tuple(sorted((a, b)))])
    expected = [np.mean([d for c, d in literal if c in codes]) if any(c in codes for c, d in literal) else np.nan for codes in GROUPS.values()]
    np.testing.assert_allclose(actual, expected, equal_nan=True)
    assert len(literal) == 17  # C(7,2) minus C(2,2) and C(3,2)
    absent = instance_means(np.zeros(6, dtype=int), i, j, category, distance, 4)
    assert np.isnan(absent).all()


def test_cross_instance_multiplicity_sign_and_attribute_validity():
    colors, shapes = ["r", "g", "b"], ["c", "s", "c"]
    hcolors, hshapes = ["r", "g"], ["s", "c"]
    i, j, category = cross_layout(colors, shapes, [1, 2, 3], hcolors, hshapes, [4, 5])
    distances = np.array([1.0 if colors[a] == hcolors[b] else 4.0 for a, b in zip(i, j)])
    stats, contrasts = contrast_statistics(distances, category)
    assert contrasts["color"] == 3.0
    assert contrasts["shape"] < 0
    s, h = np.array([0, 0, 1, 2]), np.array([0, 1, 1])
    actual = cross_instance_contrasts(s, h, i, j, category, distances, 3, 2)
    pairs = [(colors[a], shapes[a], hcolors[b], hshapes[b], distances[a*2+b]) for a, b in product(s, h)]
    for k in (0, 1):
        same = [p[4] for p in pairs if p[k] == p[k+2]]
        different = [p[4] for p in pairs if p[k] != p[k+2]]
        assert actual[k] == pytest.approx(np.mean(different)-np.mean(same))
    # Only color has both same/different pairs in this replicate.
    ii, jj, cc = cross_layout(["r", "g"], ["c", "c"], [1, 2], ["r"], ["s"], [3])
    a = cross_instance_contrasts([0, 1], [0], ii, jj, cc, np.array([1., 4.]), 2, 1)
    assert a[0] == 3 and np.isnan(a[1])


@pytest.mark.parametrize("q,expected", [(0, 1), (1, 9), (.025, 1.15), (.975, 8.7), (.5, 4)])
def test_explicit_linear_interpolation(q, expected):
    assert linear_quantile([9, 1, 3, 5], q) == pytest.approx(expected)


@pytest.mark.parametrize("valid", [0, 1, 949, 950, 1000])
def test_ci_valid_iteration_boundary(valid):
    values = np.concatenate([np.arange(valid, dtype=float), np.full(1000-valid, np.nan)])
    result = confidence_interval(values)
    assert result["valid_iterations"] == valid
    if valid < 950:
        assert result["CI"] is None and result["flag"] == "BOOTSTRAP_CI_FAILED"
    else:
        assert "flag" not in result
        np.testing.assert_allclose(result["CI"], [(valid-1)*.025, (valid-1)*.975])


def test_nonfinite_and_no_dimensions_are_downstream_distance_flags():
    labels, ids = populations()
    result = analyze_distance(np.ones((8, 2)), np.ones((600, 2)), np.ones((300, 2)), labels, ids, 77)
    assert result["flags"] == ["DISTANCE_FAILED"]
    result = analyze_distance(np.eye(4), np.full((600, 4), np.nan), np.ones((300, 4)), labels, ids, 77)
    assert result["flags"] == ["DISTANCE_FAILED"]
