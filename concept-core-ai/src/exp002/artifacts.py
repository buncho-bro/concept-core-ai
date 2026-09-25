"""Reuse exclusive/atomic storage; fingerprint both experiments and formal sources."""
from pathlib import Path
from exp001.artifacts import (new_directory, write_json, read_json, save_npz, inventory,
    environment, clean_commit, check_integrity, sha256_file)


def implementation_fingerprint(root):
    root = Path(root)
    paths = list((root / "src").rglob("*.py")) + list((root / "tests").rglob("*.py"))
    paths += [root / "pyproject.toml", root / "requirements-lock.txt"]
    paths += [root / "experiments" / exp / name for exp in ("exp001", "exp002") for name in ("spec.md", "decisions.md")]
    return {p.relative_to(root).as_posix(): sha256_file(p) for p in sorted(paths) if p.is_file()}


def require_verification(root, receipt_path):
    receipt = read_json(receipt_path)
    if (receipt.get("experiment_id") != "exp002" or receipt.get("exit_code") != 0
            or receipt.get("implementation") != implementation_fingerprint(root)):
        raise ValueError("Successful Exp002 verification of this implementation is required")
    if receipt.get("environment") != environment():
        raise ValueError("Verification environment does not match runtime")
    return receipt


def require_versions():
    runtime = environment()
    expected = {"numpy": "2.3.5", "torch": "2.7.1", "scipy": "1.15.3", "scikit-learn": "1.6.1",
                "matplotlib": "3.10.3", "threadpoolctl": "3.6.0"}
    if not runtime["python"].startswith("3.12.") or any(runtime["packages"][p].split("+")[0] != v for p, v in expected.items()):
        raise ValueError("Pinned implementation dependency versions are required")
    return runtime
