# Phạm vi Core

## Lab1

| ID | Phép đo | Thiết lập | Phạm vi |
|---|---|---|---|
| R1 | ACIL so với DS-AL | CIFAR-100 B50, ResNet-32, m8192, K5 | Một phần Table1, baseline AL trực tiếp |
| R2 | C-RLS, DAC không PLC, DAC+PLC | Cùng backbone/projection | Thiết kế Table2 chuyển từ ImageNet-Full sang CIFAR-100, phải công khai thay dataset |
| R3 | Thay số pha | K5/25/50, cùng backbone/projection | Độ ổn định accuracy, không suy bất biến chính xác từ A-bar |
| R4 | Phân tích bổ sung | m512/1024/2048 so với8192 | Accuracy, fit time, bộ nhớ |

Không tuyên bố tái hiện toàn bộ SOTA, ImageNet hoặc500 pha. Core chỉ trên
CIFAR phải được biện minh bằng tài nguyên/thời gian trong slide. Mở rộng
ImageNet-100 là hướng bổ sung, chưa thuộc pipeline cục bộ hiện tại.

Chạy seed0 hoàn chỉnh trước. `scripts.multiseed` hỗ trợ ba seed0/1/2,
backbone/class order riêng. Chỉ tính std từ run hoàn tất cùng protocol.
Trong mỗi seed, các ablation dùng chung backbone/projection.

## Lab2

| ID | Giả thuyết | Yếu tố thay đổi | Đo |
|---|---|---|---|
| E1 | Nhánh bù phụ thuộc phân hoạch | Số pha mới1/2/5, còn lại cố định | Delta W_M,W_C,scores, held-out accuracy |
| E2 | Residual ridge không trực giao | gamma1e-4..100 | norm X^TE và sai số normal equation |
| E3 | Buffer tăng chi phí | m64..1024 | Fit time, bytes ma trận |

E1/E2/E3 dùng dữ liệu Gaussian class clusters tổng hợp, ba seed0/1/2.
Không gắn accuracy tổng hợp với CIFAR. E3 timing sơ bộ ít lần lặp,
chưa phải benchmark hiệu năng chắc chắn.

## Quy tắc đánh giá

- A_k trên toàn bộ lớp đã thấy. A-bar gồm cả pha0.
- Khoảng cách accuracy tuyệt đối tính bằng điểm phần trăm. Độ lệch
  tương đối=(nhóm-paper)/paper ×100%.
- Ghi seed, class order, hash checkpoint, revision dataset, manifest
  source, dtype, solver, versions, phần cứng, thời gian và W&B runID.
- Chỉ đưa số paper vào phép tính sai lệch khi run đủ protocol đối sánh.
- Cache feature phục vụ hiệu suất. Method chỉ nhận dữ liệu pha hiện tại,
  không replay feature cũ vào fit.

## Mã gốc

`scripts.compare_reference` dùng checkout tác giả trong `artifacts/`
để kiểm chứng trên dữ liệu nhỏ, cùng projection số học. Đối chiếu một
batch bằng cả pha và nhiều batch nhỏ. Implementation nhóm bám SupplementB:
hoàn tất nhánh chính cả pha rồi mới sinh residual.
