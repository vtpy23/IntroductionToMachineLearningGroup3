# Ba seed đã xác minh

Nguồn: logs/config/checkpoint cục bộ và 12 run Forge được đọc lại trực tiếp. SD mẫu ddof=1, n=3; không dùng SE hoặc CI.

| Phương pháp | Seed | Ā (%) | A_K (%) | W&B |
|---|---:|---:|---:|---|
| acil-k5 | 0 | 65,7880 | 56,5600 | [h2sljkd5](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/h2sljkd5) |
| acil-k5 | 1 | 64,8164 | 56,5500 | [i0jt6hm8](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0jt6hm8) |
| acil-k5 | 2 | 64,7913 | 56,0000 | [7dg5j40m](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/7dg5j40m) |
| dac-no-plc-k5 | 0 | 65,4830 | 56,2400 | [gpx1ehdu](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/gpx1ehdu) |
| dac-no-plc-k5 | 1 | 64,5759 | 56,4700 | [jzgqywsg](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/jzgqywsg) |
| dac-no-plc-k5 | 2 | 64,7841 | 56,2000 | [5hnhr4tm](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/5hnhr4tm) |
| dsal-k5 | 0 | 65,8219 | 56,8700 | [i0kiycme](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme) |
| dsal-k5 | 1 | 64,9193 | 56,8900 | [8tlegrwo](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/8tlegrwo) |
| dsal-k5 | 2 | 65,0316 | 56,5600 | [9pij1vti](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/9pij1vti) |

| Phương pháp | Ā mean ± SD (%) | A_K mean ± SD (%) |
|---|---:|---:|
| acil-k5 | 65,1319 ± 0,5683 | 56,3700 ± 0,3205 |
| dac-no-plc-k5 | 64,9476 ± 0,4752 | 56,3033 ± 0,1457 |
| dsal-k5 | 65,2576 ± 0,4919 | 56,7733 ± 0,1850 |

## Chênh lệch ghép cặp

| Đối sánh | ΔĀ mean ± SD (pp) | ΔA_K mean ± SD (pp) | ΔA_K seed 0 / 1 / 2 (pp) |
|---|---:|---:|---|
| DS-AL − ACIL | 0,1257 ± 0,1051 | 0,4033 ± 0,1365 | 0,31 / 0,34 / 0,56 |
| PLC: DS-AL − DAC không PLC | 0,3100 ± 0,0541 | 0,4700 ± 0,1418 | 0,63 / 0,42 / 0,36 |
| DAC không PLC − ACIL | -0,1843 ± 0,1567 | -0,0667 ± 0,2603 | -0,32 / -0,08 / 0,20 |

## Diễn giải và giới hạn

Ā_s trung bình sáu pha của một seed; mean Ā là trung bình ba Ā_s. A_K chỉ đo pha cuối. SD đo biến động giữa ba seed, không dùng 18 pha làm 18 lần lặp độc lập.
DS-AL−ACIL và PLC−DAC không PLC đều dương ở ba seed cho cả Ā và A_K. DAC đơn lẻ không nhất quán ở A_K. Không có kiểm định nên chưa kết luận ý nghĩa thống kê.
DS-AL thấp hơn mean Table 1: Ā −1,1324 pp (−1,7057% tương đối), A_K −1,4867 pp (−2,5518%). ACIL: Ā −1,1681 pp, A_K −1,4100 pp. Không xác lập nhân quả cho gap từ những khác biệt cấu hình đã ghi nhận.
E2 chuyển ImageNet-Full/C=1,4 sang CIFAR-100/C=0,6, không là tái hiện nguyên Table 2 và không tự nhận giảng viên đã chấp nhận phạm vi. K/buffer giữ nguyên seed 0. Seed 0 resume CUDA→CPU sau epoch 19; seed 1/2 CPU xuyên suốt.
Config, class order, checkpoint SHA, dữ liệu từng pha, URLs và phép tính đầy đủ: assets/three_seeds_verified.json. Đã xác minh mỗi seed có checkpoint/feature cache riêng và trong seed ba phương pháp dùng chung projection/cache. Không huấn luyện lại hoặc thay đổi W&B khi cập nhật slide.

## Nguồn bài báo

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
