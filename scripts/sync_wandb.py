"""Sync only completed offline runs and record verified public W&B URLs."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from src.utils.reproducibility import write_json
from src.utils.tracking import public_run_accessible


def main():
    from dotenv import load_dotenv
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entity", default=os.environ.get("WANDB_ENTITY"))
    parser.add_argument("--project", default=os.environ.get("WANDB_PROJECT", "intro-ml-group3-dsal"))
    parser.add_argument("--root", default="outputs")
    args = parser.parse_args()
    if not args.entity:
        raise SystemExit("Set WANDB_ENTITY in .env or pass --entity. Never pass API keys as CLI arguments.")
    import wandb
    api = wandb.Api()
    # Authentication and project read access must succeed before any upload.
    project = api.project(args.project, entity=args.entity)
    if project is None:
        raise SystemExit("Create the W&B project first, select Public, and rerun")
    for path in sorted(Path(args.root).glob("**/summary.json")):
        summary = json.loads(path.read_text(encoding="utf-8"))
        if not summary.get("completed") or summary.get("tracking_mode") != "offline":
            continue
        candidates = list((path.parent / "wandb").glob("offline-run-*"))
        if not candidates:
            continue
        run_id = summary.get("wandb_run_id")
        selected = [p for p in candidates if run_id and p.name.endswith("-" + run_id)]
        if not selected and len(candidates) == 1:
            selected = candidates
            run_id = selected[0].name.rsplit("-", 1)[-1]
        if len(selected) != 1:
            print(f"Ambiguous offline run, leaving unchanged: {path}"); continue
        subprocess.run([sys.executable, "-m", "wandb", "sync", "--entity", args.entity,
                        "--project", args.project, str(selected[0])], check=True)
        run = api.run(f"{args.entity}/{args.project}/{run_id}")
        # A URL alone is not proof of public visibility: verify anonymously.
        visible = public_run_accessible(args.entity, args.project, run_id)
        summary.update({"wandb_url": run.url, "wandb_run_id": run_id,
                        "tracking_mode": "synced", "submission_ready": visible,
                        "public_visibility_verified": visible})
        write_json(path, summary)
        run.summary.update({"public_visibility_verified": visible, "submission_ready": visible,
                            "tracking_mode": "synced", "wandb_url": run.url})
        print(run.url, "public" if visible else "PUBLIC VISIBILITY NOT VERIFIED")


if __name__ == "__main__":
    main()
