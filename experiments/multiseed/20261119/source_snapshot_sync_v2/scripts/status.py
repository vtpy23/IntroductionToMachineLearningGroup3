"""Print pipeline progress without loading model checkpoints or exposing credentials."""
import json
from pathlib import Path


def main():
    status = Path("outputs/pipeline/status.json")
    print(status.read_text(encoding="utf-8") if status.exists() else "No pipeline status yet")
    for path in sorted(Path("outputs").glob("**/base-training/metrics.jsonl")):
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines:
            row = json.loads(lines[-1])
            print(path.parent, "epoch", row.get("base/epoch"), "test accuracy", row.get("base/test_accuracy"), "seconds", row.get("base/seconds"))


if __name__ == "__main__":
    main()
