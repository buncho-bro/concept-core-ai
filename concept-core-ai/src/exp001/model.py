"""Exact approved autoencoder; construction is independent of global RNG state."""
import torch
from torch import nn


def configure_precision():
    torch.set_float32_matmul_precision("highest")
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)


class Autoencoder(nn.Module):
    def __init__(self, model_seed):
        super().__init__()
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(model_seed)
            self.encoder = nn.Sequential(
                nn.Conv2d(3, 32, 4, 2, 1, bias=True), nn.ReLU(),
                nn.Conv2d(32, 64, 4, 2, 1, bias=True), nn.ReLU(),
                nn.Conv2d(64, 128, 4, 2, 1, bias=True), nn.ReLU(),
                nn.Conv2d(128, 256, 4, 2, 1, bias=True), nn.ReLU(),
                nn.Flatten(), nn.Linear(4096, 32, bias=True))
            self.decoder = nn.Sequential(
                nn.Linear(32, 4096, bias=True), nn.ReLU(), nn.Unflatten(1, (256, 4, 4)),
                nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=True), nn.ReLU(),
                nn.ConvTranspose2d(128, 64, 4, 2, 1, bias=True), nn.ReLU(),
                nn.ConvTranspose2d(64, 32, 4, 2, 1, bias=True), nn.ReLU(),
                nn.ConvTranspose2d(32, 3, 4, 2, 1, bias=True), nn.Sigmoid())
            self.float()
            generator = torch.Generator(device="cpu").manual_seed(model_seed)
            for layer in self.modules():
                if isinstance(layer, (nn.Conv2d, nn.ConvTranspose2d, nn.Linear)):
                    if layer is self.encoder[-1] or layer is self.decoder[-2]:
                        nn.init.xavier_uniform_(layer.weight, gain=1.0, generator=generator)
                    else:
                        nn.init.kaiming_uniform_(layer.weight, mode="fan_in", nonlinearity="relu", generator=generator)
                    nn.init.zeros_(layer.bias)

    def forward(self, x):
        if x.dtype != torch.float32:
            raise TypeError("Autoencoder input must be FP32")
        return self.decoder(self.encoder(x))
