from copy import deepcopy
import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader
from exp001.training import ExperimentalFailure
from exp001.artifacts import read_json
from exp002.reconstruction import per_image_metrics, balanced_loss, reconstruction_metrics, sanity_ratios
from exp002.data import SplitDataset
from exp002.config import SEEN, HELDOUT, ACTIVE_SPLITS
from exp002.training import train, make_loader, Autoencoder, extract_latent, load_checkpoint
from exp002.performance import Performance
from exp002.runner import export_states


def unequal_area_images():
    images = torch.zeros(2, 3, 1, 4)
    images[0, :, :, 0] = 1
    images[1, :, :, :3] = .5
    return images


def test_hand_calculated_per_image_first_loss_zero_and_gradient():
    target = unequal_area_images()
    predicted = torch.zeros_like(target, requires_grad=True)
    metrics = per_image_metrics(predicted, target)
    np.testing.assert_allclose(metrics["foreground_MSE"].detach(), [1, .25])
    np.testing.assert_allclose(metrics["background_MSE"].detach(), [0, 0])
    np.testing.assert_allclose(metrics["balanced_reconstruction_loss"].detach(), [.5, .125])
    assert balanced_loss(predicted, target).item() == .3125
    pooled = ((target**2).sum() / ((target.sum(1) > 0).sum() * 3) * .5).item()
    assert pooled == .21875 != .3125
    balanced_loss(predicted, target).backward()
    assert predicted.grad[0, 0, 0, 0].item() == pytest.approx(-1/6)
    assert predicted.grad[1, 0, 0, 0].item() == pytest.approx(-.5/18)
    model = lambda x: torch.zeros_like(x)
    class Zero(torch.nn.Module):
        def forward(self, x): return model(x)
    for batch_size in (1, 2):
        loader = DataLoader(target, batch_size=batch_size)
        assert reconstruction_metrics(None, loader) == reconstruction_metrics(Zero(), loader)
        assert reconstruction_metrics(None, loader)["balanced_reconstruction_loss"] == .3125
    nonzero = per_image_metrics(torch.full_like(target, .25), target)
    assert nonzero["balanced_reconstruction_loss"].mean().item() == .1875
    assert sanity_ratios({"balanced_reconstruction_loss": .25, "foreground_MSE": .5},
                         {"balanced_reconstruction_loss": .3125, "foreground_MSE": .625}) == {"balanced_ratio": .8, "foreground_ratio": .8}


@pytest.mark.parametrize("value", [0, 1, float("nan"), 255])
def test_invalid_target_has_no_fallback_mathematics(value):
    x = torch.full((1, 3, 2, 2), float(value))
    with pytest.raises(ValueError):
        balanced_loss(torch.zeros_like(x), x)


def tiny_datasets():
    rows = [{"sample_id": 0, "color": "red", "shape": "circle", "split": "train"},
            {"sample_id": 1, "color": "red", "shape": "triangle", "split": "train"},
            {"sample_id": 2, "color": "red", "shape": "circle", "split": "validation"}]
    rows += [{"sample_id": i+3, "color": c, "shape": s, "split": "seen_test" if (c, s) in SEEN else "heldout_test"}
             for i, (c, s) in enumerate((*SEEN, *HELDOUT))]
    images = np.zeros((len(rows), 64, 64, 3), dtype=np.float32)
    for i in range(len(rows)):
        images[i, 24:32+i, 25:36, i % 3] = 230
    indices = {s: np.asarray([i for i, r in enumerate(rows) if r["split"] == s]) for s in ACTIVE_SPLITS}
    datasets = {s: SplitDataset(images, rows, ids, s) for s, ids in indices.items()}
    return images, rows, indices, datasets


def test_real_autoencoder_50_epoch_fixture_and_export(tmp_path):
    images, rows, indices, datasets = tiny_datasets()
    model = Autoencoder(72)
    initial = deepcopy(model.state_dict())
    history = train(model, datasets["train"], datasets["validation"], 73, tmp_path)
    assert len(history) == 50 and [h["epoch"] for h in history] == list(range(1, 51))
    start, final = (torch.load(tmp_path/f"{s}.pt", weights_only=True) for s in ("initial", "final"))
    assert start["epoch"] == 0 and not start["optimizer_state_dict"]["state"]
    assert all(torch.equal(initial[k], start["model_state_dict"][k]) for k in initial)
    assert final["epoch"] == 50 and all(int(v["step"]) == 50 for v in final["optimizer_state_dict"]["state"].values())
    metrics = export_states(model, images, datasets, indices, rows, 73, tmp_path)
    assert set(metrics["initial"]) == {"seen_test", "heldout_test"}
    for state in ("initial", "final"):
        for split in ACTIVE_SPLITS:
            saved = np.load(tmp_path / "latent" / f"{state}_{split}.npz")
            assert saved["latent"].shape == (len(indices[split]), 32)
        load_checkpoint(model, tmp_path / f"{state}.pt")
        before = deepcopy(model.state_dict())
        a, b = extract_latent(model, datasets["seen_test"], 73), extract_latent(model, datasets["seen_test"], 73)
        np.testing.assert_array_equal(a, b)
        assert all(not p.requires_grad for p in model.parameters())
        assert all(torch.equal(before[k], model.state_dict()[k]) for k in before)
    reps = np.load(tmp_path / "representatives.npz")
    assert len(reps["sample_ids"]) == 9
    rm = read_json(tmp_path / "representative_metrics.json")
    for state in ("initial", "final"):
        np.testing.assert_array_equal(reps[f"{state}_absolute_error"], np.abs(reps[f"{state}_reconstruction"] - reps["input"]))
        expected = per_image_metrics(torch.from_numpy(reps[f"{state}_reconstruction"]), torch.from_numpy(reps["input"]))
        for key, values in expected.items():
            np.testing.assert_array_equal(values, rm[state][key])
    assert (tmp_path / "representatives.png").exists()
    assert read_json(tmp_path / "reconstruction_metrics.json") == metrics


def test_train_rejects_heldout_and_reserved_before_checkpoint(tmp_path):
    _, _, _, datasets = tiny_datasets()
    for split in ("validation", "seen_test", "heldout_test"):
        with pytest.raises(ValueError, match="Seen Train"):
            train(Autoencoder(74), datasets[split], datasets["validation"], 75, tmp_path)
    with pytest.raises(ValueError):
        train(Autoencoder(74), datasets["train"], datasets["heldout_test"], 75, tmp_path)
    assert not list(tmp_path.iterdir())


def test_loader_fixed_math_performance_controls_and_order():
    _, _, _, datasets = tiny_datasets()
    for perf in (Performance(), Performance(num_workers=1, persistent_workers=True)):
        a = make_loader(datasets["train"], 77, True, perf)
        assert a.batch_size == 128 and not a.drop_last
        assert a.num_workers == perf.num_workers and a.persistent_workers == perf.persistent_workers
    a, b = make_loader(datasets["train"], 77, True), make_loader(datasets["train"], 77, True)
    assert all(torch.equal(x, y) for x, y in zip(a, b))
    with pytest.raises(ValueError): Performance(num_workers=0, persistent_workers=True)


def test_training_numerical_failure_preserves_initial(tmp_path):
    _, _, _, datasets = tiny_datasets()
    model = torch.nn.Conv2d(3, 3, 1)
    with torch.no_grad(): model.weight.fill_(float("nan"))
    with pytest.raises(ExperimentalFailure, match="Non-finite"):
        train(model, datasets["train"], datasets["validation"], 77, tmp_path)
    assert (tmp_path / "initial.pt").exists() and not (tmp_path / "final.pt").exists()


def test_training_deterministic_and_validation_cannot_select_weights(tmp_path):
    images, rows, ids, datasets = tiny_datasets()
    changed = images.copy()
    changed[ids["validation"]] *= .1
    alternative = SplitDataset(changed, rows, ids["validation"], "validation")
    states, records = [], []
    for name, validation in (("a", datasets["validation"]), ("b", alternative), ("c", datasets["validation"])):
        output = tmp_path/name; output.mkdir()
        torch.manual_seed(75)
        model = torch.nn.Sequential(torch.nn.Conv2d(3, 3, 1), torch.nn.Sigmoid())
        records.append(train(model, datasets["train"], validation, 76, output))
        states.append(deepcopy(model.state_dict()))
    assert records[0] == records[2]
    assert records[0][-1]["validation_loss"] != records[1][-1]["validation_loss"]
    assert all(torch.equal(states[0][k], states[1][k]) and torch.equal(states[0][k], states[2][k]) for k in states[0])
