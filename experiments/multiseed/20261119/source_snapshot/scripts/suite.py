"""Paired reproduction, ablation, phase-count and buffer-width experiments."""
import copy
from pathlib import Path

from scripts.run import run_incremental


def run_suite(config, features, outdir, mode):
    """Run declared variants with the same backbone, data order and projection seed.

    Every variant is a distinct tracked run. Completed matching configurations
    are reused so interrupted suites can resume without repeating measurements.
    """
    import json
    variants = config.get("suite", [
        {"name": "acil", "analytic": {"use_compensation": False}},
        {"name": "dac-no-plc", "analytic": {"plc": False}},
        {"name": "dsal", "analytic": {}},
    ])
    for variant in variants:
        if Path(".stop-project").exists():
            raise SystemExit("Pause requested by .stop-project; completed runs retained")
        current = copy.deepcopy(config)
        current.pop("suite", None)
        for section in ("analytic", "protocol"):
            current[section].update(variant.get(section, {}))
        current["lab"] = variant.get("lab", config.get("lab", "lab1-reproduction"))
        if "seed" in variant:
            current["seed"] = variant["seed"]
        directory = Path(outdir) / variant["name"]
        completed = directory / "summary.json"
        if completed.exists():
            old = json.loads((directory / "config.json").read_text(encoding="utf-8"))
            expected = {k: v for k, v in old.items() if k not in {"provenance", "feature_identity"}}
            same_features = old.get("feature_identity") == features["identity"]
            if expected == current and same_features and json.loads(completed.read_text())["completed"]:
                print(f"Skipping completed run: {directory}", flush=True)
                continue
            raise ValueError(f"Existing run has different config: {directory}; use a new output directory")
        run_incremental(current, features, directory, mode)
