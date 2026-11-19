# Thực nghiệm độc lập seed 0, 1, 2

Cập nhật UTC: 2026-11-19T09:53:49.735130+00:00

## Kết quả đã hoàn thành và xác minh

| Seed | Phương pháp | A-bar (%) | A_K (%) | Fit (s) | W&B |
| --- | --- | ---: | ---: | ---: | --- |
| 0 | acil-k5 | 65.788003 | 56.560000 | 39.015 | [h2sljkd5](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/h2sljkd5) |
| 0 | dac-no-plc-k5 | 65.482976 | 56.240000 | 84.009 | [gpx1ehdu](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/gpx1ehdu) |
| 0 | dsal-k5 | 65.821872 | 56.870000 | 86.513 | [i0kiycme](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme) |
| 1 | acil-k5 | 64.816422 | 56.550000 | 44.045 | [i0jt6hm8](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0jt6hm8) |
| 1 | dac-no-plc-k5 | 64.575860 | 56.470000 | 88.838 | [jzgqywsg](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/jzgqywsg) |
| 1 | dsal-k5 | 64.919306 | 56.890000 | 89.405 | [8tlegrwo](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/8tlegrwo) |
| 2 | acil-k5 | 64.791296 | 56.000000 | 41.183 | [7dg5j40m](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/7dg5j40m) |
| 2 | dac-no-plc-k5 | 64.784081 | 56.200000 | 85.904 | [5hnhr4tm](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/5hnhr4tm) |
| 2 | dsal-k5 | 65.031647 | 56.560000 | 83.814 | [9pij1vti](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/9pij1vti) |

## Tổng hợp ba seed

SD là độ lệch chuẩn mẫu (ddof=1), chỉ tính khi đủ ba seed hợp lệ và có bằng chứng W&B.

| Phương pháp | n | A-bar mean ± SD (%) | A_K mean ± SD (%) |
| --- | ---: | ---: | ---: |
| acil-k5 | 3 | 65.1319 ± 0.5683 | 56.3700 ± 0.3205 |
| dac-no-plc-k5 | 3 | 64.9476 ± 0.4752 | 56.3033 ± 0.1457 |
| dsal-k5 | 3 | 65.2576 ± 0.4919 | 56.7733 ± 0.1850 |

## Đối chiếu bài báo

DS-AL, CIFAR-100 / ResNet-32 / B50 / K5, Table 1: A-bar = 66,39%, A_K = 58,26% (trung bình ba lần chạy). DOI: https://doi.org/10.1609/aaai.v38i15.29670.
Không dùng ImageNet-Full Table 2 để đối chiếu trực tiếp ablation CIFAR-100.

Chênh lệch DS-AL so với bài báo: A-bar -1.1324 pp; A_K -1.4867 pp.
Ba seed chưa đủ để khẳng định ý nghĩa thống kê. Sai khác có thể gắn với implementation độc lập, class order và chi tiết huấn luyện; không suy ra nguyên nhân chỉ từ bảng điểm.

## Thời gian và tài nguyên

Huấn luyện và analytic chạy tuần tự trong `.venv-cpu`: PyTorch 2.5.1+cpu, 8 CPU threads. Seed 0 cũng dùng môi trường CPU này. Giữ nguyên 160 epoch, batch 128, B50, K5, buffer 8192, FP64, analytic batch 512, gamma 0,1, C=0,6.
Fit/elapsed lấy từ log thật. Peak RAM được lấy mẫu mỗi 10 giây, có thể bỏ lỡ đỉnh ngắn. Đây không phải benchmark thời gian trên phần cứng được kiểm soát.

| Công đoạn | Exit | Thời gian (phút) | Peak RSS lấy mẫu (GiB) |
| --- | ---: | ---: | ---: |
| seed-independence-check | 0 | 0.17 | 0.006 |
| seed-independence-check | 0 | 0.17 | 0.004 |
| seed1-backbone-features | 0 | 185.84 | 1.053 |
| seed1-core-three-methods | 0 | 4.01 | 1.576 |
| seed1-core-three-methods | 0 | 0.17 | 0.004 |
| seed1-wandb-sync | 1 | 0.33 | 0.139 |
| seed1-wandb-sync | 0 | 0.17 | 0.006 |
| seed2-backbone-features | 0 | 179.99 | 1.053 |
| seed2-core-three-methods | 0 | 3.84 | 1.573 |
| seed2-wandb-sync | 0 | 4.67 | 0.149 |

## Trạng thái còn thiếu

Không còn thiếu kết quả trong phạm vi ba phương pháp × ba seed.

## Tái lập và checkpoint

Git HEAD: `d8d485f6cbf10e266adf59b82a49a0265267e93c`. Working tree có thay đổi; `provenance.json` lưu hash chính xác source/config. Bản sao source nằm trong `outputs/multiseed-20261119/source_snapshot/`, không chứa `.env` hoặc credentials.
Checkpoint riêng tại `checkpoints/multiseed-20261119/`, gồm model, optimizer, scheduler, RNG và DataLoader; thay thế nguyên tử mỗi epoch. Không tái sử dụng backbone seed 0 cho seed 1/2.
Cùng seed: dùng chung backbone, class order, feature cache và projection seed. Khác seed: thay cả class order, khởi tạo backbone, shuffle/augmentation và projection, không chỉ tên run.
Analytic chưa hỗ trợ resume giữa pha. Nếu gián đoạn, giữ nguyên attempt cũ rồi tính lại toàn bộ phương pháp cùng cấu hình; không ghép các attempt khác cấu hình.
Không mở rộng khảo sát K/buffer hoặc thay đổi slide. W&B được sync từ bản sao, xác minh config/summary/history. Không lưu API key trong source/config Git.
