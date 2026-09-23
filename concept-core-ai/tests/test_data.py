from collections import Counter
import itertools
import math
import numpy as np
import pytest
from exp001.config import FORMAL_SEEDS, PURPOSES, COLORS, SHAPES, SPLITS, derive_seed, seeds_for
from exp001.data import (generate_metadata, assign_splits, split_indices, rasterize, vertices,
                         inside_polygon, ImageDataset, generate_images, OFFSETS)


def test_seed_fixed_vectors_and_order():
    assert FORMAL_SEEDS == (1001, 1002, 1003, 1004, 1005)
    expected = [1868740972, 2343864617, 175629694, 3608716037, 872121090, 3362619837]
    assert [derive_seed(1001, p) for p in PURPOSES] == expected
    assert [derive_seed(1001, p) for p in reversed(PURPOSES)] == expected[::-1]
    all_seeds = [derive_seed(s, p) for s in FORMAL_SEEDS for p in PURPOSES]
    assert len(set(all_seeds)) == 30
    assert seeds_for(1001)["master_seed"] == 1001
    with pytest.raises(ValueError):
        derive_seed(1001, "unknown")


def test_metadata_and_independent_split(metadata):
    assert len(metadata) == 9000
    assert len({r["sample_id"] for r in metadata}) == 9000
    counts = Counter((r["color"], r["shape"], r["split"]) for r in metadata)
    for color, shape, (split, count) in itertools.product(COLORS, SHAPES, zip(SPLITS, [800, 100, 100])):
        assert counts[color, shape, split] == count
    ids = split_indices(metadata)
    assert [len(ids[s]) for s in SPLITS] == [7200, 900, 900]
    for a, b in itertools.combinations(ids.values(), 2):
        assert not set(a) & set(b)
    assert set(np.concatenate(list(ids.values()))) == set(range(9000))
    original = generate_metadata(57)
    assert original == generate_metadata(57)
    changed = assign_splits(original, 82)
    assert any(a["split"] != b["split"] for a, b in zip(metadata, changed))
    assert [{k:v for k,v in r.items() if k != "split"} for r in changed] == original
    assert generate_metadata(58) != original


def test_distribution_bounds_and_clipping(metadata):
    bases = dict(zip(COLORS, ((230,25,25), (25,230,25), (25,25,230))))
    noise = []
    for row in metadata:
        assert 26 <= row["x"] <= 38 and 26 <= row["y"] <= 38
        assert 12 <= row["size"] <= 16
        assert 0 <= row["rotation"] < 360
        if row["shape"] == "circle":
            assert row["rotation"] == 0.0
        delta = np.array([row[k] for k in "rgb"]) - bases[row["color"]]
        assert np.all((-10 <= delta) & (delta <= 10))
        noise.append(delta)
        assert row["x"] - row["size"] >= -0.5
        assert row["x"] + row["size"] < 63.5
        assert row["y"] - row["size"] >= -0.5
        assert row["y"] + row["size"] < 63.5
    noise = np.array(noise)
    assert all(set(noise[:, k]) == set(range(-10, 11)) for k in range(3))
    assert np.any(noise[:, 0] != noise[:, 1]) and np.any(noise[:, 1] != noise[:, 2])


def row(shape="circle", rotation=0.0):
    return {"shape":shape, "rotation":rotation, "x":32, "y":32, "size":12, "r":231, "g":25, "b":17}


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("rotation", [0.0, 31.25, 90.0, 359.999])
def test_raster_against_independent_halfplane_oracle(shape, rotation):
    r = row(shape, rotation)
    image = rasterize(r)
    assert image.dtype == np.float32 and image.shape == (64, 64, 3)
    assert np.all(image[0] == 0) and np.all(image[-1] == 0)
    assert set(OFFSETS) == {-3/8, -1/8, 1/8, 3/8}
    n = {"triangle":3, "square":4}.get(shape)
    # Independent regular-polygon apothem test, without implementation vertices.
    for y, x in [(32,32), (32,44), (32,43), (22,28), (23,24), (40,40), (31,20)]:
        count = 0
        for oy, ox in itertools.product((-3/8,-1/8,1/8,3/8), repeat=2):
            dx, dy = x+ox-32, -(y+oy-32)
            if shape == "circle":
                inside = dx*dx + dy*dy <= 144
            else:
                angle = math.radians(rotation)
                inside = all(dx*math.cos(angle+(2*k+1)*math.pi/n) + dy*math.sin(angle+(2*k+1)*math.pi/n)
                             <= 12*math.cos(math.pi/n) + 1e-12 for k in range(n))
            count += inside
        np.testing.assert_array_equal(image[y,x], np.array([231,25,17])*count/16)
    assert np.any(image != np.floor(image))
    assert np.all(image * 16 == np.floor(image * 16))


def test_geometry_boundary_and_direction():
    for shape, n in (("triangle",3), ("square",4)):
        points = vertices(shape, 32, 32, 12, 0)
        np.testing.assert_allclose(points[0], [44,32])
        assert points[1,1] < 32
        np.testing.assert_allclose(np.linalg.norm(points-[32,32],axis=1), 12)
        assert inside_polygon(points[:,0], points[:,1], points).all()
        mids = (points + np.roll(points, -1, axis=0))/2
        assert inside_polygon(mids[:,0], mids[:,1], points).all()
        assert not inside_polygon(np.array([100.]),np.array([100.]),points).any()
    with pytest.raises(ValueError, match="Clipping"):
        rasterize({**row(), "x":0})


def test_fractional_round_trip_and_image_only(tmp_path):
    rows = [row(), row("triangle", 13.5)]
    images = generate_images(rows, tmp_path / "images.npy")
    np.testing.assert_array_equal(images[0], rasterize(rows[0]))
    disk = np.load(tmp_path / "images.npy", allow_pickle=False)
    np.testing.assert_array_equal(disk, images)
    dataset = ImageDataset(disk, [1,0])
    assert not hasattr(dataset, "metadata")
    assert dataset[0].shape == (3,64,64)
    np.testing.assert_array_equal(dataset[0].numpy(), disk[1].transpose(2,0,1)/255)
