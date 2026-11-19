# Trạng thái dự án

Cập nhật 19/11/2026: benchmark ba seed đã hoàn thành. Trạng thái của đợt chạy này:

```powershell
Get-Content outputs/multiseed-20261119/status.json
```

## Đã có

- Nhóm xác nhận DS-AL được chấp nhận trên Moodle.
- Implementation C-RLS/RLS, sufficient statistics, DAC và PLC độc lập.
- ResNet-32 chuẩn, HF CIFAR-100 loader, caching có hash và class splits.
- Mathematical tests và pipeline smoke hoàn tất trên dữ liệu ảnh thật rút gọn.
- Ba thí nghiệm cơ chế tổng hợp, mỗi thí nghiệm ba seed, có số đo và W&B public.
- Đối chiếu mã gốc: cùng dữ liệu/projection và một batch mỗi pha cho sai số
  đầu ra cỡ1e-12; minibatch nhỏ dẫn đến khác residual targets.
- Bộ mới 40 slide tiếng Việt có notes, IEEE citations, 9 chart và 20 bảng native:
  [PPTX theo ID03](../reports/milestone2_final/submission_3seeds/03.pptx),
  [PDF](../reports/milestone2_final/DSAL_Milestone2_Lab1_3Seeds_Final.pdf).
  Đã render và kiểm tra trực quan từng trang, dữ liệu ba seed và custom error bars.
  Các bộ seed0 trước đây được giữ làm lịch sử, không phải bản nộp hiện tại.
- Repo được xác nhận public khi công bố; người dùng cho phép push cả slide.
  [Mapping](../reports/milestone2_final/EXPERIMENT_TRACEABILITY.md) và
  [snapshot log/config](../experiments/evidence/README.md) truy vết từng run.
- Notes đọc hiểu, phản biện, kế hoạch đo và hướng dẫn chạy.

## Thực nghiệm và điều kiện còn thiếu

- CIFAR-100 seed 0: backbone 160 epochs và đủ 8 biến thể đã hoàn tất;
  cả 9 run gồm backbone đã đồng bộ và xác minh W&B công khai.
- Seed1 và 2 hoàn tất backbone160 và ACIL/DAC không PLC/DS-AL K5. Chín run phương pháp
  và ba run backbone của seed0/1/2 đã xác minh finished/public cùng config/history.
  [Kết quả ba seed](../experiments/multiseed/20261119/RESULTS.md),
  [báo cáo hoàn tất](../experiments/multiseed/20261119/COMPLETION_REPORT.md).
  Mean ± SD mẫu dùng ddof=1; không lấy các pha làm lần lặp độc lập.
- W&B: đã xác minh đăng nhập và quyền ghi/đọc công khai trên Forge. Các run
  smoke, cơ chế tổng hợp và đối chiếu công thức có liên kết tại [W&B](WANDB.md).
  Các seed mới có log/config và bản sửa sync được ghi nhận riêng, không thay số đo.
- PPTX/PDF mới đã cập nhật benchmark/W&B ba seed. Ablation DAC/PLC chuyển
  từ ImageNet-Full sang CIFAR-100 cần giảng viên chấp nhận phạm vi; không
  tự nhận tái hiện nguyên Table 2. Poster vẫn là bản nháp cho mốc sau.
- Bản bổ sung ImageNet-100/Full chưa nằm trong triển khai hiện tại.

## Quyết định triển khai

Máy: RTX4050 Laptop6GB, RAM16GB. Python3.11.8. Torch2.5.1 cho cả CUDA/CPU.
Seed0 có đoạn CUDA rồi resume CPU sau epoch19. Seed1/2 dùng môi trường CPU sẵn có
vì phép thử CUDA thiếu commit headroom. Mỗi seed có backbone, checkpoint và cache riêng;
trong seed các phương pháp ghép cặp cùng projection, dữ liệu và feature identity.
Các công đoạn chạy tuần tự; hai seed mới dùng khoảng6,23 giờ compute, chưa gồm sync/chờ.
K/buffer vẫn chỉ seed0 và không có SD nhiều seed cho các khảo sát đó.
Không chạy thêm một process PyTorch CUDA lớn song song trên máy này.
Một lần thiếu bộ nhớ đã được phát hiện; checkpoint từng epoch cho phép
tiếp tục và lịch sử run cục bộ vẫn được giữ.

AI hỗ trợ viết mã, tài liệu và nội dung báo cáo. Không tạo lịch sử commit
giả cho thành viên. Nhóm cần đọc, chạy và giải thích được toàn bộ sản phẩm.
