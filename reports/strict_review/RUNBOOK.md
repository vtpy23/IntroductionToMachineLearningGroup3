# Chạy, tái lập và cập nhật slide

> Publication update 2026-11-20: see [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md). The team reports submission and has authorized publishing this revision. References below to an unpushed/local-only revision describe the original 2026-11-19 review. Original files and their manifest are archived in [history](history/review-delivery-20261119.zip). The review score is not an official grade.

Các seed0/1/2 đã xong. Các lệnh train/refit dưới đây là hướng dẫn cho một lần tái lập được nhóm chủ động chọn, **không phải lệnh đã chạy lại trong đợt review**. Không chạy stage train vào checkpoint/output lịch sử. Không cài lại hoặc nâng cấp hai venv đang dùng.

## Môi trường độc lập: chuẩn bị, chưa thực thi

Python3.11.8, `requirements.txt` pin các package nghiên cứu. Bản CPU benchmark dùng torch2.5.1+cpu, torchvision0.20.1+cpu, W&B0.23.1. `.venv` hiện tại dùng torch2.5.1+cu121 và W&B0.31.0 để quản lý; không thay các phiên bản này. Pip check hiện có7conflicts kế thừa package ngoài dự án, chi tiết `evidence/environment-check.json`; không tuyên bố clean environment đã pass.

```powershell
py -3.11 -m venv .venv-repro-clean
.venv-repro-clean/Scripts/python.exe -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu
.venv-repro-clean/Scripts/python.exe -m pip install -r requirements.txt
.venv-repro-clean/Scripts/python.exe -m pip check
.venv-repro-clean/Scripts/python.exe -m pytest -q
```

Venv mới mặc định không dùng `--system-site-packages`. Kiểm tra `pyvenv.cfg` có `include-system-site-packages = false`. Chưa chạy cài mới/full pipeline này để tránh tải package/dataset và tốn thêm tài nguyên khi không cần thiết. Mức xác nhận hiện tại là test/import trên môi trường đang hoạt động.

## Dataset và lần tái lập mới

`src/datasets/cifar100.py` tự tải Parquet từ Hugging Face `uoft-cs/cifar100`, đọc fine_label và tạo cache; không cần tải tay/giải nén thủ công. Config mới `configs/cifar100_strict_repro.json` pin đúng revision lịch sử và dùng output/checkpoint **mới**, chỉ gồm ba phương pháp K5. Config/JSON đã gắn với run cũ được giữ nguyên.

```powershell
# Data-only sẽ tải nếu cache chưa có; đây không phải train.
.venv-repro-clean/Scripts/python.exe -m scripts.run --config configs/cifar100_strict_repro.json --stage data

# Chỉ khi được đồng ý chạy lại một benchmark mới:
.venv-repro-clean/Scripts/python.exe -u -m scripts.run --config configs/cifar100_strict_repro.json --stage prepare --tracking offline
.venv-repro-clean/Scripts/python.exe -u -m scripts.run --config configs/cifar100_strict_repro.json --stage analytic --tracking offline
```

Stageprepare train backbone160epoch và trích cache; stageanalytic chạy ACIL/DAC−PLC/DS-AL từ suite. Để tạo seed mới: sao chép config sang tên mới, đổi `seed`, `class_order_seed`, `output`, `training.checkpoint` nhất quán; giữ các thông số còn lại. Không gán backbone/cache seed0 cho seed1/2. Resume checkpoint chỉ khi signature khớp; analytic gián đoạn phải chạy lại phương pháp trong output root mới, không ghép phase khác cấu hình.

## W&B Forge

```powershell
.venv/Scripts/python.exe -m wandb login --host https://api.forge.coreweave.com
```

Entity `vu-lam-vnuhcm-university-of-science`, project `intro-ml-group3-dsal`, `WANDB_BASE_URL=https://api.forge.coreweave.com`. `.env` chỉ nằm cục bộ và Git ignore. Không nhập API key vào code, command line, README hoặc chat. Login là thao tác máy người dùng; không tự đổi host hay sao chép run giữa server. Các run mới dùng online hoặc sync bản sao offline qua `scripts.sync_wandb`, rồi kiểm tra finished/config/summary/history và public trước khi đưa số vào slide. Không cần sync lại24run đã xác minh.

## Phân tích C: chỉ suy luận, không refit

```powershell
.venv-cpu/Scripts/python.exe -u -m scripts.analyze_saved_classifiers --tracking online
```

Lệnh trên **từ chối output đã tồn tại**. Kết quả lần hiện tại đã có trong `outputs/strict-review-20261119/ratio-sensitivity/`; không gọi lại để ghi đè. Nếu cần phân tích phiên bản khác, tạo config mới với output root mới rồi dùng `--config`. C-sweep chỉ final accuracy, không tự tạo A-bar cho các C khác. Kế hoạch refit riêng xem BLOCKED_AND_FOLLOWUP.md; chưa chạy control nặng.

## Tạo slide StrictReview từ repository root

Không cần thay thư viện, `reports/package.json` có PptxGenJS4.0.1/JSZip. PowerPoint desktop dùng để xuất PDF/PNG; Poppler dùng đọc lại PDF.

Cập nhật 20/11: bản snapshot sensitivity đã nằm trong `experiments/strict-review/20261119/results.json`; cả builder JS và bước merge dùng tệp này. Thành viên có clone repository và các dependency có thể tạo lại bản nháp bằng `prepare_strict_content.py`, `build_strict_review.mjs`, `merge_strict.py`, rồi render. Không cần raw `outputs/` cho các bước dựng đó. Hai lệnh audit/generate bên dưới và full finalizer cần artifact/log gốc để kiểm chứng sâu; chúng không phải điều kiện chỉ để mở hoặc đọc file PPTX/PDF đã công bố. Không giả vờ đã kiểm tra checkpoint nếu máy clone chưa có chúng.

```powershell
.venv-cpu/Scripts/python.exe -u -X utf8 reports/strict_review/audit_strict.py
.venv-cpu/Scripts/python.exe -X utf8 reports/strict_review/generate_reports.py
.venv-cpu/Scripts/python.exe -X utf8 reports/strict_review/prepare_strict_content.py
node reports/milestone2_final/build_strict_review.mjs
.venv-cpu/Scripts/python.exe -X utf8 reports/strict_review/merge_strict.py
powershell -NoProfile -ExecutionPolicy Bypass -File reports/milestone2_final/render_strict_review.ps1
.venv-cpu/Scripts/python.exe -X utf8 reports/strict_review/validate_and_finalize.py
```

Builder dùng3Seeds_Final làm gói nền, chỉ thay layout cần sửa/notes/citations, giữ nguyên byte mọi chart/workbook cũ. Chart10 mới liên kết SD đến ô workbook, chỉnh sửa được. Nguồn copy học thuật là `prepare_strict_content.py`, layout mới là `layout_overrides.mjs`. File cuối có tên phiên bản riêng; finalizer không ghi đè file có hash khác. File tạm/PNG ở `reports/milestone2_final/.build/strict-review/`. Sau mỗi lần đổi dữ liệu, phải xem lại toàn bộ40slide ở bản render cuối và cập nhật receipt visual-review; validator không thay cho người đọc.

Để cập nhật seed về sau: xác minh run finished/config/caches/phase metrics trước; cập nhật snapshot đúng nguồn và sửa pipeline tổng hợp, không gõ mean/std tay vào PPTX. Nếu làm sensitivity activation khác, phải refit comphead, không chỉ đổi activation khi suy luận.

## Công bố và nộp

Đợt này không tự push. Nhóm review localchanges rồi cho phép công bố source/evidence/slide trong một đợt riêng. Giữ data/weights/cache/venv/credentials ngoài Git; giữ `.gitattributes -text` cho snapshots. Sau khi công bố, đọc lại public bytes/hyperlinks. Nộp PPTX dưới20MB với tênID03 và repoURL ở hai mục Moodle riêng. Chưa tự nhận đã nộp bài hoặc đã được giảng viên xác nhận Core/Forge.
