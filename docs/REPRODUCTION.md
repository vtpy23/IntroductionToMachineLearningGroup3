# Chạy dự án

## Windows

```powershell
./scripts/bootstrap.ps1 -Cuda
.venv/Scripts/python.exe -X utf8 -m scripts.doctor
.venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/python.exe -X utf8 -m scripts.run --config configs/cifar100_smoke.json --stage suite --tracking offline
.venv/Scripts/python.exe -X utf8 -m scripts.empirics --tracking offline
./scripts/start_pipeline.ps1 -Tracking offline
```

Pipeline chạy ẩn, log từng stage ở `outputs/pipeline/`, checkpoint mỗi
epoch. Trên Windows, chế độ auto chọn CPU khi commit memory còn dưới10GiB
để tránh CUDA initialization/allocation thất bại. Có thể chọn rõ bằng
`./scripts/start_pipeline.ps1 -Compute cpu` hoặc `-Compute cuda`.

Pipeline lưu checkpoint mỗi
epoch. Thứ tự: tests, smoke, kiểm tra cơ chế, tóm tắt ban đầu, seed0 đầy
đủ, tóm tắt cuối. Không suy process còn sống chỉ từ PIDfile: launcher
kiểm tra cả thời điểm bắt đầu process.

```powershell
.venv/Scripts/python.exe -X utf8 -m scripts.status
Get-Content -Tail 10 outputs/pipeline/core-suite.log
```

Tạo `.stop-project` tại root để dừng sau epoch hoặc trước run kế tiếp.
Xóa file đó rồi gọi launcher để resume. Không chạy hai pipeline vào
cùng output. Checkpoint lưu optimizer,scheduler,RNG và loader state.

## Ba seed và cloud

```bash
python -m scripts.run --config configs/cifar100_core.json --stage suite --tracking offline
python -m scripts.multiseed --seeds 0 1 2 --tracking offline
python -m scripts.summarize
```

Ba seed chạy nối tiếp, mỗi seed có backbone/class order riêng, không
tính ba projection trên cùng backbone thành ba lần tái hiện độc lập.
Notebook `notebooks/Colab_Kaggle.ipynb` nạp source archive và gọi cùng
entrypoint. Người dùng bật GPU và đăng nhập cloud. Local không cần mua
tài nguyên. Môi trường được thử trên Python3.11.8 / torch2.5.1+cu121.

## W&B

Đăng ký/đăng nhập https://wandb.ai và tạo project
`intro-ml-group3-dsal`, visibility Public. Entity nằm trong URL
`https://wandb.ai/<entity>/intro-ml-group3-dsal`.

```powershell
.venv/Scripts/python.exe -m wandb login
Copy-Item .env.example .env
```

Điền WANDB_ENTITY/WANDB_PROJECT vào `.env`. API key chỉ nhập prompt
cục bộ hoặc biến môi trường, không đưa vào source/chat. Run mới dùng
`--tracking online`. Run offline hoàn tất được đồng bộ bằng:

```powershell
.venv/Scripts/python.exe -X utf8 -m scripts.sync_wandb --entity TEN_ENTITY --project intro-ml-group3-dsal
.venv/Scripts/python.exe -X utf8 -m scripts.summarize
```

Script chỉ sync run hoàn tất, đọc lại URL qua API và kiểm tra quyền đọc
không xác thực. Chưa public/chưa xác minh thì `submission_ready=false`.
Run lỗi/dang dở không được coi như bằng chứng hoàn tất.

## So sánh mã gốc

```bash
git clone --depth 1 https://github.com/ZHUANGHP/Analytic-continual-learning.git artifacts/reference/official
python -m scripts.compare_reference --tracking offline
```

Checkout kiểm tra: `0afd6bf87622e808ce7f730f8556e78229b9e758`.
Mã gốc ở thư mục gitignore, chỉ dùng kiểm chứng. Xem số đo trong
`outputs/reference-comparison/comparison.json`. Không dùng README hiện
tại của tác giả thay cấu hình SupplementC.

## Giới hạn triển khai

PDF chưa xác định đủ projection distribution/class order từng run,
nên config công khai lựa chọn của nhóm. Solver mặc định stats/Cholesky
giải cùng objective với RLS nhưng không cùng runtime. Hai solver được
đối chiếu bằng kiểm thử. ResNet32 optionA là kiến trúc hỗ trợ chuẩn.

Thư viện phụ trợ: torchvision(transform), Pillow(ảnh), HFhub/pyarrow
(parquet trực tuyến), W&B(tracking), matplotlib(plots), dotenv(cấu hình
cục bộ), pytest(hợp đồng toán học). `requirements.txt` pin versions.
Venv cục bộ đầu tiên kế thừa package hệ thống; bootstrap máy mới tạo
venv độc lập. Không dùng torchaudio trong dự án.
