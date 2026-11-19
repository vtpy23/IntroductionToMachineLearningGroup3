"""Plan-only by default; a later approved activation refit and real C logging."""
import argparse
import json
from pathlib import Path
import torch
from scripts.run import load_config, run_incremental
from src.utils.reproducibility import sha256_file
from src.utils.tracking import Tracker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/proposed_activation_control.json")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--tracking", choices=["online", "offline", "disabled"], default="offline")
    args = parser.parse_args(); plan = load_config(args.config)
    reference_seconds = 0
    for seed in plan["seeds"]:
        src = Path("outputs/core-seed0") if seed == 0 else Path(f"outputs/multiseed-20261119/core-seed{seed}")
        reference_seconds += json.loads((src / "dsal-k5/summary.json").read_text())["elapsed_seconds"] * len(plan["activations"])
    print(json.dumps({"plan_only": not args.execute, "runs": len(plan["seeds"]) * len(plan["activations"]),
                      "reference_elapsed_seconds": reference_seconds,
                      "scope": plan["scope"], "warning": "Requires 8192 FP64 refits; obtain user agreement first."}))
    if not args.execute: return
    root = Path(plan["output"])
    if root.exists(): raise SystemExit("Choose a fresh output root; do not overwrite completed or partial evidence")
    for seed in plan["seeds"]:
        src = Path("outputs/core-seed0") if seed == 0 else Path(f"outputs/multiseed-20261119/core-seed{seed}")
        cache = json.loads((src / "feature_cache.json").read_text())
        assert sha256_file(cache["path"]) == cache["sha256"]
        features = torch.load(cache["path"], map_location="cpu", weights_only=False)
        baseline = torch.load(src / "acil-k5/classifier.pt", map_location="cpu", weights_only=False)
        for activation in plan["activations"]:
            folder = root / f"seed{seed}" / activation; folder.mkdir(parents=True, exist_ok=False)
            config = load_config(src / "dsal-k5/config.json")
            config.pop("provenance", None); config.pop("feature_identity", None)
            config["analytic"]["activation"] = activation
            config["evaluate_ratios"] = plan["ratios"]
            config["output"] = folder.as_posix(); config["tracking"] = plan["tracking"]
            assert sha256_file(config["training"]["checkpoint"]) == features["identity"]["checkpoint_sha256"]
            summary = run_incremental(config, features, folder, args.tracking)
            current = torch.load(folder / "classifier.pt", map_location="cpu", weights_only=False)
            assert torch.equal(current["projection"], baseline["projection"])
            torch.testing.assert_close(current["main"], baseline["main"], rtol=1e-12, atol=1e-12)
            ratios = json.loads((folder / "ratio_sweep.json").read_text())
            expected = json.loads((src / "acil-k5/summary.json").read_text())["last_accuracy"]
            assert abs(ratios[0]["accuracy"] - expected) < 1e-10
            tracker = Tracker(root / f"seed{seed}" / (activation + "-C-analysis"),
                              {**config, "parent_run_id": summary["wandb_run_id"],
                               "classifier_sha256": sha256_file(folder / "classifier.pt"),
                               "scope": "Final-phase C sweep of a newly refitted activation; no A-bar for these C values"},
                              "lab1-reproduction", args.tracking)
            if tracker.run is not None: tracker.run.define_metric("sensitivity/*", step_metric="sensitivity/C")
            for step, row in enumerate(ratios):
                tracker.log({"sensitivity/C": row["ratio"], **{"sensitivity/"+k: v for k, v in row.items() if k != "ratio"}}, step)
            tracker.finish({"completed": True, "points": len(ratios), "seed": seed, "main_matches_ACIL": True})


if __name__ == "__main__": main()
