"""Explicit, recorded implementation settings; no scientific tuning."""
from dataclasses import asdict, dataclass
import os
import torch


@dataclass(frozen=True)
class Performance:
    torch_threads: int = 1
    torch_interop_threads: int = 1
    num_workers: int = 0
    persistent_workers: bool = False
    omp_threads: int = 1
    mkl_threads: int = 1

    def __post_init__(self):
        for name in ("torch_threads", "torch_interop_threads", "omp_threads", "mkl_threads"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError("Thread counts must be positive integers")
        if type(self.num_workers) is not int or self.num_workers < 0:
            raise ValueError("num_workers must be a nonnegative integer")
        if type(self.persistent_workers) is not bool or (self.persistent_workers and not self.num_workers):
            raise ValueError("persistent_workers requires workers")

    def as_dict(self):
        return asdict(self)

    def _apply_torch(self):
        torch.set_num_threads(self.torch_threads)
        if torch.get_num_interop_threads() != self.torch_interop_threads:
            torch.set_num_interop_threads(self.torch_interop_threads)
        if torch.get_num_threads() != self.torch_threads or torch.get_num_interop_threads() != self.torch_interop_threads:
            raise ValueError("Requested thread configuration was not applied")
        return {"torch_threads": torch.get_num_threads(),
                "torch_interop_threads": torch.get_num_interop_threads()}

    def apply(self):
        """Non-formal/reanalysis setup; formal execution uses apply_formal."""
        os.environ["OMP_NUM_THREADS"] = str(self.omp_threads)
        os.environ["MKL_NUM_THREADS"] = str(self.mkl_threads)
        return self._apply_torch()

    def apply_formal(self, process_start_provenance):
        required = {"OMP_NUM_THREADS": str(self.omp_threads), "MKL_NUM_THREADS": str(self.mkl_threads)}
        if (process_start_provenance.get("required") != required
                or process_start_provenance.get("observed") != required
                or process_start_provenance.get("validated_before_scientific_imports") is not True
                or any(os.environ.get(name) != value for name, value in required.items())):
            raise ValueError("Formal process-start performance provenance mismatch")
        return self._apply_torch()
