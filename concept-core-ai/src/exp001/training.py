"""Image-only fixed-duration training and separately callable frozen extraction."""
import csv
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from .config import BASELINE
from .data import ImageDataset
from .model import configure_precision


class ExperimentalFailure(Exception):
    """Numerical failure of an otherwise conforming experiment."""


def make_loader(dataset, loader_seed, training=False):
    return DataLoader(dataset, batch_size=128, shuffle=training, drop_last=False,
                      num_workers=0, generator=torch.Generator().manual_seed(loader_seed))


def make_optimizer(model):
    return torch.optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.999), eps=1e-8, weight_decay=0)


def reconstruction_loss(model, loader, device):
    model.eval()
    total, count = 0.0, 0
    with torch.inference_mode(), torch.autocast(device_type=torch.device(device).type, enabled=False):
        for images in loader:
            images = images.to(device=device, dtype=torch.float32)
            loss = nn.functional.mse_loss(model(images), images, reduction="mean")
            if not torch.isfinite(loss):
                raise ExperimentalFailure("Non-finite reconstruction loss")
            total += float(loss) * len(images)
            count += len(images)
    if count == 0:
        raise ValueError("Empty evaluation loader")
    return total / count


def save_checkpoint(path, model, optimizer, epoch, train_loss, validation_loss):
    with Path(path).open("xb") as stream:
        torch.save({"model_state_dict": model.state_dict(), "optimizer_state_dict": optimizer.state_dict(),
                    "epoch": epoch, "training_loss": train_loss, "validation_loss": validation_loss,
                    "model_configuration": BASELINE["model"]}, stream)


def train(model, train_dataset, validation_dataset, loader_seed, output, device="cpu"):
    """Always 50 epochs. Small image fixtures use the same loop, never fewer epochs."""
    configure_precision()
    output = Path(output)
    model.to(device=device, dtype=torch.float32)
    model.requires_grad_(True)
    optimizer = make_optimizer(model)
    train_loader = make_loader(train_dataset, loader_seed, training=True)
    validation_loader = make_loader(validation_dataset, loader_seed)
    save_checkpoint(output / "initial.pt", model, optimizer, 0, None, None)
    records = []
    with (output / "training.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("epoch", "training_loss", "validation_loss", "learning_rate"))
        writer.writeheader()
        for epoch in range(1, 51):
            model.train()
            total, count = 0.0, 0
            for images in train_loader:
                images = images.to(device=device, dtype=torch.float32)
                optimizer.zero_grad(set_to_none=True)
                with torch.autocast(device_type=torch.device(device).type, enabled=False):
                    loss = nn.functional.mse_loss(model(images), images, reduction="mean")
                if loss.dtype != torch.float32 or not torch.isfinite(loss):
                    raise ExperimentalFailure("Non-finite or non-FP32 training loss")
                loss.backward()
                if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
                    raise ExperimentalFailure("Non-finite gradient")
                optimizer.step()
                if any(not torch.isfinite(p).all() for p in model.parameters()):
                    raise ExperimentalFailure("Non-finite parameters")
                total += float(loss.detach()) * len(images)
                count += len(images)
            if count == 0:
                raise ValueError("Empty training data")
            val_loss = reconstruction_loss(model, validation_loader, device)
            row = {"epoch": epoch, "training_loss": total/count,
                   "validation_loss": val_loss, "learning_rate": optimizer.param_groups[0]["lr"]}
            records.append(row)
            writer.writerow(row)
            stream.flush()
    save_checkpoint(output / "final.pt", model, optimizer, 50, records[-1]["training_loss"], records[-1]["validation_loss"])
    return records


def load_checkpoint(model, path, device="cpu"):
    checkpoint = torch.load(path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device=device, dtype=torch.float32)
    model.requires_grad_(False)
    model.eval()
    return checkpoint


def extract_latent(model, dataset, loader_seed, device="cpu"):
    model.eval()
    model.requires_grad_(False)
    values = []
    with torch.inference_mode(), torch.autocast(device_type=torch.device(device).type, enabled=False):
        for images in make_loader(dataset, loader_seed):
            z = model.encoder(images.to(device=device, dtype=torch.float32))
            values.append(z.cpu().numpy())
    latent = np.concatenate(values)
    if not np.isfinite(latent).all():
        raise ExperimentalFailure("Non-finite saved latent")
    return latent
