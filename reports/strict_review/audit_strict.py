"""Read logs and anonymous Forge evidence; never modify measured artifacts."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent
HOST = "https://api.forge.coreweave.com"
ENTITY = "vu-lam-vnuhcm-university-of-science"
PROJECT = "intro-ml-group3-dsal"


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def equal(a, b):
    if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
    if isinstance(a, dict) and isinstance(b, dict):
        return all(k in b and equal(v, b[k]) for k, v in a.items())
    return a == b


def verify(folder):
    import requests
    local_config, local_summary = read(folder / "config.json"), read(folder / "summary.json")
    assert local_summary["completed"], str(folder)
    run_id = local_summary["wandb_run_id"]
    query = "query($e:String!,$p:String!,$r:String!){project(name:$p,entityName:$e){name run(name:$r){name state config summaryMetrics history}}}"
    with requests.Session() as session:
        session.trust_env = False
        response = session.post(HOST + "/graphql", timeout=35,
                                json={"query": query, "variables": {"e": ENTITY, "p": PROJECT, "r": run_id}})
    response.raise_for_status()
    payload = response.json()
    assert not payload.get("errors"), (run_id, "anonymous GraphQL error")
    remote = payload["data"]["project"]["run"]
    assert remote["state"] == "finished", (run_id, remote["state"])
    config = json.loads(remote["config"]) if isinstance(remote["config"], str) else remote["config"]
    config = {k: v["value"] if isinstance(v, dict) and set(v) >= {"value"} else v for k, v in config.items()}
    assert equal(local_config, config), (run_id, "configuration mismatch")
    summary = json.loads(remote["summaryMetrics"])
    skipped = {"wandb_url", "wandb_run_id", "tracking_mode", "submission_ready", "public_visibility_verified"}
    for k, v in local_summary.items():
        if k not in skipped:
            assert equal(v, summary.get(k)), (run_id, "summary", k)
    history = [json.loads(row) if isinstance(row, str) else row for row in remote["history"]]
    expected = [json.loads(line) for line in (folder / "metrics.jsonl").read_text(encoding="utf-8").splitlines()]
    keyed = {int(row["_step"]): row for row in history}
    for row in expected:
        for k, v in row.items():
            if k != "step":
                assert equal(v, keyed[row["step"]].get(k)), (run_id, "history", row["step"], k)
    result = {"directory": folder.relative_to(ROOT).as_posix(), "run_id": run_id,
              "url": local_summary.get("wandb_url") or f"https://app.forge.coreweave.com/{ENTITY}/{PROJECT}/runs/{run_id}",
              "state": "finished", "anonymous_config_summary_history": True,
              "history_rows_checked": len(expected),
              "files_sha256": {n: sha(folder / n) for n in ["config.json", "summary.json", "metrics.jsonl"]}}
    print(run_id, "finished; anonymous config/summary/history match", flush=True)
    return result


def main():
    from src.utils.reproducibility import write_json
    original = read(ROOT / "reports/milestone2_final/assets/three_seeds_verified.json")
    earlier = read(ROOT / "reports/milestone2_final/assets/verified_evidence.json")
    folders = {ROOT / r["directory"] for r in original["runs"]}
    folders.update(ROOT / r["directory"] for r in earlier["experiments"])
    sensitivity = read(ROOT / "outputs/strict-review-20261119/ratio-sensitivity/results.json")
    folders.update((ROOT / "outputs/strict-review-20261119/ratio-sensitivity").glob("saved-C-sensitivity-seed*"))
    with ThreadPoolExecutor(max_workers=3) as pool:
        verified = list(pool.map(verify, sorted(folders)))
    assert len(verified) == 24
    protected = {}
    for row in sensitivity["rows"]:
        for p, digest in row["protected_sha256"].items():
            assert sha(ROOT / p) == digest, p
            protected[p] = digest
    baseline = ROOT / "reports/milestone2_final/DSAL_Milestone2_Lab1_3Seeds_Final.pptx"
    protected[baseline.relative_to(ROOT).as_posix()] = sha(baseline)
    phase_comparison = []
    for k, paper_a, paper_k in [(5, 66.39, 58.26), (25, 66.20, 58.32), (50, 66.33, 58.37)]:
        folder = ROOT / f"outputs/core-seed0/dsal-k{k}"
        config, summary, phases = read(folder / "config.json"), read(folder / "summary.json"), read(folder / "phases.json")
        assert config["protocol"] == {"base_classes": 50, "phases": k}
        assert len(phases) == k + 1
        assert equal(statistics.mean(p["accuracy"] for p in phases), summary["average_accuracy"])
        assert equal(phases[-1]["accuracy"], summary["last_accuracy"])
        base_config = read(ROOT / "outputs/core-seed0/dsal-k5/config.json")
        for field in ["feature_identity", "analytic", "seed", "class_order_seed", "analytic_batch_size"]:
            assert config[field] == base_config[field], (k, field)
        phase_comparison.append({"K": k, "seed": 0, "paper_Abar": paper_a, "paper_AK": paper_k,
                                 "Abar": summary["average_accuracy"], "AK": summary["last_accuracy"],
                                 "gap_Abar_pp": summary["average_accuracy"] - paper_a,
                                 "gap_AK_pp": summary["last_accuracy"] - paper_k,
                                 "run_id": summary["wandb_run_id"]})
    import torch
    from src.models.resnet import CifarResNet32
    torch.set_num_threads(2)
    spec = importlib.util.spec_from_file_location("isolated_author_resnet", ROOT / "artifacts/reference/official/models/CifarResNet.py")
    reference = importlib.util.module_from_spec(spec); spec.loader.exec_module(reference)
    torch.manual_seed(5)
    ours, author = CifarResNet32(50).double(), reference.resnet32(50).double()
    author.load_state_dict({k.replace("linear.", "fc."): v for k, v in ours.state_dict().items()})
    author.fc = torch.nn.Identity(); ours.eval(); author.eval()
    x = torch.randn(4, 3, 32, 32, dtype=torch.float64)
    with torch.no_grad():
        discrepancy = float((ours.features(x) - author(x)).abs().max())
    assert discrepancy < 1e-10
    architecture = {"reference_commit": subprocess.check_output(["git", "-C", str(ROOT / "artifacts/reference/official"), "rev-parse", "HEAD"], text=True).strip(),
                    "test": "Transfer identical supporting ResNet32 parameters; compare four synthetic inputs, eval mode, float64, tolerance 1e-10",
                    "feature_max_abs_difference": discrepancy,
                    "interpretation": "Architecture/forward compatibility under shared weights; does not establish matching initializations, training trajectories or CIFAR accuracy"}
    # Scan the already-public Git tree and local source/doc additions, not credentials.
    public_root = ROOT / "artifacts/publish-code"
    public_paths = subprocess.check_output(["git", "-C", str(public_root), "ls-tree", "-r", "--name-only", "HEAD"]).decode("utf-8").splitlines()
    secret = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?i:WANDB_API_KEY|api_key)\s*[=:]\s*[\x22\x27]?[a-f0-9]{40}\b|(?:ghp_|github_pat_)[A-Za-z0-9_]{25,}")
    for rel in public_paths:
        p = public_root / rel
        if p.suffix not in [".pptx", ".pdf", ".png"]:
            assert not secret.search(p.read_bytes()), "Secret-like literal found in tracked file; inspect privately"
    result = {"checked_utc": datetime.now(timezone.utc).isoformat(), "forge_host": HOST,
              "verified_runs": verified, "all_24_finished_public_full_data": True,
              "protected_original_sha256": protected, "protected_original_count": len(protected),
              "phase_count_comparison": phase_comparison, "resnet_forward_comparison": architecture,
              "public_repository": {"name": "vtpy23/IntroductionToMachineLearningGroup3", "visibility": "public", "verified_with": "GitHub connector repository metadata this turn", "last_published_commit": "84b9564e33156073c30e9d3ccab1b9006ae25931"},
              "secret_scan": {"public_git_files_checked": len(public_paths), "result": "no matching secret literals", "limitation": "Pattern scan, not a proof of absence"},
              "administrative_limits": ["Course names wandb.ai; anonymous Forge access verified, equivalence for grading not confirmed", "Core importance/coverage is ultimately graded by instructor", "No push authorized for this revision"],
              "source_documents": read(ROOT / "reports/milestone2_final/qa/source-documents.json")}
    write_json(OUT / "evidence/strict-audit.json", result)
    print(json.dumps({"verified_runs": len(verified), "protected_original_files": len(protected), "resnet_max_abs_difference": discrepancy}))


if __name__ == "__main__":
    main()
