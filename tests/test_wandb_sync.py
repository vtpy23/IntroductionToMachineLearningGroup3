"""Ensure syncing cannot replace local evidence or silently overwrite remote IDs."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import sync_wandb


def make_result(root, run_id="valid123", completed=True):
    """Create minimal local evidence without making a W&B network call."""
    directory = root / "experiment"
    run_directory = directory / "wandb" / ("offline-run-20260101_000000-" + run_id)
    run_directory.mkdir(parents=True)
    (run_directory / f"run-{run_id}.wandb").write_bytes(b"original-run-evidence")
    summary = {"completed": completed, "tracking_mode": "offline", "wandb_run_id": run_id,
               "last_accuracy": 12.5}
    (directory / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (directory / "config.json").write_text('{}', encoding="utf-8")
    return directory, summary


def test_plan_skips_incomplete_and_never_substitutes_an_explicit_missing_id(tmp_path):
    directory, summary = make_result(tmp_path, completed=False)
    assert sync_wandb.completed_run_plan(tmp_path) == []
    summary.update(completed=True, wandb_run_id="missing1")
    (directory / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    assert sync_wandb.completed_run_plan(tmp_path) == []


def test_sync_uses_copies_and_leaves_original_evidence_unchanged(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    directory, summary = make_result(Path("outputs"))
    original = {str(p): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    plan = sync_wandb.completed_run_plan("outputs")
    remote = SimpleNamespace(id="valid123", state="finished", summary=dict(summary),
                             url="https://example.invalid/run/valid123")
    calls = []

    def fake_sync(command, **kwargs):
        staged = Path(command[-1])
        assert staged.resolve() != Path(plan[0]["source_directory"]).resolve()
        (staged / "run-valid123.wandb.synced").touch()
        calls.append(command)

    monkeypatch.setattr(sync_wandb.subprocess, "run", fake_sync)
    monkeypatch.setattr(sync_wandb, "public_run_accessible", lambda *args: True)
    api = SimpleNamespace(runs=lambda _: [], run=lambda _: remote)
    manifest = Path("outputs/wandb-sync-test.json")
    sync_wandb.sync_completed_runs(plan, api, "entity", "project", "https://example.invalid", manifest)
    assert len(calls) == 1
    assert {str(p): p.read_bytes() for p in directory.rglob("*") if p.is_file()} == original
    assert sync_wandb.synced_metadata(directory / "summary.json", "outputs")["submission_ready"]
    # A changed result must not inherit the old run's URL or public status.
    (directory / "summary.json").write_text('{}', encoding="utf-8")
    assert sync_wandb.synced_metadata(directory / "summary.json", "outputs") == {}


def test_sync_refuses_remote_id_collision_and_existing_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_result(Path("outputs"))
    plan = sync_wandb.completed_run_plan("outputs")
    remote = SimpleNamespace(id="valid123", summary={"offline_file_sha256": "other-evidence"})
    api = SimpleNamespace(runs=lambda _: [remote])
    manifest = Path("outputs/wandb-sync-test.json")
    with pytest.raises(ValueError, match="collision"):
        sync_wandb.sync_completed_runs(plan, api, "entity", "project", "https://example.invalid", manifest)
    assert not manifest.exists()
    manifest.write_text('{}', encoding="utf-8")
    with pytest.raises(FileExistsError):
        sync_wandb.sync_completed_runs(plan, api, "entity", "project", "https://example.invalid", manifest)


def test_measurement_comparison_accepts_rounding_but_preserves_small_residuals():
    assert sync_wandb.same_measurement(11.240806878306879, 11.24080687830688)
    assert not sync_wandb.same_measurement(11.2408, 11.2409)
    assert not sync_wandb.same_measurement(1e-15, 0.0)


def test_finished_run_wait_refreshes_stale_sdk_state(monkeypatch):
    running = SimpleNamespace(id='valid123', state='running', summary={'completed': True})
    finished = SimpleNamespace(id='valid123', state='finished', summary={'completed': True})
    responses = iter([running, finished])
    flushes = []
    api = SimpleNamespace(flush=lambda: flushes.append(True), run=lambda _: next(responses))
    monkeypatch.setattr(sync_wandb.time, 'sleep', lambda _: None)
    assert sync_wandb.wait_for_finished(api, 'entity/project/valid123') is finished
    assert len(flushes) == 2


def test_existing_upload_requires_matching_measured_history(tmp_path):
    directory, summary = make_result(tmp_path)
    row = {'step': 0, 'cil/phase': 0, 'cil/accuracy': 12.5}
    (directory/'metrics.jsonl').write_text(json.dumps(row)+'\n')
    item = sync_wandb.completed_run_plan(tmp_path)[0]
    remote = SimpleNamespace(id='valid123', config={}, summary=dict(summary),
                             scan_history=lambda: iter([{'cil/phase': 0, 'cil/accuracy': 12.5}]))
    sync_wandb.verify_existing_upload(item, remote)
    remote.scan_history=lambda: iter([{'cil/phase': 0, 'cil/accuracy': 12.6}])
    with pytest.raises(ValueError, match='history differs'):
        sync_wandb.verify_existing_upload(item, remote)
