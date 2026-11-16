"""Verify independent equations against an isolated official checkout on tiny inputs.

This imports the author's implementation only for output comparison. It neither
copies source into src/ nor uses the official implementation to produce our
reproduction benchmark results.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import torch

from src.methods import DualStreamAnalytic
from src.utils.reproducibility import provenance, write_json
from src.utils.tracking import Tracker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", default="artifacts/reference/official")
    parser.add_argument("--output", default="outputs/reference-comparison")
    parser.add_argument("--tracking", default="offline", choices=["offline", "online", "disabled"])
    args = parser.parse_args()
    reference = Path(args.reference).resolve()
    if not (reference / "analytic" / "DSAL.py").exists():
        raise SystemExit("Clone the official repository into --reference first; see docs/REPRODUCTION.md")
    sys.path.insert(0, str(reference))
    from analytic.DSAL import DSAL
    sha = subprocess.check_output(["git", "-C", str(reference), "rev-parse", "HEAD"], text=True).strip()
    torch.set_num_threads(2)
    generator = torch.Generator().manual_seed(87)
    x = torch.randn(40, 7, generator=generator, dtype=torch.float64)
    y = torch.tensor([0, 1] * 10 + [2, 3] * 10)
    records = []
    for chunk in [20, 4]:
        torch.manual_seed(14)
        official = DSAL(7, expansion_size=13, gamma_main=0.1, gamma_comp=0.1, C=0.6)
        independent = DualStreamAnalytic(7, 13, gamma=0.1, compensation_ratio=0.6, solver="stats")
        independent.projection.copy_(official.buffer.weight.T)
        for lower, upper, classes in [(0, 20, 2), (20, 40, 4)]:
            independent.fit_phase(x[lower:upper], y[lower:upper], classes, batch_size=4)
            for start in range(lower, upper, chunk):
                official.fit(x[start:start + chunk], y[start:start + chunk], increase_size=2)
            official.update()
        records.append({"official_batch_size": chunk,
                        "main_max_abs_difference": (independent.main.weight - official.main_stream.weight).abs().max().item(),
                        "comp_max_abs_difference": (independent.comp.weight - official.comp_stream.weight).abs().max().item(),
                        "scores_max_abs_difference": (independent.predict(x) - official(x)).abs().max().item()})
    from scripts.run import load_config
    settings = load_config("configs/cifar100_smoke.json")["tracking"]
    tracker = Tracker(args.output, {"reference_sha": sha, "provenance": provenance(),
                      "tracking": settings, "data": "tiny synthetic output comparison"},
                      "lab1-reproduction", args.tracking)
    for step, record in enumerate(records):
        tracker.log(record, step)
    write_json(Path(args.output) / "comparison.json", {"reference_sha": sha, "measurements": records})
    write_json("experiments/reproduction/reference-comparison.json", {"reference_sha": sha, "measurements": records})
    tracker.finish({"completed": True, "reference_sha": sha,
                    "scope": "equation verification, not CIFAR benchmark"})
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
