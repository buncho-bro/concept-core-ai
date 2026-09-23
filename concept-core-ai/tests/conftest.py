import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import pytest
import torch
from exp001.data import generate_metadata, assign_splits

torch.set_num_threads(1)


@pytest.fixture(scope="session")
def metadata():
    return assign_splits(generate_metadata(57), 81)
