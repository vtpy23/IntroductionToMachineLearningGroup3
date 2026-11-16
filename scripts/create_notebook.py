"""Create a portable Colab/Kaggle notebook using only Python standard library."""
import json
from pathlib import Path


def main():
    cells = []
    def cell(kind, source):
        value = {"cell_type": kind, "id": f"dsal-{len(cells):02d}", "metadata": {}, "source": source.splitlines(keepends=True)}
        if kind == "code":
            value.update({"execution_count": None, "outputs": []})
        cells.append(value)
    cell("markdown", "# DS-AL: Colab / Kaggle\n\nBật GPU trong runtime settings. Notebook gọi cùng mã nguồn của repository, không chép lại core method. Upload `artifacts/project-source.zip` do `python -m scripts.package_source` tạo. Kết quả offline cần sync W&B công khai trước khi nộp. Không nhúng token vào notebook.\n")
    cell("code", "from pathlib import Path\nimport sys, zipfile, os, subprocess\ntry:\n    from google.colab import files\n    uploaded = files.upload()\n    archive = next(Path(name) for name in uploaded if name.endswith('.zip'))\nexcept ImportError:\n    archives = list(Path('/kaggle/input').rglob('project-source.zip'))\n    if not archives: raise RuntimeError('Attach project-source.zip as a Kaggle input dataset')\n    archive = archives[0]\nworkspace = Path('/content/dsal-group3' if Path('/content').exists() else '/kaggle/working/dsal-group3')\nworkspace.mkdir(parents=True, exist_ok=True)\nwith zipfile.ZipFile(archive) as z:\n    for member in z.infolist():\n        target = (workspace / member.filename).resolve()\n        if workspace.resolve() not in target.parents: raise ValueError('Unsafe archive member')\n    z.extractall(workspace)\nos.chdir(workspace)\nprint(workspace)\n")
    cell("code", "subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'], check=True)\nprint('If pip changes a package already imported, restart the runtime before continuing.')\n")
    cell("markdown", "## Tracking\n\nĐiền entity không bí mật. `wandb.login()` nhập API key qua ô bảo mật hoặc dùng secrets của nền tảng. Không ghi token vào cell. Đổi TRACKING thành `online` sau khi đăng nhập; dùng cùng project với máy local.\n")
    cell("code", "ENTITY = ''\nPROJECT = 'intro-ml-group3-dsal'\nTRACKING = 'offline'\nif ENTITY: os.environ['WANDB_ENTITY'] = ENTITY\nos.environ['WANDB_PROJECT'] = PROJECT\nif TRACKING == 'online':\n    import wandb\n    wandb.login()\n")
    cell("code", "subprocess.run([sys.executable, '-m', 'scripts.doctor'], check=True)\nsubprocess.run([sys.executable, '-m', 'pytest', '-q'], check=True)\nsubprocess.run([sys.executable, '-m', 'scripts.run', '--config', 'configs/cifar100_smoke.json', '--stage', 'suite', '--tracking', TRACKING], check=True)\n")
    cell("markdown", "## Tái hiện đầy đủ trên CIFAR-100\n\nCấu hình mặc định160 epochs, buffer8192, K5/25/50. Runtime có thể dài. Checkpoint mỗi epoch. Để khôi phục sau khi runtime reset, tải lại checkpoint và feature cache vào cùng đường dẫn. Giữ nguyên config để tránh dùng nhầm checkpoint. Bộ nhớ buffer8192 gồm nhiều ma trận lớn.\n")
    cell("code", "subprocess.run([sys.executable, '-m', 'scripts.run', '--config', 'configs/cifar100_core.json', '--stage', 'suite', '--tracking', TRACKING], check=True)\n")
    cell("code", "subprocess.run([sys.executable, '-m', 'scripts.empirics', '--tracking', TRACKING], check=True)\nsubprocess.run([sys.executable, '-m', 'scripts.summarize'], check=True)\n")
    cell("markdown", "## Ba seed và lưu kết quả\n\nChỉ bật RUN_THREE_SEEDS khi runtime/quota đủ. Ba seed có backbone riêng. Archive kết quả có log W&B offline, checkpoint và feature cache; dung lượng có thể lớn. Không chứa API key hoặc `.env`.\n")
    cell("code", "RUN_THREE_SEEDS = False\nif RUN_THREE_SEEDS:\n    subprocess.run([sys.executable, '-m', 'scripts.multiseed', '--seeds', '0', '1', '2', '--tracking', TRACKING], check=True)\nimport shutil\nshutil.make_archive(str(workspace.parent / 'dsal-results'), 'zip', workspace, 'outputs')\ntry:\n    from google.colab import files\n    files.download(str(workspace.parent / 'dsal-results.zip'))\nexcept ImportError:\n    print('Kaggle output:', workspace.parent / 'dsal-results.zip')\n")
    notebook = {"nbformat": 4, "nbformat_minor": 5, "cells": cells,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}}
    Path("notebooks/Colab_Kaggle.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Created notebooks/Colab_Kaggle.ipynb")


if __name__ == "__main__":
    main()
