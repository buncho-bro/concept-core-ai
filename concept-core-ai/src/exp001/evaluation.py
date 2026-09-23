"""One train/validation selection path shared by probes and pixel controls."""
from dataclasses import dataclass
import warnings
import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from threadpoolctl import threadpool_limits
from .config import C_GRID


@dataclass
class TrainScaler:
    mean: np.ndarray
    std: np.ndarray
    keep: np.ndarray

    @classmethod
    def fit(cls, train):
        train = np.asarray(train, dtype=np.float64)
        if train.ndim != 2 or not len(train) or not np.isfinite(train).all():
            raise ValueError("Scaler requires finite nonempty training features")
        std = train.std(axis=0, ddof=0)
        return cls(train.mean(axis=0), std, std >= 1e-8)

    def transform(self, x):
        x = np.asarray(x, dtype=np.float64)
        return (x[:, self.keep] - self.mean[self.keep]) / self.std[self.keep]

    def as_dict(self):
        return {"mean": self.mean, "std": self.std, "keep": self.keep,
                "excluded_dimensions": np.flatnonzero(~self.keep), "ddof": 0, "fit_split": "train"}


def classifier(C, seed):
    # In scikit-learn 1.6, lbfgs with >=3 classes uses multinomial loss.
    return LogisticRegression(C=C, penalty="l2", solver="lbfgs", max_iter=1000, tol=1e-6,
                              fit_intercept=True, class_weight=None, random_state=seed)


def select_classifier(train, train_y, validation, validation_y, seed):
    """This function has no Test argument: Test cannot influence C selection."""
    candidates, selected, best_accuracy = [], None, -np.inf
    with threadpool_limits(limits=1):
        for C in C_GRID:
            model = classifier(C, seed)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ConvergenceWarning)
                model.fit(train, train_y)
            converged = not any(issubclass(w.category, ConvergenceWarning) for w in caught)
            converged = converged and np.isfinite(model.coef_).all() and np.isfinite(model.intercept_).all()
            accuracy = float(accuracy_score(validation_y, model.predict(validation))) if converged else None
            candidates.append({"C": C, "converged": bool(converged), "n_iter": model.n_iter_.tolist(),
                               "validation_accuracy": accuracy, "warnings": [str(w.message) for w in caught]})
            # Sorted C grid and strict comparison implements smallest-C tie breaking.
            if converged and accuracy > best_accuracy:
                selected, best_accuracy = model, accuracy
    return selected, candidates


def evaluate_classifier(features, labels, class_order, seed, failure_flag="PROBE_FAILED"):
    scaler = TrainScaler.fit(features["train"])
    result = {"class_order": list(class_order), "chance_level": 1/3, "scaler": scaler.as_dict()}
    if not scaler.keep.any():
        return {**result, "flag": failure_flag, "reason": "No retained features", "candidates": []}
    train = scaler.transform(features["train"])
    validation = scaler.transform(features["validation"])
    model, candidates = select_classifier(train, labels["train"], validation, labels["validation"], seed)
    result["candidates"] = candidates
    if model is None:
        return {**result, "flag": failure_flag, "reason": "All C candidates did not converge"}
    result.update(selected_C=float(model.C), coefficients=model.coef_, intercept=model.intercept_,
                  estimator_classes=model.classes_)
    # Only the selected, already fitted model sees Test. No train+validation refit.
    transformed = {"train": train, "validation": validation, "test": scaler.transform(features["test"])}
    for split, x in transformed.items():
        prediction = model.predict(x)
        result[f"{split}_accuracy"] = float(accuracy_score(labels[split], prediction))
        result[f"{split}_balanced_accuracy"] = float(balanced_accuracy_score(labels[split], prediction))
        result[f"{split}_predictions"] = prediction
    result["test_confusion_matrix"] = confusion_matrix(labels["test"], result["test_predictions"], labels=list(class_order))
    return result


def pixel_features(images, kind):
    images = np.asarray(images, dtype=np.float64)
    if kind == "simple_image_statistics":
        means = images.mean(axis=(1, 2))
        stds = images.std(axis=(1, 2), ddof=0)
        foreground = (images.sum(axis=3) > 0).mean(axis=(1, 2))[:, None]
        return np.concatenate((means, stds, foreground), axis=1)
    if kind == "raw_pixel_linear":
        return (images.transpose(0, 3, 1, 2) / 255).reshape(len(images), 12288)
    raise ValueError("Unknown pixel baseline")
