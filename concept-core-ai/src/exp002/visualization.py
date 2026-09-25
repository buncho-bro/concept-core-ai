"""Nine fixed representatives with both states and independently inspectable metrics."""
from pathlib import Path
import numpy as np
import torch
from exp001.data import ImageDataset
from exp001.training import load_checkpoint
from exp001.visualization import pca_artifacts, plt
from .data import representative_indices
from .artifacts import save_npz, write_json
from .reconstruction import per_image_metrics


def reconstruction_artifacts(model, images, rows, output, device="cpu"):
    output = Path(output)
    ids = representative_indices(rows)
    dataset = ImageDataset(images, ids)
    inputs = torch.stack([dataset[i] for i in range(9)]).to(device)
    arrays = {"sample_ids": np.asarray([rows[i]["sample_id"] for i in ids]),
              "split": np.asarray([rows[i]["split"] for i in ids]),
              "color": np.asarray([rows[i]["color"] for i in ids]),
              "shape": np.asarray([rows[i]["shape"] for i in ids]), "input": inputs.cpu().numpy()}
    metrics = {"sample_ids": arrays["sample_ids"], "split": arrays["split"],
               "color": arrays["color"], "shape": arrays["shape"]}
    with torch.inference_mode(), torch.autocast(device_type=torch.device(device).type, enabled=False):
        metrics["zero"] = {k: v.cpu().numpy() for k, v in per_image_metrics(torch.zeros_like(inputs), inputs).items()}
        for state in ("initial", "final"):
            load_checkpoint(model, output / f"{state}.pt", device)
            predictions = model(inputs)
            arrays[f"{state}_reconstruction"] = predictions.cpu().numpy()
            arrays[f"{state}_absolute_error"] = (predictions - inputs).abs().cpu().numpy()
            metrics[state] = {k: v.cpu().numpy() for k, v in per_image_metrics(predictions, inputs).items()}
    save_npz(output / "representatives.npz", **arrays)
    write_json(output / "representative_metrics.json", metrics)
    fig, axes = plt.subplots(5, 9, figsize=(18, 10), squeeze=False)
    names = ("input", "initial_reconstruction", "final_reconstruction", "initial_absolute_error", "final_absolute_error")
    for column in range(9):
        for row, name in enumerate(names):
            values = np.nan_to_num(arrays[name][column], nan=0, posinf=1, neginf=0)
            axes[row, column].imshow(np.clip(values.transpose(1, 2, 0), 0, 1))
            axes[row, column].axis("off")
            if column == 0:
                axes[row, column].set_ylabel(name)
        axes[0, column].set_title(f"{arrays['sample_ids'][column]}\n{arrays['split'][column]}\n"
                                 f"{arrays['color'][column]} {arrays['shape'][column]}", fontsize=8)
    fig.tight_layout()
    fig.savefig(output / "representatives.png", dpi=140)
    plt.close(fig)
