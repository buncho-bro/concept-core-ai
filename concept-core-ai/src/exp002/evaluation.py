"""Inherited probe mathematics; one seen-only fit followed by two Test evaluations."""
import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from exp001.evaluation import TrainScaler, select_classifier, pixel_features
from .config import ACTIVE_SPLITS


def evaluate_classifier(features, labels, class_order, seed, failure_flag="PROBE_FAILED"):
    if set(features) != set(ACTIVE_SPLITS) or set(labels) != set(ACTIVE_SPLITS):
        raise ValueError("Expected exactly four active splits; Reserved is prohibited")
    width = np.asarray(features["train"]).shape[1]
    for split in ACTIVE_SPLITS:
        x, y = np.asarray(features[split]), np.asarray(labels[split])
        if x.ndim != 2 or x.shape[1] != width or len(x) != len(y) or not len(y):
            raise ValueError("Malformed probe split")
        if not set(y).issubset(class_order):
            raise ValueError("Unknown class label")
    result = {"class_order": list(class_order), "chance_level": 1 / 3, "converged": False}
    # Missing/non-finite downstream evidence is not a failure of AE execution.
    if not all(np.isfinite(features[s]).all() for s in ACTIVE_SPLITS):
        return {**result, "flag": failure_flag, "reason": "Non-finite evaluation features"}
    scaler = TrainScaler.fit(features["train"])
    result["scaler"] = {**scaler.as_dict(), "fit_split": "seen_train"}
    if not scaler.keep.any():
        return {**result, "flag": failure_flag, "reason": "No retained dimensions", "candidates": []}
    train, validation = scaler.transform(features["train"]), scaler.transform(features["validation"])
    model, candidates = select_classifier(train, labels["train"], validation, labels["validation"], seed)
    result["candidates"] = candidates
    if model is None:
        return {**result, "flag": failure_flag, "reason": "All C candidates did not converge"}
    result.update(selected_C=float(model.C), converged=True, coefficients=model.coef_,
                  intercept=model.intercept_, estimator_classes=model.classes_)
    for split in ACTIVE_SPLITS:
        x = train if split == "train" else validation if split == "validation" else scaler.transform(features[split])
        prediction = model.predict(x)
        result[split] = {"accuracy": float(accuracy_score(labels[split], prediction)),
            "balanced_accuracy": float(balanced_accuracy_score(labels[split], prediction)),
            "confusion_matrix": confusion_matrix(labels[split], prediction, labels=list(class_order)),
            "predictions": prediction}
    return result
