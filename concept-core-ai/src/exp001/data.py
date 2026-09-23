"""Explicit geometry, independent generation/split streams and image-only data."""
import numpy as np
from .config import COLORS, SHAPES, SPLITS, BASELINE

OFFSETS = np.array([-3/8, -1/8, 1/8, 3/8], dtype=np.float64)
_yy, _xx, _oy, _ox = np.meshgrid(np.arange(64), np.arange(64), OFFSETS, OFFSETS, indexing="ij")
PX, PY = _xx + _ox, _yy + _oy


def vertices(shape, x, y, size, rotation):
    n = {"triangle": 3, "square": 4}[shape]
    angle = np.deg2rad(rotation + np.arange(n) * (360.0 / n))
    return np.column_stack((x + size * np.cos(angle), y - size * np.sin(angle)))


def inside_polygon(px, py, points):
    """Clockwise convex vertices. Include edges, with roundoff-scale error bounds."""
    inside = np.ones(np.broadcast_shapes(np.shape(px), np.shape(py)), dtype=bool)
    for a, b in zip(points, np.roll(points, -1, axis=0)):
        u = (b[0] - a[0]) * (py - a[1])
        v = (b[1] - a[1]) * (px - a[0])
        error = 8 * np.finfo(np.float64).eps * (np.abs(u) + np.abs(v))
        inside &= u - v <= error
    return inside


def rasterize(row):
    x, y, size = row["x"], row["y"], row["size"]
    if row["shape"] == "circle":
        bounds = np.array([[x-size, y-size], [x+size, y+size]])
        inside = (PX-x)**2 + (PY-y)**2 <= size**2
    else:
        bounds = vertices(row["shape"], x, y, size, row["rotation"])
        inside = inside_polygon(PX, PY, bounds)
    if np.any(bounds < -0.5) or np.any(bounds >= 63.5):
        raise ValueError("Clipping is prohibited")
    coverage = inside.sum(axis=(2, 3)).astype(np.float32) / 16
    rgb = np.array([row["r"], row["g"], row["b"]], dtype=np.float32)
    return coverage[..., None] * rgb


def generate_metadata(generation_seed):
    rng = np.random.Generator(np.random.PCG64(generation_seed))
    rows = []
    for color, base in zip(COLORS, BASELINE["dataset"]["colors"]):
        for shape in SHAPES:
            for _ in range(1000):
                rgb = np.clip(np.asarray(base) + rng.integers(-10, 11, size=3), 0, 255)
                rows.append({"sample_id": len(rows), "color": color, "shape": shape,
                    "x": int(rng.integers(26, 39)), "y": int(rng.integers(26, 39)),
                    "size": int(rng.integers(12, 17)),
                    "rotation": 0.0 if shape == "circle" else float(rng.uniform(0, 360)),
                    "r": int(rgb[0]), "g": int(rgb[1]), "b": int(rgb[2]),
                    "generation_seed": generation_seed})
    return rows


def assign_splits(rows, split_seed):
    if len(rows) != 9000 or len({r["sample_id"] for r in rows}) != 9000:
        raise ValueError("Expected 9000 unique samples")
    result = [dict(row) for row in rows]
    rng = np.random.Generator(np.random.PCG64(split_seed))
    for color in COLORS:
        for shape in SHAPES:
            group = np.array([i for i, r in enumerate(rows) if (r["color"], r["shape"]) == (color, shape)])
            if len(group) != 1000:
                raise ValueError("Expected 1000 samples in each combination")
            group = rng.permutation(group)
            for name, ids in zip(SPLITS, (group[:800], group[800:900], group[900:])):
                for i in ids:
                    result[int(i)]["split"] = name
    return result


def split_indices(rows):
    return {s: np.array(sorted((i for i, r in enumerate(rows) if r["split"] == s),
                               key=lambda i: rows[i]["sample_id"]), dtype=np.int64) for s in SPLITS}


def generate_images(rows, path):
    images = np.lib.format.open_memmap(path, mode="w+", dtype=np.float32, shape=(len(rows), 64, 64, 3))
    for i, row in enumerate(rows):
        images[i] = rasterize(row)
    images.flush()
    return images


class ImageDataset:
    """Only pixels and positional indices can enter the autoencoder path."""
    def __init__(self, images, indices):
        self.images = images
        self.indices = np.asarray(indices, dtype=np.int64)

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        import torch
        image = np.array(self.images[self.indices[index]], dtype=np.float32, copy=True)
        return torch.from_numpy(image.transpose(2, 0, 1).copy()) / 255.0
