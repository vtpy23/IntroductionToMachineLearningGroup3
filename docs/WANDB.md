Cập nhật bàn giao 20/11/2026: xem [trạng thái nhóm](../TEAM_HANDOFF.md) và [mapping đầy đủ 24 run](../reports/strict_review/EXPERIMENT_MAPPING.md). Ba run sensitivity C mới dùng final classifier đã lưu, không huấn luyện/refit lại:

| Seed | Run C-sensitivity | Bằng chứng |
|---:|---|---|
|0 |[i2c96w3y](https://app.forge.coreweave.com/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i2c96w3y) |[config/history/analysis](../experiments/strict-review/20261119/saved-C-sensitivity-seed0/) |
|1 |[cu5nowzq](https://app.forge.coreweave.com/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/cu5nowzq) |[config/history/analysis](../experiments/strict-review/20261119/saved-C-sensitivity-seed1/) |
|2 |[xq49tulq](https://app.forge.coreweave.com/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/xq49tulq) |[config/history/analysis](../experiments/strict-review/20261119/saved-C-sensitivity-seed2/) |

Benchmark ACIL, DAC không PLC và DS-AL đã đủ seed 0/1/2. Chín run phương pháp và ba run backbone đã được đối chiếu log/config/history với Forge, tất cả finished và public. Xem [kết quả ba seed](../experiments/multiseed/20261119/RESULTS.md), [báo cáo hoàn tất](../experiments/multiseed/20261119/COMPLETION_REPORT.md) và [snapshot dùng cho slide](../reports/milestone2_final/assets/three_seeds_verified.json). Mean ± SD mẫu dùng ddof=1; K/buffer giữ seed 0. Những bảng smoke và ghi nhận ngày 17/11 dưới đây là lịch sử, không thay cho benchmark hiện hành.

W&B của nhóm 03 dùng API Forge `https://api.forge.coreweave.com` và project [intro-ml-group3-dsal](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal).

Routing entity/project/server được lưu trong `.env` cục bộ, đã được Git ignore. Credentials do `wandb login` quản lý ở máy người dùng. Không đặt API key trong source, config thí nghiệm hoặc lệnh có tham số key.

Run [connection-test](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/eoq2736v) chỉ xác minh đăng nhập, quyền ghi và đọc lại qua API; không chứa số liệu nghiên cứu.

Các run dưới đây xuất phát từ log offline đã có, được giữ nguyên run ID:

| Phạm vi | Run | Dữ liệu |
| --- | --- | --- |
| Smoke: backbone | [base-training](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/ncygqogl) | CIFAR-100 rút gọn, 2 epoch |
| Smoke: ACIL | [acil](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/xtiy6508) | CIFAR-100 rút gọn, buffer 128 |
| Smoke: DAC không PLC | [dac-no-plc](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/hib950j6) | CIFAR-100 rút gọn, buffer 128 |
| Smoke: DS-AL | [dsal](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/klafufff) | CIFAR-100 rút gọn, buffer 128 |
| Cơ chế: phụ thuộc số pha | [phase-dependence](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/hh31425p) | Tổng hợp, 3 seed |
| Cơ chế: ridge residual | [ridge-residue](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/is6rnul0) | Tổng hợp, 3 seed |
| Cơ chế: chi phí theo buffer | [scaling](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/p343muf2) | Tổng hợp, 3 seed |
| Đối chiếu công thức với mã tác giả | [reference-comparison](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/nv8x5tld) | Đầu vào tổng hợp nhỏ |

Các run trong bảng trên là smoke/synthetic/đối chiếu công thức. CIFAR-100 seed 0 hiện đã hoàn tất 160 epoch và đủ 8 biến thể; cả backbone và các biến thể đã đồng bộ công khai. Xem [bảng kết quả seed 0](../experiments/reproduction/RESULTS.md). Benchmark chính nay đã có ba seed; các khảo sát K/buffer vẫn chỉ seed 0.

Logging hiện có lưu config, provenance, seed, loss/accuracy/lr từng epoch, accuracy lớp gốc/lớp mới/tổng và thời gian fit từng pha, cùng summary trung bình/pha cuối. Trục biểu đồ run mới sử dụng `base/epoch` và `cil/phase`. Các thí nghiệm cơ chế giữ phép đo thật của từng seed trong history.

Đồng bộ thủ công các run mới hoàn tất:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m scripts.sync_wandb --dry-run
.\.venv\Scripts\python.exe -X utf8 -m scripts.sync_wandb
```

Script chọn run theo summary hoàn tất và run ID, xác minh tài khoản/project trước upload, sao chép thư mục run vào `artifacts/wandb-sync/` rồi đồng bộ bản sao. File gốc trong `outputs/`, checkpoint và kết quả đo giữ nguyên. URL và trạng thái xác minh được lưu riêng ở `outputs/wandb-sync-*.json`; `scripts.summarize` đọc thông tin này khi tạo bảng lần sau. Script từ chối ghi đè run ID trên server nếu không khớp hash của dữ liệu đã đồng bộ, và bỏ qua run đã được xác minh.

Run public được kiểm tra qua GraphQL bằng phiên HTTP không dùng credentials, `.netrc` hoặc cookie đăng nhập. Public chỉ xác nhận quyền đọc; việc một thí nghiệm có đáp ứng protocol bài báo còn phụ thuộc config và phạm vi dữ liệu.

Kiểm tra ngày 17/11/2026: 8 run thực nghiệm finished/public, 64 dòng history và 356 giá trị đo khớp log offline; 113 file kết quả gốc giữ nguyên SHA-256. Có sai số biểu diễn JSON ở summary DS-AL khoảng 1.78e-15; đối chiếu số thực dùng relative tolerance 1e-12, không sửa số đo. Bộ kiểm thử dự án: 11 passed. Tracker được kiểm tra offline trên cả SDK 0.23.1 của `.venv-cpu` và 0.31.0 của `.venv`.

Máy hiện tại có watcher cục bộ tại `artifacts/wandb-integration/watch_sync.py`, kiểm tra mỗi 60 giây và đồng bộ sau khi summary hoàn tất và file W&B ổn định qua hai lần đọc. Trạng thái ở `artifacts/wandb-integration/watcher-status.json`. Watcher giữ nguyên tiến trình huấn luyện, dùng SDK 0.31.0 để sync, dừng khi pipeline hoàn tất/thất bại hoặc có `.stop-project`. Watcher không phải dịch vụ tự khởi động sau khi Windows khởi động lại.
