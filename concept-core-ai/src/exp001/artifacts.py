"""Exclusive artifacts, provenance and integrity checks; never erase a failed run."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
import numpy as np


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path, value, *, replace=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(jsonable(value), ensure_ascii=False, indent=2, allow_nan=False)
    if not replace:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text + "\n")
        return
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".atomic-")
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def new_directory(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    return path


def save_npz(path, **arrays):
    with Path(path).open("xb") as stream:
        np.savez_compressed(stream, **arrays)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(path, excluded=("integrity.json",)):
    path = Path(path)
    return {p.relative_to(path).as_posix(): sha256_file(p) for p in sorted(path.rglob("*"))
            if p.is_file() and p.name not in excluded}


def check_integrity(path):
    path = Path(path)
    expected = read_json(path / "integrity.json")
    if expected != inventory(path):
        raise ValueError("Artifact integrity mismatch")


def environment():
    packages = ("numpy", "torch", "scipy", "scikit-learn", "matplotlib", "threadpoolctl", "pytest")
    return {"python": platform.python_version(), "platform": platform.platform(),
            "packages": {p: importlib.metadata.version(p) for p in packages}}


def implementation_fingerprint(root):
    root = Path(root)
    paths = list((root / "src" / "exp001").glob("*.py")) + list((root / "tests").glob("*.py"))
    paths += [root / "pyproject.toml", root / "requirements-lock.txt"]
    return {p.relative_to(root).as_posix(): sha256_file(p) for p in sorted(paths) if p.exists()}


def clean_commit(root):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
    commit = git("rev-parse", "HEAD")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Formal runs require a clean committed implementation")
    return commit
