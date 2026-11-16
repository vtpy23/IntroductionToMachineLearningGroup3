"""Build a clean cloud source archive from an explicit allowlist (never credentials)."""
from pathlib import Path
import zipfile


def main():
    roots = ["src", "scripts", "configs", "tests", "docs", "notebooks", "experiments"]
    allowed = {".py", ".json", ".md", ".ps1", ".ipynb", ".mjs", ".csv", ".png"}
    files = [Path(p) for p in ["README.md", "requirements.txt", "pyproject.toml", ".env.example"]]
    files += [p for root in roots for p in Path(root).rglob("*") if p.is_file()
              and p.suffix in allowed and "__pycache__" not in p.parts
              and ".build" not in p.parts and "node_modules" not in p.parts]
    destination = Path("artifacts/project-source.zip")
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            if path.exists():
                archive.write(path, path.as_posix())
    print(destination, destination.stat().st_size, "bytes", len(files), "allowlisted files")


if __name__ == "__main__":
    main()
