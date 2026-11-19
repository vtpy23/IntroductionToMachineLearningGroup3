"""CIFAR-100 downloaded from Hugging Face, with pinned dataset revision."""
import io
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

from src.utils.reproducibility import write_json


def load_cifar100(root="data/cache", revision="main"):
    """Download HF parquet files and return train/test images, labels, provenance.

    Args:
        root: Local cache directory, excluded from Git.
        revision: HF commit SHA (or ``main``, resolved to a SHA before download).
    Returns:
        Dictionary of uint8 NHWC images, int64 fine labels, and dataset metadata.
    """
    from huggingface_hub import HfApi, hf_hub_download
    import pyarrow.parquet as pq
    dataset_id = "uoft-cs/cifar100"
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    record = root / "dataset.json"
    # Resolve once and retain the exact revision locally, including offline reruns.
    import json
    if revision == "main" and record.exists():
        revision = json.loads(record.read_text(encoding="utf-8"))["revision"]
    elif revision == "main":
        revision = HfApi().dataset_info(dataset_id).sha
    data = {}
    for split in ("train", "test"):
        cache = root / f"cifar100-{revision}-{split}.npz"
        if cache.exists():
            with np.load(cache) as stored:
                data[split + "_images"] = stored["images"]
                data[split + "_labels"] = stored["labels"]
            continue
        path = hf_hub_download(dataset_id, f"cifar100/{split}-00000-of-00001.parquet",
                               repo_type="dataset", revision=revision)
        table = pq.read_table(path, columns=["img", "fine_label"])
        images = np.stack([np.asarray(Image.open(io.BytesIO(item["bytes"])).convert("RGB"))
                           for item in table.column("img").to_pylist()])
        labels = np.array(table.column("fine_label").to_pylist(), dtype=np.int64)
        np.savez(cache, images=images, labels=labels)
        data[split + "_images"], data[split + "_labels"] = images, labels
    data["metadata"] = {"id": dataset_id, "revision": revision, "label": "fine_label",
                        "train_samples": len(data["train_labels"]),
                        "test_samples": len(data["test_labels"]),
                        "url": "https://huggingface.co/datasets/uoft-cs/cifar100",
                        "license_note": "HF card declares unknown; see original CIFAR terms and docs/DATA.md"}
    write_json(record, data["metadata"])
    return data


def class_order(seed=0, explicit=None):
    """Return a validated permutation of the 100 original fine-class labels."""
    order = np.random.RandomState(seed).permutation(100) if explicit is None else np.asarray(explicit)
    if sorted(order.tolist()) != list(range(100)):
        raise ValueError("class_order must be a permutation of 0..99")
    return order


def phase_boundaries(base_classes=50, phases=5, total_classes=100):
    """Return cumulative class counts for base phase and equally sized increments."""
    if not 0 < base_classes < total_classes or phases < 1:
        raise ValueError("invalid base classes or phases")
    if (total_classes - base_classes) % phases:
        raise ValueError("remaining classes must divide evenly among phases")
    step = (total_classes - base_classes) // phases
    return [base_classes + i * step for i in range(phases + 1)]


class ImageDataset(Dataset):
    """Array-backed images with standard CIFAR normalization and optional crop/flip."""
    def __init__(self, images, labels, augment=False):
        from torchvision import transforms as T
        ops = [T.RandomCrop(32, padding=4), T.RandomHorizontalFlip()] if augment else []
        self.transform = T.Compose(ops + [T.ToTensor(), T.Normalize(
            (0.5071, 0.4867, 0.4408), (0.2675, 0.2565, 0.2761))])
        self.images, self.labels = images, labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        return self.transform(Image.fromarray(self.images[i])), int(self.labels[i])
