"""Resume must preserve the actual optimization/augmentation trajectory."""
import copy

import numpy as np
import pytest
import torch
from torch import nn

from scripts import run
from src.utils.reproducibility import seed_everything


class TinyClassifier(nn.Module):
    def __init__(self, classes):
        super().__init__()
        self.linear = nn.Linear(3 * 32 * 32, classes)

    def forward(self, x):
        return self.linear(x.flatten(1))


def test_resumed_training_matches_uninterrupted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run, "CifarResNet32", TinyClassifier)
    rng = np.random.RandomState(3)
    data = {"train_images": rng.randint(0, 256, (8, 32, 32, 3), dtype=np.uint8),
            "train_labels": np.array([0, 1] * 4),
            "test_images": rng.randint(0, 256, (4, 32, 32, 3), dtype=np.uint8),
            "test_labels": np.array([0, 1] * 2),
            "class_order": list(range(100)), "metadata": {"revision": "unit-test"}}
    config = {"seed": 5, "dataset": {}, "protocol": {"base_classes": 2},
              "training": {"epochs": 2, "batch_size": 4, "workers": 0,
                           "lr": 0.01, "milestones": [1], "augment": True}}
    seed_everything(5)
    full = run.train_backbone(config, data, tmp_path / "full.pt", "cpu")

    class Interrupt:
        run = None
        def log(self, values, step):
            if step == 2:
                raise RuntimeError("simulated interruption")

    seed_everything(5)
    with pytest.raises(RuntimeError, match="simulated"):
        run.train_backbone(config, data, tmp_path / "resumed.pt", "cpu", Interrupt())
    assert torch.load(tmp_path / "resumed.pt", weights_only=False)["epoch"] == 1
    seed_everything(5)
    resumed = run.train_backbone(config, data, tmp_path / "resumed.pt", "cpu")
    for key, value in full.state_dict().items():
        torch.testing.assert_close(value, resumed.state_dict()[key], rtol=0, atol=0)
