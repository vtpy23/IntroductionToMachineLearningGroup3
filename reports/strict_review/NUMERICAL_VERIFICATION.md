# Kiểm chứng số liệu

> Publication update 2026-11-20: see [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md). The team reports submission and has authorized publishing this revision. References below to an unpushed/local-only revision describe the original 2026-11-19 review. Original files and their manifest are archived in [history](history/review-delivery-20261119.zip). The review score is not an official grade.

Audit trực tiếp UTC: 2026-11-19T15:11:33.502170+00:00

24 run finished, config/summary/history đọc được qua GraphQL **không đăng nhập**, khớp toàn bộ log. Đây là kiểm tra public data kỹ thuật, không tự chứng minh giảng viên chấp nhận host Forge thay cho wandb.ai.

## Ba seed: hai tầng trung bình

Ā_s=(Σ_{k=0}^5 A_{s,k})/6. Sau đó mean và SD mẫu của ba Ā_s; A_K tính riêng từ pha cuối. SD dùng ddof=1, không phải SE/CI. Không dùng 18 pha làm 18 lần lặp.

| Phương pháp | Ā mean ± SD (%) | A_K mean ± SD (%) | Base mean ± SD | Novel mean ± SD |
|---|---:|---:|---:|---:|
| acil-k5 | 65.131907 ± 0.568334 | 56.370000 ± 0.320468 | 68.293333 ± 1.098605 | 44.446667 ± 0.980680 |
| dac-no-plc-k5 | 64.947639 ± 0.475162 | 56.303333 ± 0.145717 | 63.866667 ± 1.090015 | 48.740000 ± 1.251080 |
| dsal-k5 | 65.257608 ± 0.491884 | 56.773333 ± 0.185023 | 66.160000 ± 1.233045 | 47.386667 ± 1.142337 |

## Gain và gap

DS-AL−ACIL A_K: +0,31/+0,34/+0,56pp, mean+0,403333pp (SD paired0,136504). PLC−DAC A_K: +0,63/+0,42/+0,36pp, mean+0,470000pp (SD paired0,141774). DAC−ACIL: −0,32/−0,08/+0,20pp, mean−0,066667pp.

Paper gain 58,26−57,78=0,48 pp, nhóm 0,403333 pp, chênh gain −0,076667 pp. Hai gain gần nhau về độ lớn không định danh nguyên nhân gap tuyệt đối. DS-AL Ā gap −1,132392 pp (−1,705666% tương đối), A_K gap −1,486667 pp (−2,551779% tương đối). Không khẳng định ý nghĩa thống kê.

## K đối sánh Table1, DS-AL ResNet32, chỉ seed0

| K | Paper Ā | Nhóm Ā | Paper A_K | Nhóm A_K | Gap A_K (pp) |
|---:|---:|---:|---:|---:|---:|
| 5 | 66.39 | 65.821872 | 58.26 | 56.87 | -1.39 |
| 25 | 66.20 | 65.543308 | 58.32 | 56.83 | -1.49 |
| 50 | 66.33 | 65.536096 | 58.37 | 56.87 | -1.50 |

## Sensitivity C: final classifier Tanh, ba seed

| C | A_K mean ± SD | Base mean | Novel mean |
|---:|---:|---:|---:|
| 0.0 | 56.370000 ± 0.320468 | 68.293333 | 44.446667 |
| 0.1 | 56.393333 ± 0.271539 | 67.933333 | 44.853333 |
| 0.2 | 56.436667 ± 0.228983 | 67.613333 | 45.260000 |
| 0.3 | 56.533333 ± 0.175594 | 67.253333 | 45.813333 |
| 0.4 | 56.616667 ± 0.187705 | 66.813333 | 46.420000 |
| 0.5 | 56.713333 ± 0.198578 | 66.480000 | 46.946667 |
| 0.6 | 56.773333 ± 0.185023 | 66.160000 | 47.386667 |
| 0.7 | 56.830000 ± 0.165227 | 65.840000 | 47.820000 |
| 0.8 | 56.830000 ± 0.105830 | 65.453333 | 48.206667 |
| 0.9 | 56.736667 ± 0.167432 | 65.033333 | 48.440000 |
| 1.0 | 56.603333 ± 0.164418 | 64.573333 | 48.633333 |

Đỉnh mean trong lưới tại C0,7/0,8:56,83%. Paper chỉ mô tả Tanh CIFAR đạt đỉnh quanh0,6; không dựng số tại những điểm Figure4 không ghi nhãn. Giữ C0,6 trong benchmark, không dùng test sweep để thay lựa chọn hyperparameter. Không có A-bar mới vì thiếu head từng pha.

## Paired prediction flips, cùng10.000 ảnh mỗi seed

| So sánh | Seed | Sửa sai | Làm hỏng | Net (pp) |
|---|---:|---:|---:|---:|
| dac_minus_acil | 0 | 310 | 342 | -0.32 |
| dsal_minus_acil | 0 | 195 | 164 | +0.31 |
| plc_minus_dac | 0 | 202 | 139 | +0.63 |
| dac_minus_acil | 1 | 330 | 338 | -0.08 |
| dsal_minus_acil | 1 | 204 | 170 | +0.34 |
| plc_minus_dac | 1 | 192 | 150 | +0.42 |
| dac_minus_acil | 2 | 342 | 322 | +0.20 |
| dsal_minus_acil | 2 | 219 | 163 | +0.56 |
| plc_minus_dac | 2 | 181 | 145 | +0.36 |

DAC mất4,426667pp base và tăng4,293333pp novel. PLC so DAC lấy lại2,293333pp base nhưng giảm1,353333pp novel. Hai nhóm bằng5.000 ảnh nên gain tổng bằng trung bình hai gain nhóm. Không suy rộng DAC luôn tốt hoặc PLC luôn tăng cả hai nhóm.

52 file gốc được kiểm tra SHA-256 sau phân tích, gồm classifier/checkpoint/cache/log và PPTX nguồn. ResNet32 chuyển cùng weights, float64,4 input tổng hợp: max abs feature 1.137e-13. Đây không phải đối chiếu accuracy CIFAR hoặc init/training.

Ba lượt suy luận mới mất tổng 1.474 giây tính score; không gồm import, hash, W&B và đọc đĩa. Không so số này với thời gian train/fit. Wrapper PowerShell ghi NativeCommandError do stderr của W&B; results.json hoàn tất và cả ba run được audit lại finished, đầy đủ11 điểm. Không coi wrapper exit này là kết quả scientific failure.
