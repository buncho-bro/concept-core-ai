"""One per-image-first definition for training, evaluation and zero baselines."""
import numpy as np
import torch

METRICS = ("global_MSE", "foreground_MSE", "background_MSE", "balanced_reconstruction_loss")


def per_image_metrics(prediction, target):
    if prediction.shape != target.shape or target.ndim != 4 or target.shape[1] != 3 or not len(target):
        raise ValueError("Expected nonempty matching NCHW RGB tensors")
    if target.dtype != torch.float32 or prediction.dtype != torch.float32:
        raise ValueError("Reconstruction calculations require FP32")
    if not torch.isfinite(target).all() or torch.any(target < 0) or torch.any(target > 1):
        raise ValueError("Targets must be finite normalized [0,1] RGB")
    foreground = target.sum(dim=1, keepdim=True) > 0
    foreground_count = foreground.sum(dim=(1, 2, 3)) * 3
    background_count = (~foreground).sum(dim=(1, 2, 3)) * 3
    if torch.any(foreground_count == 0) or torch.any(background_count == 0):
        # Valid generated images always contain both. This is a data/technical
        # violation (INVALID), not a new fallback loss or a scientific threshold.
        raise ValueError("Target has no foreground or no background; approved loss is undefined")
    error = (prediction - target).square()
    fg = (error * foreground).sum(dim=(1, 2, 3)) / foreground_count
    bg = (error * ~foreground).sum(dim=(1, 2, 3)) / background_count
    return dict(zip(METRICS, (error.mean(dim=(1, 2, 3)), fg, bg, 0.5 * fg + 0.5 * bg)))


def balanced_loss(prediction, target):
    return per_image_metrics(prediction, target)["balanced_reconstruction_loss"].mean()


def reconstruction_metrics(model, loader, device="cpu"):
    """Accumulate per-image values in fixed order, never average batch means."""
    values = {k: [] for k in METRICS}
    if model is not None:
        model.eval()
    with torch.inference_mode(), torch.autocast(device_type=torch.device(device).type, enabled=False):
        for images in loader:
            images = images.to(device=device, dtype=torch.float32)
            predicted = torch.zeros_like(images) if model is None else model(images)
            metrics = per_image_metrics(predicted, images)
            for key in METRICS:
                values[key].append(metrics[key].cpu().numpy())
    if not values[METRICS[0]]:
        raise ValueError("Empty reconstruction evaluation")
    return {key: float(np.concatenate(parts).astype(np.float64).mean()) for key, parts in values.items()}


def sanity_ratios(final_seen, zero_seen):
    result = {}
    for name, metric in (("balanced_ratio", "balanced_reconstruction_loss"), ("foreground_ratio", "foreground_MSE")):
        numerator, denominator = final_seen.get(metric), zero_seen.get(metric)
        result[name] = (numerator / denominator if isinstance(numerator, (int, float))
            and isinstance(denominator, (int, float)) and np.isfinite([numerator, denominator]).all()
            and denominator > 0 and numerator >= 0 else None)
    return result
