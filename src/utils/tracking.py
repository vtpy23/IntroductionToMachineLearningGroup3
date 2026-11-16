"""W&B tracking with explicit offline status and a local JSONL audit trail."""
import json
import os
from pathlib import Path

from .reproducibility import write_json


def public_run_accessible(entity, project, run_id, base_url=None):
    """Check unauthenticated read access without consulting .netrc or cookies."""
    import requests
    try:
        with requests.Session() as session:
            session.trust_env = False
            endpoint = base_url or os.environ.get("WANDB_BASE_URL", "https://api.forge.coreweave.com")
            response = session.post(endpoint.rstrip("/") + "/graphql", timeout=20, json={
                "query": "query($e:String!,$p:String!,$r:String!){project(name:$p,entityName:$e){run(name:$r){id}}}",
                "variables": {"e": entity, "p": project, "r": run_id}})
            payload = response.json() if response.ok else {}
            return bool(((payload.get("data") or {}).get("project") or {}).get("run"))
    except (requests.RequestException, ValueError):
        return False


class Tracker:
    """Record each run locally and in the single configured W&B project.

    ``online`` fails early if authentication/configuration is missing. Offline
    results remain marked unsubmitted until a public W&B run URL is recorded.
    """

    def __init__(self, directory, config: dict, group: str, mode: str = "offline"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.run = None
        self.url = None
        self.run_id = None
        self.mode = mode
        write_json(self.directory / "config.json", config)
        if mode != "disabled":
            import wandb
            settings = config.get("tracking", {})
            base_url = settings.get("base_url") or os.environ.get("WANDB_BASE_URL")
            self.run = wandb.init(project=settings.get("project", "intro-ml-group3-dsal"),
                                  entity=settings.get("entity"), mode=mode,
                                  name=self.directory.name, config=config,
                                  tags=[group], dir=str(self.directory),
                                  settings=wandb.Settings(base_url=base_url) if base_url else None)
            self.run.define_metric("base/*", step_metric="base/epoch")
            self.run.define_metric("cil/*", step_metric="cil/phase")
            self.run_id = self.run.id
            if mode == "online":
                self.url = self.run.url

    def log(self, values: dict, step: int) -> None:
        """Append one metrics record and forward it to W&B at ``step``."""
        with (self.directory / "metrics.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"step": step, **values}, allow_nan=False) + "\n")
        if self.run is not None:
            self.run.log(values, step=step)

    def finish(self, summary: dict) -> None:
        """Persist summary and W&B metadata and close the W&B run."""
        public = bool(self.url) and public_run_accessible(
            self.run.entity, self.run.project, self.run_id, self.run.settings.base_url)
        summary.update({"wandb_url": self.url, "wandb_run_id": self.run_id, "tracking_mode": self.mode,
                        "submission_ready": public, "public_visibility_verified": public})
        write_json(self.directory / "summary.json", summary)
        if self.run is not None:
            for k, v in summary.items():
                self.run.summary[k] = v
            self.run.finish()
