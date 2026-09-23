"""Fixed approved research conditions and deterministic seed derivation."""
from copy import deepcopy
from hashlib import sha256

FORMAL_SEEDS = (1001, 1002, 1003, 1004, 1005)
PURPOSES = ("generation", "split", "model", "loader", "probe", "analysis")
COLORS = ("red", "green", "blue")
SHAPES = ("circle", "triangle", "square")
SPLITS = ("train", "validation", "test")
C_GRID = (0.01, 0.1, 1.0, 10.0, 100.0)
NUMPY_VERSION = "2.3.5"
SOURCE_COMMIT = "207bee36f2a5b1b57de2d73d582ef9f890dbe855"
BASELINE = {
    "experiment_id": "exp001",
    "dataset": {"height": 64, "width": 64, "channels": 3,
        "background": [0, 0, 0], "colors": [[230, 25, 25], [25, 230, 25], [25, 25, 230]],
        "channel_noise_inclusive": [-10, 10], "center_inclusive": [26, 38],
        "circumradius_inclusive": [12, 16], "rotation_degrees": [0, 360],
        "circle_rotation": 0.0, "subpixel_offsets": [-0.375, -0.125, 0.125, 0.375],
        "samples_per_combination": 1000, "split_per_combination": [800, 100, 100],
        "rgb_storage": "float32_unnormalized", "augmentation": None},
    "model": {"latent_dim": 32, "channels": [3, 32, 64, 128, 256],
        "kernel": 4, "stride": 2, "padding": 1, "bias": True,
        "relu_initialization": "kaiming_uniform_fan_in_relu",
        "output_initialization": "xavier_uniform_gain_1", "bias_initialization": 0.0,
        "dtype": "float32", "AMP": False, "TF32": False,
        "batch_norm": False, "dropout": False, "latent_normalization": False},
    "training": {"epochs": 50, "batch_size": 128, "loss": "MSE_mean",
        "optimizer": "Adam", "lr": 0.001, "betas": [0.9, 0.999], "eps": 1e-8,
        "weight_decay": 0, "shuffle_train": True, "drop_last": False,
        "scheduler": None, "early_stopping": None, "gradient_clipping": None,
        "regularization": None, "checkpoint_selection": "final_epoch_50"},
    "analysis": {"scaler_fit": "train_only", "std_ddof": 0, "std_threshold": 1e-8,
        "C_grid": list(C_GRID), "solver": "lbfgs", "penalty": "l2",
        "multiclass": "multinomial", "fit_intercept": True, "class_weight": None,
        "max_iter": 1000, "tol": 1e-6, "bootstrap_iterations": 1000,
        "bootstrap_size": 900, "bootstrap_rng": "numpy.Generator(PCG64)",
        "minimum_valid_iterations": 950, "CI": [0.025, 0.975]},
}


def configuration():
    return deepcopy(BASELINE)


def derive_seed(master_seed, purpose):
    if purpose not in PURPOSES or not isinstance(master_seed, int):
        raise ValueError("Invalid seed purpose or master seed")
    return int.from_bytes(sha256(f"exp001|{master_seed}|{purpose}".encode("ascii")).digest()[:4], "big")


def seeds_for(master_seed):
    return {"master_seed": master_seed, **{f"{p}_seed": derive_seed(master_seed, p) for p in PURPOSES}}
