"""Controlled synthetic tests of DS-AL claims, distinct from image benchmarks."""
import argparse
import time
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from scripts.run import load_config
from src.methods import DualStreamAnalytic
from src.utils.reproducibility import provenance, seed_everything, write_json
from src.utils.tracking import Tracker


def data(seed, classes=10, samples=40, dimension=12):
    """Return fixed synthetic class clusters and independent held-out feature rows."""
    gen = torch.Generator().manual_seed(seed)
    centers = torch.randn(classes, dimension, generator=gen, dtype=torch.float64)
    labels = torch.arange(classes).repeat_interleave(samples)
    train = centers[labels] + torch.randn(len(labels), dimension, generator=gen, dtype=torch.float64)
    test = centers[labels] + torch.randn(len(labels), dimension, generator=gen, dtype=torch.float64)
    return train, labels, test


def phase_dependence(seed, gamma=0.1, buffer=64):
    """Hold samples, order, backbone features and projection fixed; vary only phases."""
    train, labels, test = data(seed)
    models, records = [], []
    for increments in [1, 2, 5]:
        model = DualStreamAnalytic(12, buffer, gamma=gamma, seed=seed, compensation_ratio=0.6)
        boundaries = np.linspace(5, 10, increments + 1, dtype=int).tolist()
        lower = 0
        for classes in boundaries:
            mask = (labels >= lower) & (labels < classes)
            model.fit_phase(train[mask], labels[mask], classes, 128)
            lower = classes
        models.append(model)
        reference = models[0]
        relative = lambda a, b: (torch.linalg.norm(a - b) / torch.linalg.norm(b).clamp_min(1e-15)).item()
        record = {"seed": seed, "increments": increments, "gamma": gamma,
                  "main_relative_difference": relative(model.main.weight, reference.main.weight),
                  "comp_relative_difference": relative(model.comp.weight, reference.comp.weight),
                  "scores_relative_difference": relative(model.predict(test), reference.predict(test)),
                  "accuracy": (model.predict(test).argmax(1) == labels).double().mean().item() * 100}
        records.append(record)
    return records


def ridge_residue(seed):
    """Test X.T @ residual = gamma * W, rather than assuming exact orthogonality."""
    train, labels, _ = data(seed)
    records = []
    for gamma in [0.0001, 0.01, 0.1, 1.0, 10.0, 100.0]:
        model = DualStreamAnalytic(12, 64, gamma=gamma, seed=seed, use_compensation=False)
        model.fit_phase(train, labels, 10, 128)
        x, _ = model.embeddings(train)
        residue = F.one_hot(labels, 10).double() - model.main.predict(x)
        lhs = x.T @ residue
        rhs = gamma * model.main.weight
        records.append({"seed": seed, "gamma": gamma,
                        "cross_residual_norm": torch.linalg.norm(lhs).item(),
                        "gamma_weight_norm": torch.linalg.norm(rhs).item(),
                        "normal_equation_error": torch.linalg.norm(lhs - rhs).item(),
                        "normalized_cross_residual": (torch.linalg.norm(lhs) /
                            (torch.linalg.norm(x) * torch.linalg.norm(residue))).item()})
    return records


def scaling(seed):
    """Measure analytic fitting as buffer width changes, excluding backbone training."""
    train, labels, _ = data(seed)
    records = []
    for width in [64, 128, 256, 512, 1024]:
        model = DualStreamAnalytic(12, width, gamma=0.1, seed=seed)
        started = time.perf_counter()
        model.fit_phase(train, labels, 10, 128)
        records.append({"seed": seed, "buffer_size": width,
                        "fit_seconds": time.perf_counter() - started,
                        "two_correlation_matrices_bytes": 2 * width * width * 8})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/empirics-synthetic")
    parser.add_argument("--tracking", choices=["offline", "online", "disabled"], default="offline")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    args = parser.parse_args()
    torch.set_num_threads(4)
    config = load_config("configs/cifar100_smoke.json")
    for name, experiment in [("phase-dependence", phase_dependence),
                             ("ridge-residue", ridge_residue), ("scaling", scaling)]:
        directory = Path(args.output) / name
        if (directory / "summary.json").exists():
            print(f"Skipping existing mechanism experiment: {directory}"); continue
        settings = {"experiment": name, "seeds": args.seeds,
                    "data": "synthetic fixed-feature Gaussian class clusters; NOT CIFAR reproduction",
                    "tracking": config["tracking"], "provenance": provenance()}
        tracker = Tracker(directory, settings, "lab2-empirics", args.tracking)
        records = []
        for seed in args.seeds:
            seed_everything(seed)
            for row in experiment(seed):
                records.append(row)
                tracker.log(row, len(records))
        write_json(directory / "measurements.json", records)
        tracker.finish({"completed": True, "measurement_count": len(records),
                        "data_kind": "synthetic mechanism test"})
        print(name, records, flush=True)


if __name__ == "__main__":
    main()
