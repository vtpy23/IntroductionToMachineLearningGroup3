"""Sync completed offline runs from copies; preserve original results and logs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

from src.utils.reproducibility import write_json
from src.utils.tracking import public_run_accessible


def file_digest(path):
    """Hash a small run metadata or W&B file without modifying it."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def same_measurement(left, right):
    """Allow only relative floating-point serialization rounding, including near zero."""
    if (isinstance(left, (int, float)) and not isinstance(left, bool) and
            isinstance(right, (int, float)) and not isinstance(right, bool)):
        return math.isclose(left, right, rel_tol=1e-12, abs_tol=0.0)
    return left == right


def completed_run_plan(root):
    """Select completed runs by stored ID, or by a single unambiguous candidate."""
    plan = []
    for path in sorted(Path(root).glob("**/summary.json")):
        summary = json.loads(path.read_text(encoding="utf-8"))
        if not summary.get("completed") or summary.get("tracking_mode") != "offline":
            continue
        candidates = sorted(p for p in (path.parent / "wandb").glob("offline-run-*")
                            if list(p.glob("*.wandb")))
        run_id = summary.get("wandb_run_id")
        selected = [p for p in candidates if run_id and p.name.endswith("-" + run_id)]
        if not run_id and len(candidates) == 1:
            selected = candidates
            run_id = selected[0].name.rsplit("-", 1)[-1]
        if len(selected) != 1:
            print(f"Missing or ambiguous offline run, leaving unchanged: {path}")
            continue
        blobs = list(selected[0].glob("*.wandb"))
        if len(blobs) != 1 or blobs[0].name != f"run-{run_id}.wandb":
            raise ValueError(f"Run ID and data file do not match: {selected[0]}")
        config = path.parent / "config.json"
        plan.append({"source_summary": path.as_posix(), "source_directory": selected[0].as_posix(),
                     "summary_sha256": file_digest(path),
                     "config_sha256": file_digest(config), "source_wandb_sha256": file_digest(blobs[0]),
                     "run_id": run_id, "summary": summary})
    return plan


def sync_completed_runs(plan, api, entity, project, base_url, manifest_path):
    """Upload copies and write new verification metadata, refusing remote collisions."""
    manifest_path = Path(manifest_path)
    if manifest_path.exists():
        raise FileExistsError(f"Refusing to replace an existing manifest: {manifest_path}")
    manifest = {"entity": entity, "project": project, "base_url": base_url,
                "created_utc": datetime.now(timezone.utc).isoformat(), "runs": []}
    existing = {run.id: run for run in api.runs(f"{entity}/{project}")}
    for item in plan:
        previous = synced_metadata(item["source_summary"], manifest_path.parent)
        previous_run = existing.get(previous.get("wandb_run_id"))
        if (previous_run and previous_run.state == "finished" and
                previous_run.summary.get("offline_file_sha256") == previous.get("offline_file_sha256")):
            print(f"Already verified, leaving unchanged: {previous_run.url}", flush=True)
            continue
        source = Path(item["source_directory"])
        blob = source / f"run-{item['run_id']}.wandb"
        if file_digest(blob) != item["source_wandb_sha256"]:
            raise ValueError(f"Run data changed since planning: {source}")
        if item["run_id"] in existing:
            run = existing[item["run_id"]]
            if run.summary.get("offline_file_sha256") != item["source_wandb_sha256"]:
                raise ValueError(f"Existing remote run ID collision; refusing overwrite: {run.id}")
        else:
            staging = Path("artifacts/wandb-sync")
            staging.mkdir(parents=True, exist_ok=True)
            destination = Path(tempfile.mkdtemp(prefix=item["run_id"] + "-", dir=staging)).resolve() / source.name
            shutil.copytree(source, destination)
            env = dict(os.environ, WANDB_BASE_URL=base_url, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
            subprocess.run([sys.executable, "-X", "utf8", "-m", "wandb", "sync", "--entity", entity,
                            "--project", project, str(destination)], env=env, check=True,
                           cwd=destination.parent)
            run = api.run(f"{entity}/{project}/{item['run_id']}")
        if run.state != "finished" or not run.summary.get("completed"):
            raise ValueError(f"Remote run not completed: {run.id}")
        # Compare original scientific summary values; update tracking metadata only.
        metadata = {"wandb_url", "wandb_run_id", "tracking_mode", "submission_ready",
                    "public_visibility_verified"}
        for key, value in item["summary"].items():
            if key not in metadata and not same_measurement(run.summary.get(key), value):
                raise ValueError(f"Remote summary differs for {run.id}: {key}")
        visible = public_run_accessible(entity, project, run.id, base_url)
        record = {key: value for key, value in item.items() if key != "summary"}
        record.update(wandb_url=run.url, tracking_mode="synced", public_visibility_verified=visible,
                      submission_ready=visible, verified_state=run.state)
        run.summary.update({"public_visibility_verified": visible, "submission_ready": visible,
                            "tracking_mode": "synced", "wandb_url": run.url,
                            "offline_file_sha256": item["source_wandb_sha256"]})
        manifest["runs"].append(record)
        write_json(manifest_path, manifest)
        print(run.url, "public" if visible else "PUBLIC VISIBILITY NOT VERIFIED", flush=True)
    if not plan:
        write_json(manifest_path, manifest)
    return manifest


def synced_metadata(summary_path, root):
    """Read verified tracking sidecars only while the original result still matches."""
    summary_path = Path(summary_path)
    digest = file_digest(summary_path)
    config_digest = file_digest(summary_path.parent / "config.json")
    result = {}
    for path in sorted(Path(root).glob("wandb-sync-*.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for record in manifest.get("runs", []):
            if (record.get("source_summary") and
                    Path(record["source_summary"]).resolve() == summary_path.resolve() and
                    record.get("summary_sha256") == digest and
                    record.get("config_sha256") == config_digest):
                result = {key: record[key] for key in ["wandb_url", "tracking_mode",
                          "public_visibility_verified", "submission_ready"]}
                result.update(wandb_run_id=record["run_id"],
                              offline_file_sha256=record["source_wandb_sha256"])
    return result


def main():
    from dotenv import load_dotenv
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entity", default=os.environ.get("WANDB_ENTITY"))
    parser.add_argument("--project", default=os.environ.get("WANDB_PROJECT", "intro-ml-group3-dsal"))
    parser.add_argument("--base-url", default=os.environ.get("WANDB_BASE_URL", "https://api.forge.coreweave.com"))
    parser.add_argument("--root", default="outputs")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.entity:
        raise SystemExit("Set WANDB_ENTITY in .env or pass --entity. Never pass API keys as CLI arguments.")
    plan = completed_run_plan(Path(args.root))
    if args.dry_run:
        print(json.dumps([{key: value for key, value in row.items() if key != "summary"} for row in plan], indent=2))
        return
    import wandb
    api = wandb.Api(overrides={"base_url": args.base_url})
    # Verify credentials and project read access before any upload.
    api.viewer
    if api.project(args.project, entity=args.entity) is None:
        raise SystemExit("Create the W&B project first and rerun")
    filename = "wandb-sync-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6] + ".json"
    manifest_path = Path(args.manifest) if args.manifest else Path(args.root) / filename
    sync_completed_runs(plan, api, args.entity, args.project, args.base_url, manifest_path)
    print(f"Sync manifest (original results preserved): {manifest_path}")


if __name__ == "__main__":
    main()
