"""Publish lightweight local evidence and derive numerical/mapping reports."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import statistics

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, text): Path(p).parent.mkdir(parents=True, exist_ok=True); Path(p).write_text(text, encoding="utf-8")


def main():
    audit = read(HERE / "evidence/strict-audit.json")
    old = read(ROOT / "reports/milestone2_final/assets/three_seeds_verified.json")
    source = ROOT / "outputs/strict-review-20261119/ratio-sensitivity"
    sensitivity = read(source / "results.json")
    published = ROOT / "experiments/strict-review/20261119"
    published.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / "results.json", published / "results.json")
    for folder in source.glob("saved-C-sensitivity-seed*"):
        for name in ["config.json", "summary.json", "metrics.jsonl", "analysis.json"]:
            target = published / folder.name / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(folder / name, target)
    for rel in ["scripts/analyze_saved_classifiers.py", "configs/saved_classifier_sensitivity.json"]:
        target = published / "source_snapshot" / rel; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
    config = read(source / "saved-C-sensitivity-seed0/config.json")
    for rel in ["scripts/analyze_saved_classifiers.py", "configs/saved_classifier_sensitivity.json"]:
        assert sha(ROOT / rel) == config["provenance"]["source_sha256"][rel]
    write(published / "README.md", """# Phân tích classifier đã lưu, 19/11/2026

Chỉ suy luận trên final heads, không fit lại hoặc thay kết quả seed0/1/2. Ba run sensitivity có config, parent run IDs, hash artifact gốc, history11 điểm, và counts corrected/harmed. C0 khớp ACIL; C0,6 khớp DS-AL cũ ở accuracy tổng/base/novel. C0,6 vẫn là benchmark đã khai báo trước. Không có A-bar mới cho các C khác.

Nguồn chạy ở `source_snapshot/` giữ byte của hai file mới dùng tạo kết quả; provenance đầy đủ trong từng config. Thay đổi sau đó ở reporting/docs không thay thí nghiệm đã đo. Snapshot thí nghiệm train/fit gốc ở `experiments/multiseed/20261119/`. Không chứa dữ liệu ảnh, feature cache, checkpoint hay credentials.

Đợt rà soát này chưa push GitHub theo yêu cầu người dùng. Xem `reports/strict_review/` cho audit, mapping và giới hạn.
""")
    # A new config, never modify config paths attached to completed runs.
    fresh = copy.deepcopy(read(ROOT / "configs/cifar100_core.json"))
    fresh["dataset"]["revision"] = "aadb3af77e9048adbea6b47c21a81e47dd092ae5"
    fresh["output"] = "outputs/fresh-strict-repro/seed0"
    fresh["training"]["checkpoint"] = "checkpoints/fresh-strict-repro/seed0-resnet32.pt"
    fresh["training"]["device"] = "cpu"
    fresh["suite"] = fresh["suite"][:3]
    write(ROOT / "configs/cifar100_strict_repro.json", json.dumps(fresh, indent=2) + "\n")
    lines = ["# Kiểm chứng số liệu", "", f"Audit trực tiếp UTC: {audit['checked_utc']}",
             "", "24 run finished, config/summary/history đọc được qua GraphQL **không đăng nhập**, khớp toàn bộ log. Đây là kiểm tra public data kỹ thuật, không tự chứng minh giảng viên chấp nhận host Forge thay cho wandb.ai.",
             "", "## Ba seed: hai tầng trung bình", "", "Ā_s=(Σ_{k=0}^5 A_{s,k})/6. Sau đó mean và SD mẫu của ba Ā_s; A_K tính riêng từ pha cuối. SD dùng ddof=1, không phải SE/CI. Không dùng 18 pha làm 18 lần lặp.", "",
             "| Phương pháp | Ā mean ± SD (%) | A_K mean ± SD (%) | Base mean ± SD | Novel mean ± SD |", "|---|---:|---:|---:|---:|"]
    methods = ["acil-k5", "dac-no-plc-k5", "dsal-k5"]
    for m in methods:
        a = old["aggregates"][m]
        fields = [f"{a[k]['mean']:.6f} ± {a[k]['sd']:.6f}" for k in ["average_accuracy", "last_accuracy", "base_accuracy", "novel_accuracy"]]
        lines.append("| " + " | ".join([m, *fields]) + " |")
    lines += ["", "## Gain và gap", "", "DS-AL−ACIL A_K: +0,31/+0,34/+0,56pp, mean+0,403333pp (SD paired0,136504). PLC−DAC A_K: +0,63/+0,42/+0,36pp, mean+0,470000pp (SD paired0,141774). DAC−ACIL: −0,32/−0,08/+0,20pp, mean−0,066667pp.",
              "", "Paper gain 58,26−57,78=0,48 pp, nhóm 0,403333 pp, chênh gain −0,076667 pp. Hai gain gần nhau về độ lớn không định danh nguyên nhân gap tuyệt đối. DS-AL Ā gap −1,132392 pp (−1,705666% tương đối), A_K gap −1,486667 pp (−2,551779% tương đối). Không khẳng định ý nghĩa thống kê.",
              "", "## K đối sánh Table1, DS-AL ResNet32, chỉ seed0", "", "| K | Paper Ā | Nhóm Ā | Paper A_K | Nhóm A_K | Gap A_K (pp) |", "|---:|---:|---:|---:|---:|---:|"]
    for r in audit["phase_count_comparison"]:
        lines.append(f"| {r['K']} | {r['paper_Abar']:.2f} | {r['Abar']:.6f} | {r['paper_AK']:.2f} | {r['AK']:.2f} | {r['gap_AK_pp']:+.2f} |")
    lines += ["", "## Sensitivity C: final classifier Tanh, ba seed", "", "| C | A_K mean ± SD | Base mean | Novel mean |", "|---:|---:|---:|---:|"]
    for r in sensitivity["aggregate"]:
        lines.append(f"| {r['ratio']:.1f} | {r['all_accuracy']['mean']:.6f} ± {r['all_accuracy']['sd']:.6f} | {r['base_accuracy']['mean']:.6f} | {r['novel_accuracy']['mean']:.6f} |")
    lines += ["", "Đỉnh mean trong lưới tại C0,7/0,8:56,83%. Paper chỉ mô tả Tanh CIFAR đạt đỉnh quanh0,6; không dựng số tại những điểm Figure4 không ghi nhãn. Giữ C0,6 trong benchmark, không dùng test sweep để thay lựa chọn hyperparameter. Không có A-bar mới vì thiếu head từng pha.",
              "", "## Paired prediction flips, cùng10.000 ảnh mỗi seed", "", "| So sánh | Seed | Sửa sai | Làm hỏng | Net (pp) |", "|---|---:|---:|---:|---:|"]
    for r in sensitivity["rows"]:
        for comparison, groups in r["paired_prediction_changes"].items():
            x = groups["all"]
            lines.append(f"| {comparison} | {r['seed']} | {x['corrected']} | {x['harmed']} | {x['net_pp']:+.2f} |")
    lines += ["", "DAC mất4,426667pp base và tăng4,293333pp novel. PLC so DAC lấy lại2,293333pp base nhưng giảm1,353333pp novel. Hai nhóm bằng5.000 ảnh nên gain tổng bằng trung bình hai gain nhóm. Không suy rộng DAC luôn tốt hoặc PLC luôn tăng cả hai nhóm.",
              "", f"{audit['protected_original_count']} file gốc được kiểm tra SHA-256 sau phân tích, gồm classifier/checkpoint/cache/log và PPTX nguồn. ResNet32 chuyển cùng weights, float64,4 input tổng hợp: max abs feature {audit['resnet_forward_comparison']['feature_max_abs_difference']:.3e}. Đây không phải đối chiếu accuracy CIFAR hoặc init/training.",
              "", "Ba lượt suy luận mới mất tổng " + f"{sum(r['elapsed_seconds'] for r in sensitivity['rows']):.3f}" + " giây tính score; không gồm import, hash, W&B và đọc đĩa. Không so số này với thời gian train/fit. Wrapper PowerShell ghi NativeCommandError do stderr của W&B; results.json hoàn tất và cả ba run được audit lại finished, đầy đủ11 điểm. Không coi wrapper exit này là kết quả scientific failure."]
    write(HERE / "NUMERICAL_VERIFICATION.md", "\n".join(lines) + "\n")
    mapping = ["# Ánh xạ thí nghiệm → source → config → W&B", "", "Các đường dẫn dưới đây là bằng chứng nhẹ. Checkpoint/cache gốc giữ tại máy, chỉ hash được công bố. Bản sửa mới chưa push.", "", "| Phạm vi / run | Script | Config | History | W&B |", "|---|---|---|---|---|"]
    for r in audit["verified_runs"]:
        folder = Path(r["directory"]); name = folder.name
        if "ratio-sensitivity" in r["directory"]:
            evidence = "experiments/strict-review/20261119/" + name
            script = "scripts/analyze_saved_classifiers.py"; scope = "E4 Tanh/C final; " + name
        elif "multiseed-20261119" in r["directory"]:
            seed = folder.parent.name.replace("core-seed", "")
            evidence = f"experiments/multiseed/20261119/evidence/seed{seed}/{name}"
            script = "scripts/run.py"; scope = f"CIFAR seed{seed} / {name}"
        else:
            evidence = "experiments/evidence/" + name
            script = "scripts/compare_reference.py" if name == "reference-comparison" else "scripts/empirics.py" if "empirics" in r["directory"] else "scripts/run.py"
            scope = ("Synthetic / " if "empirics" in r["directory"] or name == "reference-comparison" else "CIFAR seed0 / ") + name
        mapping.append(f"| {scope} | [{script}](../../{script}) | [config](../../{evidence}/config.json) | [history](../../{evidence}/metrics.jsonl) | [{r['run_id']}]({r['url']}) |")
    mapping += ["", "Lệnh chính và quy trình môi trường sạch: [RUNBOOK.md](RUNBOOK.md). Checkpoint, class order, nguồn dữ liệu và run IDs được đối chiếu trong [strict-audit.json](evidence/strict-audit.json), snapshot ba seed và completion audit gốc."]
    write(HERE / "EXPERIMENT_MAPPING.md", "\n".join(mapping) + "\n")
    print("Generated local evidence, pinned fresh config and numerical/run mapping reports")


if __name__ == "__main__": main()
