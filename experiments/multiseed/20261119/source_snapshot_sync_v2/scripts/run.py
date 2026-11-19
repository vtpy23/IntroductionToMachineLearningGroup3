"""End-to-end CIFAR-100 base training, feature extraction and DS-AL evaluation."""
import argparse
import copy
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from src.datasets.cifar100 import ImageDataset, class_order, load_cifar100, phase_boundaries
from src.methods import DualStreamAnalytic
from src.models.resnet import CifarResNet32
from src.utils.reproducibility import provenance, seed_everything, sha256_file, write_json
from src.utils.tracking import Tracker


def load_config(path):
    """Load JSON config and apply non-secret W&B settings from the environment."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    tracking = config.setdefault("tracking", {})
    for key, env in [("entity", "WANDB_ENTITY"), ("project", "WANDB_PROJECT"),
                     ("base_url", "WANDB_BASE_URL")]:
        if os.environ.get(env):
            tracking[key] = os.environ[env]
    return config


def resolve_device(name):
    """Resolve auto device or fail explicitly if CUDA was requested but unavailable."""
    if name == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if name.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable; use scripts/doctor.py")
    return name


def prepare_data(config):
    """Download CIFAR-100, remap class labels and optionally apply balanced smoke limits."""
    settings = config["dataset"]
    data = load_cifar100(settings.get("cache", "data/cache"), settings.get("revision", "main"))
    order = class_order(config.get("class_order_seed", 0), config.get("class_order"))
    inverse = np.argsort(order)
    for split in ("train", "test"):
        labels = inverse[data[split + "_labels"]]
        limit = settings.get(split + "_per_class")
        indices = (np.concatenate([np.flatnonzero(labels == c)[:limit] for c in range(100)])
                   if limit else np.arange(len(labels)))
        data[split + "_images"] = data[split + "_images"][indices]
        data[split + "_labels"] = labels[indices]
    data["class_order"] = order.tolist()
    return data


def make_loader(images, labels, config, training=False):
    """Build a reproducible loader with Windows-compatible worker defaults."""
    settings = config["training"]
    generator = torch.Generator().manual_seed(config["seed"])
    return DataLoader(ImageDataset(images, labels, augment=training and settings.get("augment", True)),
                      batch_size=settings.get("batch_size", 128), shuffle=training,
                      num_workers=settings.get("workers", 0), generator=generator,
                      pin_memory=torch.cuda.is_available())


def train_backbone(config, data, checkpoint, device, tracker=None):
    """Train ResNet-32 on base classes only and atomically checkpoint every epoch.

    Resume restores optimizer, scheduler, RNG and loader generator state. The
    final-epoch model is used, avoiding test-set-based checkpoint selection.
    """
    base = config["protocol"]["base_classes"]
    model = CifarResNet32(base).to(device)
    settings = config["training"]
    signature = {"seed": config["seed"], "class_order": data["class_order"],
                 "dataset_revision": data["metadata"]["revision"], "base_classes": base,
                 "training": settings, "train_per_class": config["dataset"].get("train_per_class")}
    state = None
    if checkpoint.exists():
        state = torch.load(checkpoint, map_location="cpu", weights_only=False)
        if state.get("signature") != signature:
            raise ValueError(f"Checkpoint configuration mismatch: {checkpoint}. Choose a different checkpoint path.")
        model.load_state_dict(state["model"])
        if state["epoch"] >= settings["epochs"]:
            print(f"Reusing completed backbone: {checkpoint}", flush=True)
            return model
    mask = data["train_labels"] < base
    loader = make_loader(data["train_images"][mask], data["train_labels"][mask], config, True)
    test_mask = data["test_labels"] < base
    test_loader = make_loader(data["test_images"][test_mask], data["test_labels"][test_mask], config)
    optimizer = torch.optim.SGD(model.parameters(), lr=settings["lr"], momentum=0.9,
                                weight_decay=settings.get("weight_decay", 5e-4))
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, settings["milestones"], gamma=0.1)
    start_epoch = 0
    if state is not None:
        optimizer.load_state_dict(state["optimizer"])
        scheduler.load_state_dict(state["scheduler"])
        torch.set_rng_state(state["torch_rng"])
        if torch.cuda.is_available() and state.get("cuda_rng") is not None:
            torch.cuda.set_rng_state_all(state["cuda_rng"])
        loader.generator.set_state(state["loader_rng"])
        start_epoch = state["epoch"]
        if tracker and tracker.run is not None:
            # Reconstruct prior completed epoch history in the resumed W&B run.
            # Local JSONL is not appended again, and the resume point is explicit.
            tracker.run.config.update({"resume_from_epoch": start_epoch}, allow_val_change=True)
            history = tracker.directory / "metrics.jsonl"
            if history.exists():
                rows = {int(row["step"]): row for row in
                        (json.loads(line) for line in history.read_text(encoding="utf-8").splitlines())
                        if int(row["step"]) <= start_epoch}
                for step, row in sorted(rows.items()):
                    tracker.run.log({k: v for k, v in row.items() if k != "step"}, step=step)
    criterion = nn.CrossEntropyLoss()
    for epoch in range(start_epoch, settings["epochs"]):
        if Path(".stop-project").exists():
            raise SystemExit("Pause requested by .stop-project; checkpoint retained for resume")
        started = time.perf_counter()
        model.train()
        loss_total = correct = count = 0
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            loss_total += loss.item() * len(labels)
            correct += (logits.argmax(1) == labels).sum().item()
            count += len(labels)
        model.eval()
        test_correct = test_count = 0
        with torch.no_grad():
            for images, labels in test_loader:
                logits = model(images.to(device))
                test_correct += (logits.argmax(1).cpu() == labels).sum().item()
                test_count += len(labels)
        metrics = {"base/epoch": epoch + 1, "base/loss": loss_total / count,
                   "base/train_accuracy": 100 * correct / count,
                   "base/test_accuracy": 100 * test_correct / test_count,
                   "base/lr": optimizer.param_groups[0]["lr"],
                   "base/seconds": time.perf_counter() - started}
        print(json.dumps(metrics), flush=True)
        if tracker:
            tracker.log(metrics, epoch + 1)
        scheduler.step()
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        temporary = checkpoint.with_suffix(".tmp")
        torch.save({"model": model.state_dict(), "epoch": epoch + 1, "signature": signature,
                    "optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict(),
                    "torch_rng": torch.get_rng_state(), "loader_rng": loader.generator.get_state(),
                    "cuda_rng": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None}, temporary)
        temporary.replace(checkpoint)
    return model


@torch.no_grad()
def extract_features(model, config, data, checkpoint, device):
    """Cache deterministic backbone features, keyed by data, transform and weight hash."""
    identity = {"checkpoint_sha256": sha256_file(checkpoint), "dataset": data["metadata"],
                "class_order": data["class_order"], "limits": config["dataset"],
                "transform": "cifar100-normalize-v1", "architecture": "option-a-resnet32"}
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]
    path = Path(config["dataset"].get("cache", "data/cache")) / f"features-{digest}.pt"
    if path.exists():
        write_json(Path(config["output"]) / "feature_cache.json", {"path": path.as_posix(), "sha256": sha256_file(path)})
        return torch.load(path, map_location="cpu", weights_only=False)
    model.eval()
    result = {"identity": identity}
    for split in ("train", "test"):
        loader = make_loader(data[split + "_images"], data[split + "_labels"], config)
        batches = [model.features(images.to(device)).cpu() for images, _ in loader]
        result[split + "_features"] = torch.cat(batches)
        result[split + "_labels"] = torch.from_numpy(data[split + "_labels"])
    torch.save(result, path)
    write_json(Path(config["output"]) / "feature_cache.json", {"path": path.as_posix(), "sha256": sha256_file(path)})
    print(f"Feature cache: {path}", flush=True)
    return result


@torch.no_grad()
def evaluate(model, features, labels, base_classes, batch_size=1024, ratio=None):
    """Return accuracy on seen classes and separate base/new-class accuracies."""
    predictions = torch.cat([model.predict(x, ratio).argmax(1).cpu()
                             for x in features.split(batch_size)])
    correct = predictions == labels
    base = labels < base_classes
    result = {"accuracy": correct.double().mean().item() * 100,
              "base_accuracy": correct[base].double().mean().item() * 100}
    result["novel_accuracy"] = correct[~base].double().mean().item() * 100 if (~base).any() else None
    return result


def run_incremental(config, features, outdir, mode="offline"):
    """Execute complete disjoint class phases and save per-phase evidence and scores."""
    seed_everything(config["seed"])
    torch.set_num_threads(config.get("cpu_threads", 8))
    settings = copy.deepcopy(config["analytic"])
    settings["device"] = resolve_device(settings.get("device", "auto"))
    settings["dtype"] = getattr(torch, settings.get("dtype", "float64"))
    settings["seed"] = config.get("projection_seed", config["seed"])
    model = DualStreamAnalytic(features["train_features"].shape[1], **settings)
    tracker = Tracker(outdir, {**config, "provenance": provenance(),
                              "feature_identity": features["identity"]},
                      config.get("lab", "lab1-reproduction"), mode)
    started = time.perf_counter()
    records = []
    previous = 0
    protocol = config["protocol"]
    counts = phase_boundaries(protocol["base_classes"], protocol["phases"])
    if settings["device"].startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()
    for phase, classes in enumerate(counts):
        train_mask = (features["train_labels"] >= previous) & (features["train_labels"] < classes)
        phase_start = time.perf_counter()
        model.fit_phase(features["train_features"][train_mask], features["train_labels"][train_mask],
                        classes, config.get("analytic_batch_size", 512))
        if settings["device"].startswith("cuda"):
            torch.cuda.synchronize()
        fit_seconds = time.perf_counter() - phase_start
        test_mask = features["test_labels"] < classes
        measured = evaluate(model, features["test_features"][test_mask], features["test_labels"][test_mask],
                            protocol["base_classes"])
        records.append({"phase": phase, "classes": classes, "fit_seconds": fit_seconds, **measured})
        tracker.log({f"cil/{k}": v for k, v in records[-1].items() if v is not None}, phase)
        write_json(Path(outdir) / "phases.json", records)
        print(f"{Path(outdir).name} {json.dumps(records[-1])}", flush=True)
        previous = classes
    sweep = []
    for ratio in config.get("evaluate_ratios", []):
        sweep.append({"ratio": ratio, **evaluate(model, features["test_features"],
                      features["test_labels"], protocol["base_classes"], ratio=ratio)})
    write_json(Path(outdir) / "ratio_sweep.json", sweep)
    torch.save({"main": model.main.weight.cpu(), "comp": model.comp.weight.cpu() if model.comp else None,
                "projection": model.projection.cpu(), "bias": model.bias.cpu(),
                "config": config}, Path(outdir) / "classifier.pt")
    summary = {"average_accuracy": float(np.mean([r["accuracy"] for r in records])),
               "last_accuracy": records[-1]["accuracy"], "base_accuracy": records[-1]["base_accuracy"],
               "novel_accuracy": records[-1]["novel_accuracy"],
               "elapsed_seconds": time.perf_counter() - started,
               "fit_seconds": sum(r["fit_seconds"] for r in records),
               "peak_cuda_bytes": torch.cuda.max_memory_allocated() if settings["device"].startswith("cuda") else None,
               "protocol": config.get("result_label", "configured experiment"), "completed": True,
               "phases": protocol["phases"], "buffer_size": settings["buffer_size"],
               "solver": settings["solver"], "seed": config["seed"]}
    tracker.finish(summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cifar100_core.json")
    parser.add_argument("--stage", choices=["data", "train", "features", "prepare", "analytic", "all", "suite"], default="all")
    parser.add_argument("--tracking", choices=["online", "offline", "disabled"], default="offline")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    config = load_config(args.config)
    seed_everything(config["seed"])
    torch.set_num_threads(config.get("cpu_threads", 8))
    outdir = Path(args.output or config["output"])
    config["output"] = outdir.as_posix()
    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir / "environment.json", provenance())
    if args.stage == "analytic":
        from scripts.suite import run_suite
        cached = json.loads((outdir / "feature_cache.json").read_text(encoding="utf-8"))
        if sha256_file(cached["path"]) != cached["sha256"]:
            raise ValueError("Feature cache hash mismatch")
        features = torch.load(cached["path"], map_location="cpu", weights_only=False)
        run_suite(config, features, outdir, args.tracking)
        return
    data = prepare_data(config)
    if args.stage == "data":
        print(json.dumps(data["metadata"])); return
    device = resolve_device(config["training"].get("device", "auto"))
    checkpoint = Path(config["training"]["checkpoint"])
    tracker = None
    if args.stage in {"train", "prepare", "all", "suite"}:
        tracker = Tracker(outdir / "base-training", {**config, "provenance": provenance()},
                          "lab1-reproduction", args.tracking)
    model = train_backbone(config, data, checkpoint, device, tracker)
    if tracker:
        tracker.finish({"completed": True, "epochs": config["training"]["epochs"],
                        "checkpoint_sha256": sha256_file(checkpoint)})
    if args.stage == "train":
        return
    features = extract_features(model, config, data, checkpoint, device)
    del model, data
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    if args.stage in {"features", "prepare"}:
        return
    if args.stage == "suite":
        from scripts.suite import run_suite
        run_suite(config, features, outdir, args.tracking)
    else:
        print(run_incremental(config, features, outdir / "dsal", args.tracking))


if __name__ == "__main__":
    main()
