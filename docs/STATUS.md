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
- Ba thí nghiệm cơ chế tổng hợp, mỗi thí nghiệm ba seed, có số đo và W&B offline.
- Đối chiếu mã gốc: cùng dữ liệu/projection và một batch mỗi pha cho sai số
  đầu ra cỡ1e-12; minibatch nhỏ dẫn đến khác residual targets.
- Notes đọc hiểu, phản biện, kế hoạch đo và hướng dẫn chạy.

## Đang thực hiện / điều kiện còn thiếu

- Full CIFAR-100: huấn luyện backbone160 epochs và suite m8192. Chỉ xem là
  hoàn tất khi summary của từng run ghi completed=true.
- Mean/std ba seed chỉ có sau `scripts.multiseed`, không tự tạo từ một seed.
- W&B công khai: người dùng tạo project và đăng nhập cục bộ. Chưa có URL
  công khai được xác minh thì các artifact thực nghiệm chưa đủ điều kiện nộp.
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
