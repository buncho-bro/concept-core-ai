import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import torch

from exp002 import baseline
from exp002.performance import Performance
from exp002.training import make_loader


def process_manifest(tmp_path, performance=None):
    path = tmp_path / "baseline"
    path.mkdir()
    manifest = {"schema_version": baseline.SCHEMA_VERSION, "frozen": True,
                "frozen_performance": performance or Performance(omp_threads=4, mkl_threads=3).as_dict()}
    manifest = baseline._with_hash(manifest, "manifest_hash")
    (path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return path


def run_guard(path, omp, mkl):
    project = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment.update(OMP_NUM_THREADS=str(omp), MKL_NUM_THREADS=str(mkl),
                       PYTHONPATH=str(project / "src"))
    return subprocess.run([sys.executable, "-m", "exp002.formal_worker", "--baseline", str(path),
                           "--validate-only"], cwd=project, env=environment, text=True,
                          capture_output=True, check=False)


def test_cli_entry_import_is_lightweight_before_launcher_decision():
    project = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(project / "src")
    script = ("import json,sys; import exp002.cli; "
              "print(json.dumps(sorted(set(n.split('.')[0] for n in sys.modules) "
              "& {'numpy','torch','scipy','sklearn'})))")
    result = subprocess.run([sys.executable, "-c", script], cwd=project, env=environment,
                            text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == []


def test_fresh_worker_validates_before_scientific_native_imports(tmp_path):
    result = run_guard(process_manifest(tmp_path), 4, 3)
    assert result.returncode == 0, result.stderr
    provenance = json.loads(result.stdout)
    assert provenance["observed"] == {"OMP_NUM_THREADS": "4", "MKL_NUM_THREADS": "3"}
    assert provenance["validated_before_scientific_imports"] is True
    assert provenance["native_modules_loaded_before_guard"] == []


@pytest.mark.parametrize("omp,mkl,name", [(1, 3, "OMP_NUM_THREADS"), (4, 1, "MKL_NUM_THREADS")])
def test_fresh_worker_rejects_process_start_mismatch(tmp_path, omp, mkl, name):
    result = run_guard(process_manifest(tmp_path), omp, mkl)
    assert result.returncode != 0
    assert "process-start environment mismatch" in result.stderr
    assert name in result.stderr


def test_formal_torch_threads_are_applied_and_verified(monkeypatch):
    state = {"threads": 1, "interop": 1}
    monkeypatch.setenv("OMP_NUM_THREADS", "4")
    monkeypatch.setenv("MKL_NUM_THREADS", "3")
    monkeypatch.setattr(torch, "set_num_threads", lambda value: state.update(threads=value))
    monkeypatch.setattr(torch, "get_num_threads", lambda: state["threads"])
    monkeypatch.setattr(torch, "set_num_interop_threads", lambda value: state.update(interop=value))
    monkeypatch.setattr(torch, "get_num_interop_threads", lambda: state["interop"])
    performance = Performance(torch_threads=5, torch_interop_threads=2, omp_threads=4, mkl_threads=3)
    provenance = {"required": {"OMP_NUM_THREADS": "4", "MKL_NUM_THREADS": "3"},
                  "observed": {"OMP_NUM_THREADS": "4", "MKL_NUM_THREADS": "3"},
                  "validated_before_scientific_imports": True}
    assert performance.apply_formal(provenance) == {"torch_threads": 5, "torch_interop_threads": 2}


def test_formal_torch_application_rejects_false_process_start_provenance(monkeypatch):
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.setenv("MKL_NUM_THREADS", "1")
    with pytest.raises(ValueError, match="process-start"):
        Performance(omp_threads=4, mkl_threads=3).apply_formal({"required": {}, "observed": {}})


def test_dataloader_uses_both_frozen_worker_knobs():
    performance = Performance(num_workers=1, persistent_workers=True)
    loader = make_loader(torch.utils.data.TensorDataset(torch.zeros(2, 1)), 123, performance=performance)
    assert loader.num_workers == 1
    assert loader.persistent_workers is True
