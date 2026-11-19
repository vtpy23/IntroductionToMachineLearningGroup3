"""Determinism and machine-readable experiment provenance."""
import hashlib
import importlib.metadata
import json
import os
import platform
import random
import subprocess
import sys
from pathlib import Path



def seed_everything(seed: int) -> None:
    """Seed Python, NumPy and PyTorch and select deterministic CUDA operations."""
    import numpy as np
    import torch
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True, warn_only=True)


def sha256_file(path) -> str:
    """Return a streaming SHA-256 digest of the file at ``path``."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def provenance() -> dict:
    """Return environment, command, git revision and dirty-state metadata."""
    import numpy as np
    import torch
    def git(*args):
        try:
            return subprocess.check_output(["git", *args], text=True, encoding="utf-8").strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    manifest = {p.as_posix(): sha256_file(p) for folder in ["src", "scripts", "configs"]
                for p in Path(folder).rglob("*") if p.suffix in {".py", ".json", ".ps1", ".mjs"}}
    packages = {}
    for package in ["numpy", "scipy", "torch", "torchvision", "wandb", "huggingface-hub", "pyarrow", "Pillow"]:
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None
    return {"python": sys.version, "platform": platform.platform(), "source_sha256": manifest, "packages": packages,
            "torch": torch.__version__, "numpy": np.__version__,
            "cuda_available": torch.cuda.is_available(), "cuda_runtime": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "command": sys.argv, "git_commit": git("rev-parse", "HEAD"),
            "git_dirty": bool(git("status", "--porcelain"))}


def write_json(path, value) -> None:
    """Write UTF-8 JSON atomically, creating parent directories if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    temp.replace(path)
