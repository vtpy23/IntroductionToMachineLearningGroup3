"""Generate traceable results tables, scientific plots and status from completed runs."""
import argparse
import csv
import json
from pathlib import Path

from src.utils.reproducibility import write_json
from scripts.sync_wandb import synced_metadata


PAPER = {
    5: {"acil": (66.30, 57.78), "dsal": (66.39, 58.26)},
    25: {"acil": (65.95, 57.65), "dsal": (66.20, 58.32)},
    50: {"acil": (66.01, 57.83), "dsal": (66.33, 58.37)},
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="outputs")
    args = parser.parse_args()
    rows = []
    for path in sorted(Path(args.root).glob("**/summary.json")):
        summary = json.loads(path.read_text(encoding="utf-8"))
        if "last_accuracy" not in summary:
            continue
        summary.update(synced_metadata(path, args.root))
        config = json.loads((path.parent / "config.json").read_text(encoding="utf-8"))
        analytic = config["analytic"]
        method = "dsal" if analytic.get("use_compensation", True) else "acil"
        limited = any(config["dataset"].get(k) for k in ["train_per_class", "test_per_class"])
        eligible = (not limited and config["training"]["epochs"] == 160 and
                    analytic["buffer_size"] == 8192 and analytic.get("plc", True))
        published = PAPER.get(config["protocol"]["phases"], {}).get(method) if eligible else None
        row = {"run": path.parent.as_posix(), "method": method,
               "protocol": summary["protocol"], "phases": summary["phases"],
               "buffer_size": summary["buffer_size"], "seed": summary["seed"],
               "average_accuracy": summary["average_accuracy"], "last_accuracy": summary["last_accuracy"],
               "fit_seconds": summary["fit_seconds"], "wandb_url": summary.get("wandb_url"),
               "submission_ready": summary.get("submission_ready", False),
               "paper_average_accuracy": published[0] if published else None,
               "paper_last_accuracy": published[1] if published else None,
               "last_gap_percentage_points": summary["last_accuracy"] - published[1] if published else None,
               "last_relative_deviation_percent": 100 * (summary["last_accuracy"] - published[1]) / published[1] if published else None}
        rows.append(row)
    destination = Path("experiments/reproduction")
    destination.mkdir(parents=True, exist_ok=True)
    if rows:
        with (destination / "results.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    write_json(destination / "results.json", rows)
    text = ["# Kết quả đo được", "", "Bảng sinh tự động bởi `python -m scripts.summarize`. Đơn vị accuracy: %.",
            "Smoke test không phải tái hiện. Run offline chưa đáp ứng yêu cầu W&B công khai.", "",
            "| Run | K | Buffer | Trung bình | Pha cuối | W&B |", "|---|---:|---:|---:|---:|---|"]
    for row in rows:
        text.append(f"| {row['run']} | {row['phases']} | {row['buffer_size']} | {row['average_accuracy']:.3f} | {row['last_accuracy']:.3f} | {row['wandb_url'] or 'OFFLINE, cần sync'} |")
    (destination / "RESULTS.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    plot_empirics(Path(args.root))
    print(f"Summarized {len(rows)} completed classification runs")


def plot_empirics(root):
    """Render measured mechanism evidence only; never fill absent experiments."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    directory = Path("experiments/empirics")
    directory.mkdir(parents=True, exist_ok=True)
    for name, xkey, ykey, xlabel, ylabel in [
        ("phase-dependence", "increments", "comp_relative_difference", "Incremental phases", "Relative compensation weight difference"),
        ("ridge-residue", "gamma", "cross_residual_norm", "Ridge coefficient gamma", "Norm of X.T @ residual"),
        ("scaling", "buffer_size", "fit_seconds", "Buffer dimension", "Fit time (seconds)")]:
        paths = list(root.glob(f"**/{name}/measurements.json"))
        if not paths:
            continue
        records = json.loads(paths[0].read_text(encoding="utf-8"))
        write_json(directory / f"{name}.json", records)
        fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
        for seed in sorted(set(r["seed"] for r in records)):
            part = [r for r in records if r["seed"] == seed]
            ax.plot([r[xkey] for r in part], [r[ykey] for r in part], "o-", label=f"seed {seed}")
        if name == "ridge-residue":
            ax.set_xscale("log"); ax.set_yscale("log")
        ax.set(xlabel=xlabel, ylabel=ylabel, title="Synthetic fixed-feature mechanism test")
        ax.legend(); ax.grid(alpha=0.25)
        fig.savefig(directory / f"{name}.png", dpi=180)
        plt.close(fig)


if __name__ == "__main__":
    main()
