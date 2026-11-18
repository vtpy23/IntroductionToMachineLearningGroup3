# Trạng thái dự án

Trạng thái pipeline và epoch hiện tại được đọc trực tiếp bằng:

```powershell
.venv/Scripts/python.exe -X utf8 -m scripts.status
```

## Đã có

- Nhóm xác nhận DS-AL được chấp nhận trên Moodle.
- Implementation C-RLS/RLS, sufficient statistics, DAC và PLC độc lập.
- ResNet-32 chuẩn, HF CIFAR-100 loader, caching có hash và class splits.
- Mathematical tests và pipeline smoke hoàn tất trên dữ liệu ảnh thật rút gọn.
- Ba thí nghiệm cơ chế tổng hợp, mỗi thí nghiệm ba seed, có số đo và W&B public.
- Đối chiếu mã gốc: cùng dữ liệu/projection và một batch mỗi pha cho sai số
  đầu ra cỡ1e-12; minibatch nhỏ dẫn đến khác residual targets.
- Bộ mới 40 slide tiếng Việt có notes, citations, 8 chart và 18 bảng native:
  [PPTX](../reports/milestone2_final/03.pptx),
  [PDF](../reports/milestone2_final/DSAL_Milestone2_Lab1_Final.pdf).
  Đã kiểm tra trực quan từng trang và số liệu seed 0; bản 30 slide cũ là legacy.
- Repo được xác nhận public khi công bố; người dùng cho phép push cả slide.
  [Mapping](../reports/milestone2_final/EXPERIMENT_TRACEABILITY.md) và
  [snapshot log/config](../experiments/evidence/README.md) truy vết từng run.
- Notes đọc hiểu, phản biện, kế hoạch đo và hướng dẫn chạy.

## Đang thực hiện / điều kiện còn thiếu

- CIFAR-100 seed 0: backbone 160 epochs và đủ 8 biến thể đã hoàn tất;
  cả 9 run gồm backbone đã đồng bộ và xác minh W&B công khai.
- Mean/std ba seed chỉ có sau `scripts.multiseed`, không tự tạo từ một seed.
- W&B: đã xác minh đăng nhập và quyền ghi/đọc công khai trên Forge. Các run
  smoke, cơ chế tổng hợp và đối chiếu công thức có liên kết tại [W&B](WANDB.md).
  Seed 1 và 2 chưa chạy; chưa có mean/std cho benchmark nhiều seed.
- PPTX/PDF mới đã cập nhật benchmark/W&B seed 0. Ablation DAC/PLC chuyển
  từ ImageNet-Full sang CIFAR-100 cần giảng viên chấp nhận phạm vi; không
  tự nhận tái hiện nguyên Table 2. Poster vẫn là bản nháp cho mốc sau.
- Bản bổ sung ImageNet-100/Full chưa nằm trong triển khai hiện tại.

## Quyết định triển khai

Máy: RTX4050 Laptop6GB, RAM16GB. Python3.11.8. Torch2.5.1 cho cả CUDA/CPU.
Tách tiến trình huấn luyện/trích feature dùng GPU khỏi tiến trình analytic
dùng CPU để giải phóng thư viện CUDA và bộ nhớ trước các ma trận8192².
Không chạy thêm một process PyTorch CUDA lớn song song trên máy này.
Một lần thiếu bộ nhớ đã được phát hiện; checkpoint từng epoch cho phép
tiếp tục và lịch sử run cục bộ vẫn được giữ.

AI hỗ trợ viết mã, tài liệu và nội dung báo cáo. Không tạo lịch sử commit
giả cho thành viên. Nhóm cần đọc, chạy và giải thích được toàn bộ sản phẩm.
