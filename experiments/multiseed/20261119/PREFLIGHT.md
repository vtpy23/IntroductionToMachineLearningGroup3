# Kiểm tra trước khi chạy seed 1 và 2

## Protocol và phạm vi

- CIFAR-100 đầy đủ: 50.000 ảnh train, 10.000 ảnh test; Hugging Face revision `aadb3af77e9048adbea6b47c21a81e47dd092ae5` đã lưu trong cache.
- B50, K=5: sáu lần đánh giá tại 50, 60, 70, 80, 90, 100 lớp. A-bar tính trung bình sáu độ chính xác này, giống pipeline seed 0.
- Mỗi seed mới huấn luyện ResNet-32 độc lập, 160 epoch, batch 128, SGD lr 0,1, momentum 0,9, weight decay 0,0005, giảm lr tại epoch 80 và 120. Dùng checkpoint epoch cuối, không chọn checkpoint bằng test accuracy.
- Ba phương pháp: ACIL, DAC không PLC, DS-AL. Buffer 8192, analytic batch 512, sufficient statistics, FP64, gamma 0,1, compensation ratio 0,6. Giữ nguyên mã học thuật đã chạy seed 0.
- Trong cùng seed, ba phương pháp dùng chung class order, checkpoint, feature cache và random projection. Giữa các seed, thay class order, khởi tạo backbone, thứ tự minibatch/augmentation và random projection; không chỉ đổi tên run.
- Không mở rộng khảo sát K hoặc buffer. Ablation DAC/PLC vẫn là phạm vi chuyển sang CIFAR-100, không phải nguyên Table 2 của ImageNet-Full.

## Điều kiện thực thi

Máy có RTX 4050 Laptop 6 GB và 15,71 GiB RAM vật lý. Lúc kiểm tra đầu, chỉ còn khoảng 1,03 GiB RAM trống và 5,44 GiB Windows commit headroom. Ổ D còn khoảng 13,94 GiB, ổ C còn khoảng 8,60 GiB. Dữ liệu cần thiết đã có sẵn, không cần tải lại.

Theo sự cho phép của người dùng, đã đóng các tiến trình nền của Zalo, Viber và Copilot. Giữ các dịch vụ SQL Server hoạt động. Script mở lại ứng dụng nằm tại `artifacts/multiseed-resource-recovery/restore_apps.ps1`; bộ điều phối gọi script này khi hoàn tất hoặc dừng do lỗi.

Phép thử một batch 128 trên GPU là phép đo tài nguyên trên input tạo sẵn, **không phải thí nghiệm nghiên cứu**, không log accuracy lên W&B. PyTorch 2.5.1+cu121 và torchvision 0.20.1+cu121 import và thực thi được, GPU peak allocation khoảng 323 MiB, nhưng tiến trình đạt peak RSS khoảng 5,31 GiB, còn khoảng 0,24 GiB Windows commit headroom và 0,18 GiB RAM vật lý. Vì vậy không chạy training trên CUDA trong đợt này.

Chọn `.venv-cpu` đang hoạt động, PyTorch 2.5.1+cpu và torchvision 0.20.1+cpu, cùng môi trường CPU của lượt resume cuối đã hoàn thành seed 0. Kiểm tra sâu các offline attempt cho thấy seed 0 từng chạy bằng CUDA trước khi tiếp tục bằng CPU: các attempt CUDA có history tới epoch 19; run cuối `zuc29egg` ghi CPU và phát lại lịch sử trước điểm resume. Không khẳng định toàn bộ seed 0 được huấn luyện trên CPU hoặc các backend cho kết quả giống nhau từng bit. Đây là hạn chế cần ghi nhận khi diễn giải độ biến thiên ba seed, và thời gian seed 0 không phải baseline thuần CPU được kiểm soát. Bằng chứng tóm tắt nằm trong `outputs/multiseed-20261119/verification/seed0-prior-attempts.json`.

Seed 1 và 2 dùng CPU xuyên suốt. Giữ nguyên thuật toán, batch size và cấu hình huấn luyện; không đổi protocol dữ liệu/đánh giá. Không thay phiên bản Python/PyTorch/CUDA, không tự thay pagefile và không xóa virtual environment. GPU để trống trong lúc huấn luyện CPU.

Máy đang cắm điện lúc khởi chạy, pin 96%. Bộ điều phối giữ máy không tự sleep trong khi hoạt động và trả lại trạng thái này khi thoát. Việc tắt máy, đóng nắp hoặc khởi động lại vẫn có thể ngắt tiến trình; checkpoint cho phép tiếp tục.

## Thời gian và dung lượng

Log seed 0 có đủ 160 epoch; tổng thời gian ghi theo epoch là 14.791,432 giây, tương đương 246,52 phút. Median khoảng thời gian mỗi epoch và tốc độ cuối lượt thay đổi nhiều theo tài nguyên thực tế; dự trù ban đầu khoảng 8–10 giờ cho hai seed trên CPU. Suite seed 0 gồm 8 biến thể mất khoảng 9,5 phút, nên không dùng thời gian toàn suite này làm thời gian của ba phương pháp mới.

Sau bốn epoch thật đầu của seed 1, tốc độ ổn định khoảng 69 giây/epoch, tương đương khoảng 6,1 giờ cho 320 epoch nếu duy trì tốc độ này. Ước tính cập nhật khoảng 6–8 giờ cho toàn đợt, tùy tải máy và thời gian analytic/sync; đây là dự báo thời gian, không phải kết quả đã hoàn thành.

Ước tính dữ liệu mới nhỏ hơn 0,5 GiB: mỗi seed có checkpoint vài MiB, feature cache khoảng 15 MiB và ba classifier khoảng vài chục MiB tổng cộng, cộng logs/W&B/source snapshot. Mỗi ma trận FP64 8192 × 8192 chiếm 0,5 GiB; DS-AL giữ hai stream và cần thêm workspace Cholesky, projection/batch/evaluation. Dự trù khoảng 2–3 GiB RAM cho analytic; mức dùng thực tế được lấy mẫu mỗi 10 giây. Bộ điều phối yêu cầu ít nhất 4 GiB commit headroom và 2 GiB dung lượng ổ đĩa trước mỗi công đoạn; không chạy hai worker đồng thời.

## Kiểm tra môi trường và resume

- 13 kiểm thử qua, gồm kiểm thử resume so với lượt chạy không gián đoạn, các bất biến của analytic learning và kiểm thử không tính mean/SD khi thiếu seed.
- Checkpoint seed 0 ở epoch 160; các trường model, optimizer, scheduler, RNG và DataLoader được kiểm tra riêng bằng worker CPU.
- Hash class order, backbone khởi tạo và projection của seed 0/1/2 được kiểm tra phải khác nhau; ghi tại `outputs/multiseed-20261119/verification/seed-independence.json`. Đây là phép kiểm tra độc lập, không sinh số liệu accuracy.
- Checkpoint riêng: `checkpoints/multiseed-20261119/seed1-resnet32.pt` và `seed2-resnet32.pt`. Không tái sử dụng checkpoint seed 0.
- Nếu analytic bị ngắt, giữ nguyên attempt dở trong `interrupted_attempts/`, rồi chạy lại toàn phương pháp bằng config và feature identity giống hệt; không ghép các pha từ hai attempt.
- Source, config và dataset metadata được hash; bộ điều phối từ chối chạy công đoạn tiếp theo nếu chúng thay đổi. Git HEAD và bản sao source chính xác được lưu vì working tree đang có thay đổi.
- `pip check` còn báo xung đột ở các thư viện hệ thống không dùng trong pipeline (OpenCV, PaddleX, PDF/PyMuPDF, psd-tools/Pillow, torchaudio). Không nâng cấp/gỡ các thư viện này. Các import và kiểm thử thực tế của pipeline CPU đều qua. Không còn xung đột OpenTelemetry xuất hiện trong kết quả `pip check` lần này.

## W&B

SDK 0.31.0 trong `.venv` đã xác thực với `https://api.forge.coreweave.com`, entity `vu-lam-vnuhcm-university-of-science`, project `intro-ml-group3-dsal`. Worker CPU dùng SDK 0.23.1 sẵn có ở chế độ offline; SDK 0.31.0 đồng bộ sau mỗi seed.

Đã đọc lại config, summary và history thực tế của bốn run seed 0: backbone `zuc29egg`, ACIL `h2sljkd5`, DAC không PLC `gpx1ehdu`, DS-AL `i0kiycme`; trạng thái đều `finished`. Kết quả đã được đối chiếu với log cục bộ. Không ghi lại kết quả hoặc thay đổi dữ liệu các run này.

Mỗi run mới có ID riêng. Sync thực hiện từ bản sao offline run, xác minh config/summary và từng phase accuracy/thời gian fit trên server, kiểm tra quyền đọc công khai và trạng thái `finished` trước khi đưa vào bảng tổng hợp. Không cần gửi API key trong chat; không lưu key vào source, config Git hoặc báo cáo.

## Sản phẩm tự động

- `RESULTS.md`, `results.json`, `results.csv`: bảng từng seed, URL run, trạng thái thiếu, mean và sample SD (ddof=1) chỉ khi đủ ba seed đã xác minh.
- `provenance.json`, `configs/`: cấu hình và phiên bản mã nguồn chính xác.
- `outputs/multiseed-20261119/`: log, mẫu tài nguyên, trạng thái, source snapshot, W&B manifests và bằng chứng kiểm tra.
- Slide và kết quả seed 0 được giữ nguyên.
