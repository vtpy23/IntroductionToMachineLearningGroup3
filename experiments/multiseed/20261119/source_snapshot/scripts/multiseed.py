"""Run independent base training seeds sequentially with isolated checkpoints."""
import argparse
import copy
import subprocess
import sys
from pathlib import Path

from scripts.run import load_config
from src.utils.reproducibility import write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cifar100_core.json")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--tracking", default="offline", choices=["offline", "online", "disabled"])
    args = parser.parse_args()
    base = load_config(args.config)
    for seed in args.seeds:
        if Path(".stop-project").exists():
            raise SystemExit("Pause requested by .stop-project")
        config = copy.deepcopy(base)
        config["seed"] = seed
        config["class_order_seed"] = seed
        config["output"] = f"outputs/core-seed{seed}"
        config["training"]["checkpoint"] = f"checkpoints/core-seed{seed}-resnet32.pt"
        generated = Path("outputs/pipeline") / f"config-seed{seed}.json"
        write_json(generated, config)
        subprocess.run([sys.executable, "-X", "utf8", "-m", "scripts.run", "--config", str(generated),
                        "--stage", "prepare", "--tracking", args.tracking], check=True)
        cpu = Path(".venv-cpu/Scripts/python.exe")
        analytic_python = str(cpu.resolve()) if cpu.exists() else sys.executable
        subprocess.run([analytic_python, "-X", "utf8", "-m", "scripts.run", "--config", str(generated),
                        "--stage", "analytic", "--tracking", args.tracking], check=True)
        subprocess.run([sys.executable, "-X", "utf8", "-m", "scripts.summarize"], check=True)


if __name__ == "__main__":
    main()
