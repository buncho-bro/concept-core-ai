from copy import deepcopy
import numpy as np
import pytest
import torch
from torch import nn
from torch.utils.data import RandomSampler, SequentialSampler
from exp001.config import configuration
from exp001.model import Autoencoder, configure_precision
from exp001.data import ImageDataset
from exp001.training import (train, make_loader, make_optimizer, load_checkpoint,
                             extract_latent, reconstruction_loss, ExperimentalFailure)


def test_exact_architecture_and_initialization(monkeypatch):
    calls = []
    kaiming, xavier = nn.init.kaiming_uniform_, nn.init.xavier_uniform_
    def k(*a, **kw):
        if kw.get("nonlinearity") == "relu":
            calls.append(("kaiming", tuple(a[0].shape), kw["mode"], kw["nonlinearity"]))
        return kaiming(*a, **kw)
    def x(*a, **kw):
        calls.append(("xavier",tuple(a[0].shape),kw["gain"]))
        return xavier(*a, **kw)
    monkeypatch.setattr(nn.init, "kaiming_uniform_", k)
    monkeypatch.setattr(nn.init, "xavier_uniform_", x)
    model = Autoencoder(123)
    assert [type(m) for m in model.encoder] == [nn.Conv2d,nn.ReLU]*4 + [nn.Flatten,nn.Linear]
    assert [type(m) for m in model.decoder] == [nn.Linear,nn.ReLU,nn.Unflatten] + [nn.ConvTranspose2d,nn.ReLU]*3 + [nn.ConvTranspose2d,nn.Sigmoid]
    enc = [m for m in model.encoder if isinstance(m, nn.Conv2d)]
    dec = [m for m in model.decoder if isinstance(m, nn.ConvTranspose2d)]
    assert [(m.in_channels,m.out_channels) for m in enc] == [(3,32),(32,64),(64,128),(128,256)]
    assert [(m.in_channels,m.out_channels) for m in dec] == [(256,128),(128,64),(64,32),(32,3)]
    for m in enc+dec:
        assert m.kernel_size == (4,4) and m.stride == (2,2) and m.padding == (1,1)
    assert model.encoder[-1].in_features == 4096 and model.encoder[-1].out_features == 32
    assert model.decoder[0].in_features == 32 and model.decoder[0].out_features == 4096
    assert len(calls) == 10
    assert sum(c[0] == "kaiming" for c in calls) == 8
    assert ("xavier",(32,4096),1.0) in calls and ("xavier",(32,3,4,4),1.0) in calls
    assert sum(p.numel() for p in model.parameters()) == 1646307
    for name,p in model.named_parameters():
        assert p.dtype == torch.float32
        if name.endswith("bias"):
            assert torch.count_nonzero(p) == 0
    with torch.no_grad():
        assert model.encoder(torch.zeros(2,3,64,64)).shape == (2,32)
        output = model(torch.zeros(2,3,64,64))
        assert output.shape == (2,3,64,64) and output.dtype == torch.float32
        assert torch.all((0 <= output) & (output <= 1))
    assert not any(isinstance(m,(nn.Dropout,nn.BatchNorm2d)) for m in model.modules())
    with pytest.raises(TypeError):
        model(torch.zeros(1,3,64,64,dtype=torch.float64))


def test_model_seed_isolated():
    torch.manual_seed(23)
    before = torch.get_rng_state().clone()
    a = Autoencoder(19)
    assert torch.equal(before, torch.get_rng_state())
    torch.manual_seed(981)
    b, c = Autoencoder(19), Autoencoder(20)
    assert all(torch.equal(x,y) for x,y in zip(a.parameters(),b.parameters()))
    assert any(not torch.equal(x,y) for x,y in zip(a.parameters(),c.parameters()))


def test_precision_optimizer_and_loader():
    configure_precision()
    assert torch.get_float32_matmul_precision() == "highest"
    assert not torch.backends.cuda.matmul.allow_tf32 and not torch.backends.cudnn.allow_tf32
    model = Autoencoder(1)
    opt = make_optimizer(model)
    assert isinstance(opt,torch.optim.Adam)
    defaults = opt.defaults
    for key,value in {"lr":.001,"betas":(.9,.999),"eps":1e-8,"weight_decay":0}.items():
        assert defaults[key] == value
    ds = list(range(257))
    first, second = make_loader(ds,12,True), make_loader(ds,12,True)
    assert isinstance(first.sampler,RandomSampler)
    assert first.batch_size == 128 and not first.drop_last
    assert [len(b) for b in first] == [128,128,1]
    assert [b.tolist() for b in make_loader(ds,12,True)] == [b.tolist() for b in second]
    assert [b.tolist() for b in make_loader(ds,12,True)] != [b.tolist() for b in make_loader(ds,13,True)]
    assert isinstance(make_loader(ds,12).sampler,SequentialSampler)
    assert configuration()["training"]["epochs"] == 50


def test_actual_autoencoder_50_epoch_tiny_fixture(tmp_path):
    # Two synthetic images, seed 72, temporary artifacts; never a formal experiment.
    images = np.zeros((2,64,64,3),dtype=np.float32)
    images[:,25:40,25:40,0] = 230
    ds = ImageDataset(images,[0,1])
    model = Autoencoder(72)
    before = deepcopy(model.state_dict())
    records = train(model,ds,ds,73,tmp_path)
    assert len(records) == 50 and [r["epoch"] for r in records] == list(range(1,51))
    initial = torch.load(tmp_path/"initial.pt",weights_only=True)
    final = torch.load(tmp_path/"final.pt",weights_only=True)
    assert initial["epoch"] == 0 and not initial["optimizer_state_dict"]["state"]
    assert all(torch.equal(before[k],initial["model_state_dict"][k]) for k in before)
    assert final["epoch"] == 50
    assert all(int(v["step"]) == 50 for v in final["optimizer_state_dict"]["state"].values())
    assert any(not torch.equal(before[k],final["model_state_dict"][k]) for k in before)
    assert not list(tmp_path.glob("*best*"))
    load_checkpoint(model,tmp_path/"final.pt")
    frozen = deepcopy(model.state_dict())
    latent = extract_latent(model,ds,73)
    assert latent.shape == (2,32) and latent.dtype == np.float32
    assert all(not p.requires_grad for p in model.parameters())
    assert all(torch.equal(frozen[k],model.state_dict()[k]) for k in frozen)
    expected = torch.mean((model(ds[0][None])-ds[0][None])**2).item()
    assert reconstruction_loss(model,make_loader(ds,73),"cpu") == pytest.approx(expected)
    from exp001.runner import export_states
    from exp001.artifacts import read_json
    datasets={s:ds for s in ("train","validation","test")}
    indices={s:np.array([0,1]) for s in datasets}
    losses=export_states(model,datasets,indices,[{"sample_id":901},{"sample_id":902}],73,tmp_path)
    assert set(losses)=={"initial","final"}
    for state in losses:
        assert set(losses[state])==set(datasets)
        for split in datasets:
            with np.load(tmp_path/"latent"/f"{state}_{split}.npz") as artifact:
                assert artifact["latent"].shape==(2,32)
                assert artifact["sample_ids"].tolist()==[901,902]
    assert read_json(tmp_path/"reconstruction_losses.json")==losses


def test_validation_monitoring_cannot_change_training(tmp_path):
    images = torch.full((1,3,64,64),0.4)
    def small():
        m = nn.Sequential(nn.Conv2d(3,3,1),nn.Sigmoid())
        nn.init.constant_(m[0].weight,.1)
        nn.init.zeros_(m[0].bias)
        return m
    a,b = small(),small()
    (tmp_path/"a").mkdir(); (tmp_path/"b").mkdir()
    ra = train(a,images,torch.zeros_like(images),5,tmp_path/"a")
    rb = train(b,images,torch.ones_like(images),5,tmp_path/"b")
    assert all(torch.equal(x,y) for x,y in zip(a.parameters(),b.parameters()))
    assert [r["training_loss"] for r in ra] == [r["training_loss"] for r in rb]
    assert ra[-1]["validation_loss"] != rb[-1]["validation_loss"]


def test_nonfinite_preserves_initial(tmp_path):
    model = nn.Conv2d(3,3,1)
    ds = torch.full((1,3,64,64),float("nan"))
    with pytest.raises(ExperimentalFailure):
        train(model,ds,ds,1,tmp_path)
    assert (tmp_path/"initial.pt").exists() and (tmp_path/"training.csv").exists()
    assert not (tmp_path/"final.pt").exists()
