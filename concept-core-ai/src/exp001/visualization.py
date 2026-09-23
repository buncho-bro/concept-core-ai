"""Exploratory PCA and fixed reconstruction displays; never used for classification."""
from pathlib import Path
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from threadpoolctl import threadpool_limits
from .artifacts import save_npz
from .config import COLORS, SHAPES


def pca_artifacts(test_latent, sample_ids, labels, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for dimensions in (2, 3):
        with threadpool_limits(limits=1):
            pca = PCA(n_components=dimensions, svd_solver="full")
            coordinates = pca.fit_transform(np.asarray(test_latent, dtype=np.float64))
        save_npz(output / f"pca_{dimensions}d.npz", coordinates=coordinates, sample_ids=sample_ids,
                 explained_variance=pca.explained_variance_, explained_variance_ratio=pca.explained_variance_ratio_,
                 components=pca.components_, mean=pca.mean_)
        for attribute, classes in (("color", COLORS), ("shape", SHAPES)):
            fig = plt.figure(figsize=(7, 6))
            ax = fig.add_subplot(111, projection="3d" if dimensions == 3 else None)
            for label in classes:
                selected = coordinates[np.asarray(labels[attribute]) == label]
                ax.scatter(*selected.T, label=label, s=9, alpha=0.65)
            ax.set(xlabel="PC1", ylabel="PC2", title=f"Exploratory PCA: {attribute}")
            if dimensions == 3:
                ax.set_zlabel("PC3")
            ax.legend()
            fig.tight_layout()
            fig.savefig(output / f"pca_{dimensions}d_{attribute}.png", dpi=140)
            plt.close(fig)


def reconstruction_artifact(model, dataset, sample_ids, output, device="cpu"):
    # First nine saved Test IDs, independent of labels, errors and model state.
    n = min(9, len(dataset))
    inputs = torch.stack([dataset[i] for i in range(n)]).to(device)
    with torch.inference_mode():
        outputs = model(inputs).cpu().numpy()
    originals = inputs.cpu().numpy()
    save_npz(Path(output) / "reconstruction.npz", sample_ids=np.asarray(sample_ids)[:n], inputs=originals, reconstructions=outputs)
    fig, axes = plt.subplots(2, n, figsize=(n*1.5, 3), squeeze=False)
    for k in range(n):
        axes[0, k].imshow(originals[k].transpose(1, 2, 0))
        axes[1, k].imshow(outputs[k].transpose(1, 2, 0))
        axes[0, k].set_title(str(sample_ids[k]), fontsize=8)
        for ax in axes[:, k]:
            ax.axis("off")
    fig.tight_layout()
    fig.savefig(Path(output) / "reconstruction.png", dpi=140)
    plt.close(fig)
