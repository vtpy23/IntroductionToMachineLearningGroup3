"""Prepare a projection-distribution control; default is plan only.

The --execute flag is for a later explicitly approved refit. This entry point
cannot replace any old output and never trains a new backbone.
"""
import argparse
import copy
import json
import math
from pathlib import Path
from unittest.mock import patch

import torch

from scripts.run import load_config, run_incremental
from src.methods import DualStreamAnalytic
from src.utils.reproducibility import sha256_file


class ProjectionControl(DualStreamAnalytic):
    """Keep all equations unchanged and override only projection distribution."""
    def __init__(self, input_dimension, projection_distribution="normal", **kwargs):
        super().__init__(input_dimension, **kwargs)
        if projection_distribution == "uniform_linear":
            gen = torch.Generator(device="cpu").manual_seed(kwargs["seed"])
            bound = 1 / math.sqrt(input_dimension)
            self.projection.copy_(torch.empty(self.projection.shape, dtype=self.dtype).uniform_(-bound, bound, generator=gen))
        elif projection_distribution != "normal":
            raise ValueError("Unknown projection control")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/proposed_projection_control.json")
    parser.add_argument("--execute", action="store_true", help="Refit only after explicit user approval")
    parser.add_argument("--tracking", choices=["online", "offline", "disabled"], default="offline")
    args = parser.parse_args(); plan = load_config(args.config)
    rows = []
    for seed in plan["seeds"]:
        source = Path("outputs/core-seed0") if seed == 0 else Path(f"outputs/multiseed-20261119/core-seed{seed}")
        for method in plan["methods"]:
            config = load_config(source / method / "config.json")
            summary = json.loads((source / method / "summary.json").read_text(encoding="utf-8"))
            rows.append({"seed": seed, "method": method, "source": str(source),
                         "observed_original_elapsed_seconds": summary["elapsed_seconds"],
                         "target": str(Path(plan["output"]) / f"seed{seed}" / method)})
    print(json.dumps({"plan_only": not args.execute, "runs": rows,
                      "rough_reference_seconds": sum(r["observed_original_elapsed_seconds"] for r in rows),
                      "limit": "Reference cost, not guaranteed duration. No backbone training. 8192 FP64 refits require significant RAM."}, indent=2))
    if not args.execute: return
    if Path(plan["output"]).exists(): raise SystemExit("Choose a fresh output root; existing evidence is protected")
    for row in rows:
        source = Path(row["source"])
        config = load_config(source / row["method"] / "config.json")
        config.pop("provenance", None); config.pop("feature_identity", None)
        config["analytic"]["projection_distribution"] = plan["distribution"]
        config["output"] = row["target"]; config["tracking"] = copy.deepcopy(plan["tracking"])
        config["result_label"] = "Approved projection-distribution control; parent seed/config otherwise unchanged"
        cache = json.loads((source / "feature_cache.json").read_text())
        assert sha256_file(cache["path"]) == cache["sha256"]
        features = torch.load(cache["path"], map_location="cpu", weights_only=False)
        assert sha256_file(config["training"]["checkpoint"]) == features["identity"]["checkpoint_sha256"]
        Path(row["target"]).mkdir(parents=True, exist_ok=False)
        with patch("scripts.run.DualStreamAnalytic", ProjectionControl):
            run_incremental(config, features, row["target"], args.tracking)


if __name__ == "__main__": main()
