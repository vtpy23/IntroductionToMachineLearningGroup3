"""Check environment and credentials without printing secrets."""
import importlib.metadata
import importlib.util
import json
import os
import sys


def main():
    from dotenv import load_dotenv
    load_dotenv()
    info = {"python": sys.version, "executable": sys.executable, "packages": {}}
    for package in ["torch", "torchvision", "numpy", "scipy", "wandb", "huggingface-hub", "pyarrow"]:
        try:
            info["packages"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            info["packages"][package] = "MISSING"
    import torch
    info["cuda_available"] = torch.cuda.is_available()
    if torch.cuda.is_available():
        info["gpu"] = torch.cuda.get_device_name(0)
        info["vram_gib"] = torch.cuda.get_device_properties(0).total_memory / 2**30
    info["wandb_key_in_environment"] = bool(os.environ.get("WANDB_API_KEY"))
    info["wandb_entity"] = os.environ.get("WANDB_ENTITY")
    info["wandb_project"] = os.environ.get("WANDB_PROJECT")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
