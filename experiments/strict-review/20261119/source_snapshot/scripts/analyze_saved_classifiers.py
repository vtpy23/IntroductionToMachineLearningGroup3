"""Read-only, bounded-memory score analysis of existing CIFAR classifiers.

C occurs only in inference, so its sweep needs no retraining. Check C=0 against
ACIL and C=0.6 against DS-AL before logging any new measured result. Fail closed
on changed feature/checkpoint identity; write only into a fresh analysis folder.
"""
import argparse
import gc
import json
import math
from pathlib import Path
import statistics
import time

import torch

from scripts.run import load_config
from src.utils.reproducibility import provenance, sha256_file, write_json
from src.utils.tracking import Tracker


def accuracy_by_group(predictions, labels, base_classes=50):
    """Return percentage accuracy and counts for balanced or unbalanced groups."""
    correct = predictions.eq(labels)
    result = {}
    for name, mask in [("all", torch.ones_like(correct)), ("base", labels < base_classes),
                       ("novel", labels >= base_classes)]:
        count = int(mask.sum())
        if not count:
            raise ValueError("All evaluation groups must be nonempty")
        result[name + "_accuracy"] = 100 * int(correct[mask].sum()) / count
        result[name + "_count"] = count
    return result


def paired_changes(before, after, labels, base_classes=50):
    """Count corrected/harmed predictions on the same labeled examples."""
    first, second = before.eq(labels), after.eq(labels)
    result = {}
    for name, mask in [("all", torch.ones_like(first)), ("base", labels < base_classes),
                       ("novel", labels >= base_classes)]:
        fixed = int((~first & second & mask).sum())
        harmed = int((first & ~second & mask).sum())
        result[name] = {"corrected": fixed, "harmed": harmed,
                        "net_pp": 100 * (fixed - harmed) / int(mask.sum()),
                        "count": int(mask.sum())}
    return result


def source_directory(seed):
    """Locate completed benchmark artifacts without changing their paths."""
    return Path("outputs/core-seed0") if seed == 0 else Path(f"outputs/multiseed-20261119/core-seed{seed}")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


@torch.no_grad()
def analyze_seed(seed, settings):
    """Compute each projection/score once, then sweep C on final test scores."""
    directory = source_directory(seed)
    cache_info = read(directory / "feature_cache.json")
    cache_path = Path(cache_info["path"])
    assert sha256_file(cache_path) == cache_info["sha256"]
    features = torch.load(cache_path, map_location="cpu", weights_only=False)
    saved = {}; protected = {cache_path.as_posix(): cache_info["sha256"]}
    summaries = {}
    for method in ["acil-k5", "dac-no-plc-k5", "dsal-k5"]:
        folder = directory / method
        for name in ["classifier.pt", "config.json", "summary.json", "phases.json", "metrics.jsonl"]:
            protected[(folder / name).as_posix()] = sha256_file(folder / name)
        config, summaries[method] = read(folder / "config.json"), read(folder / "summary.json")
        assert summaries[method]["completed"] and config["seed"] == seed
        assert config["feature_identity"] == features["identity"]
        assert config["protocol"] == {"base_classes": 50, "phases": 5}
        saved[method] = torch.load(folder / "classifier.pt", map_location="cpu", weights_only=False)
    full = saved["dsal-k5"]
    for method, state in saved.items():
        assert torch.equal(state["projection"], full["projection"]), method
        assert torch.equal(state["bias"], full["bias"]), method
        torch.testing.assert_close(state["main"], full["main"], rtol=1e-12, atol=1e-12)
    assert features["identity"]["dataset"]["revision"] == "aadb3af77e9048adbea6b47c21a81e47dd092ae5"
    checkpoint = Path(full["config"]["training"]["checkpoint"])
    assert sha256_file(checkpoint) == features["identity"]["checkpoint_sha256"]
    protected[checkpoint.as_posix()] = features["identity"]["checkpoint_sha256"]
    labels = features["test_labels"].long()
    assert len(labels) == 10000 and torch.equal(torch.bincount(labels), torch.full((100,), 100))
    main_scores, comp_scores, dac_scores = [], [], []
    started = time.perf_counter()
    for x in features["test_features"].split(settings["batch_size"]):
        z = x.to(full["projection"].dtype) @ full["projection"] + full["bias"]
        main_scores.append(z.relu() @ full["main"])
        activated = z.tanh()
        comp_scores.append(activated @ full["comp"])
        dac_scores.append(activated @ saved["dac-no-plc-k5"]["comp"])
    main, comp, dac = map(torch.cat, [main_scores, comp_scores, dac_scores])
    ratios = []
    for c in settings["ratios"]:
        ratios.append({"ratio": c, **accuracy_by_group((main + c * comp).argmax(1), labels)})
    methods = {"acil-k5": main.argmax(1),
               "dac-no-plc-k5": (main + settings["reference_ratio"] * dac).argmax(1),
               "dsal-k5": (main + settings["reference_ratio"] * comp).argmax(1)}
    for name, pred in methods.items():
        measured = accuracy_by_group(pred, labels)
        for key, old_key in [("all_accuracy", "last_accuracy"), ("base_accuracy", "base_accuracy"), ("novel_accuracy", "novel_accuracy")]:
            assert math.isclose(measured[key], summaries[name][old_key], abs_tol=1e-10), (seed, name, key)
    assert math.isclose(ratios[0]["all_accuracy"], summaries["acil-k5"]["last_accuracy"], abs_tol=1e-10)
    flips = {"dac_minus_acil": paired_changes(methods["acil-k5"], methods["dac-no-plc-k5"], labels),
             "dsal_minus_acil": paired_changes(methods["acil-k5"], methods["dsal-k5"], labels),
             "plc_minus_dac": paired_changes(methods["dac-no-plc-k5"], methods["dsal-k5"], labels)}
    result = {"seed": seed, "ratios": ratios, "paired_prediction_changes": flips,
              "elapsed_seconds": time.perf_counter() - started,
              "feature_identity": features["identity"], "protected_sha256": protected,
              "parent_runs": {m: s["wandb_run_id"] for m, s in summaries.items()},
              "source_summaries_reproduced": True}
    assert all(sha256_file(p) == digest for p, digest in protected.items())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/saved_classifier_sensitivity.json")
    parser.add_argument("--tracking", choices=["disabled", "offline", "online"], default="offline")
    args = parser.parse_args()
    settings = load_config(args.config)
    output = Path(settings["output"])
    if output.exists():
        raise SystemExit("Analysis output exists; select a fresh output path, never append or overwrite.")
    torch.set_num_threads(settings["cpu_threads"])
    rows = []
    for seed in settings["seeds"]:
        result = analyze_seed(seed, settings)
        tracker = Tracker(output / f"saved-C-sensitivity-seed{seed}",
                          {**settings, "seed": seed, "parent_runs": result["parent_runs"],
                           "feature_identity": result["feature_identity"],
                           "source_artifact_sha256": result["protected_sha256"],
                           "provenance": provenance()}, "lab1-reproduction", args.tracking)
        if tracker.run is not None:
            tracker.run.define_metric("sensitivity/*", step_metric="sensitivity/C")
        for step, row in enumerate(result["ratios"]):
            tracker.log({"sensitivity/C": row["ratio"], **{"sensitivity/"+k: v for k, v in row.items() if k != "ratio"}}, step)
        write_json(tracker.directory / "analysis.json", result)
        tracker.finish({"completed": True, "seed": seed, "analysis_only": True,
                        "points": len(result["ratios"]), "elapsed_seconds": result["elapsed_seconds"],
                        "source_summaries_reproduced": True,
                        "reference_ratio": settings["reference_ratio"],
                        "scope": settings["scope"]})
        result["tracking"] = read(tracker.directory / "summary.json")
        rows.append(result)
        print(json.dumps({"seed": seed, "verified": True, "seconds": result["elapsed_seconds"],
                          "run_id": result["tracking"]["wandb_run_id"]}), flush=True)
        gc.collect()
    aggregate = [{"ratio": c, **{metric: {"mean": statistics.mean(r["ratios"][i][metric] for r in rows),
                  "sd": statistics.stdev(r["ratios"][i][metric] for r in rows), "ddof": 1}
                  for metric in ["all_accuracy", "base_accuracy", "novel_accuracy"]}}
                 for i, c in enumerate(settings["ratios"])]
    write_json(output / "results.json", {"rows": rows, "aggregate": aggregate,
               "scope": settings["scope"], "n_seeds": len(rows), "completed": True})


if __name__ == "__main__":
    main()
