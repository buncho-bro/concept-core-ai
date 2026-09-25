"""Exp001 optimizer/checkpoints/precision with the approved Exp002 loss."""
import csv
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader
from exp001.model import Autoencoder, configure_precision
from exp001.training import ExperimentalFailure, make_optimizer, save_checkpoint, load_checkpoint
from .performance import Performance
from .reconstruction import balanced_loss, reconstruction_metrics


def make_loader(dataset, loader_seed, training=False, performance=None):
    perf = performance or Performance()
    if training and getattr(dataset, "split", None) != "train":
        raise ValueError("AE optimization requires Seen Train")
    return DataLoader(dataset, batch_size=128, shuffle=training, drop_last=False,
        num_workers=perf.num_workers, persistent_workers=perf.persistent_workers,
        generator=torch.Generator().manual_seed(loader_seed))


def train(model, train_dataset, validation_dataset, loader_seed, output, device="cpu", performance=None):
    if getattr(train_dataset, "split", None) != "train" or getattr(validation_dataset, "split", None) != "validation":
        raise ValueError("AE training/monitoring require Seen Train/Validation only")
    configure_precision()
    output = Path(output)
    model.to(device=device, dtype=torch.float32)
    model.requires_grad_(True)
    optimizer = make_optimizer(model)
    train_loader = make_loader(train_dataset, loader_seed, True, performance)
    validation_loader = make_loader(validation_dataset, loader_seed, False, performance)
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
                    loss = balanced_loss(model(images), images)
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
            if not count:
                raise ValueError("Empty Seen Train")
            validation = reconstruction_metrics(model, validation_loader, device)["balanced_reconstruction_loss"]
            if not np.isfinite(validation):
                raise ExperimentalFailure("Non-finite validation loss")
            record = {"epoch": epoch, "training_loss": total / count, "validation_loss": validation,
                      "learning_rate": optimizer.param_groups[0]["lr"]}
            records.append(record)
            writer.writerow(record)
            stream.flush()
    save_checkpoint(output / "final.pt", model, optimizer, 50, records[-1]["training_loss"], records[-1]["validation_loss"])
    return records


def extract_latent(model, dataset, loader_seed, device="cpu", performance=None):
    model.eval()
    model.requires_grad_(False)
    values = []
    with torch.inference_mode(), torch.autocast(device_type=torch.device(device).type, enabled=False):
        for images in make_loader(dataset, loader_seed, performance=performance):
            values.append(model.encoder(images.to(device=device, dtype=torch.float32)).cpu().numpy())
    # Preserve non-finite evaluation values for diagnostics. Downstream analysis
    # records missing primary evidence with evaluation flags, not run failure.
    return np.concatenate(values)
