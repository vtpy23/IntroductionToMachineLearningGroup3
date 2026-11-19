# Hoàn tất thí nghiệm ba seed

Đã hoàn thành ACIL, DAC không PLC và DS-AL cho seed 0, 1, 2. Chín run scientific và ba backbone run được xác minh finished, công khai, config/summary/history khớp dữ liệu cục bộ. Không còn thiếu thí nghiệm trong phạm vi này.

## Kết quả mean ± sample SD

Accuracy tính bằng %, SD mẫu dùng ddof=1, n=3. Từng seed và URL W&B xem [RESULTS.md](RESULTS.md).

| Phương pháp | A-bar mean ± SD (%) | A_K mean ± SD (%) |
| --- | ---: | ---: |
| acil-k5 | 65.1319 ± 0.5683 | 56.3700 ± 0.3205 |
| dac-no-plc-k5 | 64.9476 ± 0.4752 | 56.3033 ± 0.1457 |
| dsal-k5 | 65.2576 ± 0.4919 | 56.7733 ± 0.1850 |

## Đối chiếu bài báo

Nguồn: Table 1, CIFAR-100 / ResNet-32 / B50 / K5, giá trị không trong ngoặc; [DS-AL, AAAI 2024](https://doi.org/10.1609/aaai.v38i15.29670).

| Phương pháp | A-bar bài báo | Chênh A-bar (pp) | Chênh tương đối (%) | A_K bài báo | Chênh A_K (pp) | Chênh tương đối (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| acil-k5 | 66.30 | -1.1681 | -1.762 | 57.78 | -1.4100 | -2.440 |
| dsal-k5 | 66.39 | -1.1324 | -1.706 | 58.26 | -1.4867 | -2.552 |

DAC không PLC là ablation chuyển sang CIFAR-100, không đối chiếu trực tiếp với ImageNet-Full Table 2. Ba seed còn ít để suy luận ý nghĩa thống kê hoặc nguyên nhân sai lệch.
Seed 0 có 19 epoch CUDA trước khi resume sang CPU; seed 1/2 dùng CPU xuyên suốt. Vì vậy không coi độ biến thiên đo được là chỉ do seed hoặc so thời gian giữa seed như một benchmark phần cứng kiểm soát. Xem [PREFLIGHT.md](PREFLIGHT.md).

## Thời gian và tài nguyên

Tổng wall time của hai lượt backbone/features và hai suite ba phương pháp: 6.2279 giờ. Không cộng thời gian chờ giữa các phiên, đồng bộ W&B hoặc diagnostic vào chi phí scientific này.
Peak RSS lấy mẫu: 1.576 GiB; peak private memory lấy mẫu: 2.160 GiB. Lấy mẫu mỗi 10 giây nên có thể bỏ lỡ đỉnh ngắn. CPU i7-13620H, 8 PyTorch threads, torch 2.5.1+cpu.
Từng công đoạn, cả lần sync bị lỗi và lần khôi phục, được giữ trong logs/receipts. [SYNC_RECOVERY.md](SYNC_RECOVERY.md) ghi bản sửa support; mã học thuật và hyperparameters không đổi.

## Kiểm chứng và khả năng tái lập

Đã đọc lại checkpoint epoch 160, optimizer/scheduler/RNG, feature cache và chín classifier. Trong cùng seed, projection và feature identity khớp; giữa các seed, class order, khởi tạo và trọng số backbone cuối khác nhau. Không huấn luyện hoặc inference lại trong bước audit.
Source snapshot ban đầu và snapshot support v2 được giữ riêng; provenance ghi Git HEAD, dirty state, hash source/config và thay đổi chỉ ở công cụ sync. Evidence nhẹ được sao chép byte-identical vào `evidence/seed0`, `evidence/seed1`, `evidence/seed2` và có SHA-256 ở `verification/completion-audit.json`.
Seed 0 và số liệu seed 1 giữ nguyên hash. Không chạy thêm khảo sát K/buffer. Slide v3 PPTX/PDF giữ nguyên hash. Các khảo sát K/buffer vẫn chỉ có seed 0 và không được gộp vào mean/SD ba seed.

## Việc tiếp theo

- Cập nhật slide khi nhóm yêu cầu; chưa sửa slide trong đợt này.
- Có thể công bố source/config/evidence nhẹ và báo cáo lên GitHub sau khi rà soát; không đưa checkpoint, data, `.env` hay credentials lên Git.
- Giữ bản sao checkpoint và feature cache để tái lập hoặc mở rộng sau.
