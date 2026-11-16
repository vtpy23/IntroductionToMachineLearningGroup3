# Đọc hiểu DS-AL

## Bài toán và ví dụ

Class-incremental learning (CIL) cung cấp các lớp mới theo pha. Khi dự đoán,
mô hình phải phân biệt tất cả lớp đã gặp, không được cho sẵn task ID.
Exemplar-free CIL không giữ ảnh cũ để replay. Ví dụ, hệ thống phân loại
động vật học chó/mèo trước, rồi chim/cá, nhưng vẫn phải nhận ra chó/mèo
mà không giữ lại ảnh huấn luyện của chúng.

DS-AL cố định biểu diễn ảnh và cập nhật bộ phân loại bằng đại số. Cần
phân biệt quên do cập nhật head với biểu diễn không đủ tốt cho lớp mới.
Định lý của bài xử lý nguồn thứ nhất trong bài toán ridge cụ thể.

## Công trình tiền nhiệm

1. **LwF** dùng distillation để giữ đầu ra mạng cũ khi học lớp mới. Dữ liệu
   hiện tại có thể đại diện kém cho kiến thức cũ khi phân phối thay đổi.
   Phải cân bằng loss mới/distillation, không có bảo đảm nghiệm bằng học
   gộp. Nguồn: Li và Hoiem, TPAMI 2018, DOI 10.1109/TPAMI.2017.2773081.
2. **ACIL** đóng băng backbone, mở rộng đặc trưng và giải least squares đệ
   quy. Có thể đạt nghiệm học gộp trên embedding cố định, nhưng một head
   tuyến tính trong không gian mở rộng có thể chưa khớp đủ tốt. Đây là
   tiền nhiệm trực tiếp. Nguồn: Zhuang et al., NeurIPS 2022,
   https://proceedings.neurips.cc/paper_files/paper/2022/hash/4b74a42fc81fc7ee252f6bcb6e26c8be-Abstract-Conference.html .
3. **iCaRL / replay** giữ exemplar để đại diện lớp cũ, cho phép cập nhật từ
   dữ liệu mới và cũ nhưng vi phạm exemplar-free và cần ngân sách lưu ảnh.
   Nguồn: Rebuffi et al., CVPR 2017.

## Ký hiệu

| Ký hiệu | Ý nghĩa |
|---|---|
| k=0..K | Pha gốc và K pha tăng dần |
| N_k, c_k | Số mẫu hiện tại, số lớp tích lũy |
| f(x), d | Feature backbone cố định, chiều feature |
| B, m | Phép chiếu cố định, chiều mở rộng |
| X_M, X_C | Embedding ReLU và embedding activation khác |
| W_M, W_C | Head chính và head bù |
| gamma, C | Hệ số ridge, hệ số cộng điểm nhánh bù |

## Phương pháp và bảo đảm

Huấn luyện CNN trên base classes bằng BP, đóng băng CNN, thay classifier.
Nhánh chính dùng ReLU(B(f(x))) và giải:

\[
\min_W \|Y-XW\|_F^2+\gamma\|W\|_F^2,
\quad W=(X^TX+\gamma I)^{-1}X^TY.
\]

Đặt R=(X^TX+gamma I)^(-1). Trước pha mới, thêm cột 0 vào W. Woodbury
cho phép cập nhật R và W bằng dữ liệu hiện tại, công thức (11)-(12).
Supplement A chứng minh bằng ma trận tương quan và tương quan chéo
cộng dồn, có mở rộng chiều nhãn.

**Theorem 1 bảo đảm:** trong số học chính xác, cùng embedding, gamma và
dữ liệu, head chính cuối bằng nghiệm ridge học gộp. gamma>0 làm ma trận
khả nghịch ngay cả khi feature phụ thuộc tuyến tính.

**Giới hạn:** backbone/phép chiếu phải cố định. Không tương đương huấn
luyện lại toàn CNN với toàn dữ liệu. Nghiệm học gộp không có nghĩa
accuracy lớp cũ không thể giảm khi có thêm lớp cạnh tranh. Định lý chưa
tự chứng minh bất biến pha cho nhánh bù.

DAC dùng activation khác (thường Tanh) để học E_k=Y_k-X_M,k W_M,k.
Phải hoàn tất cập nhật nhánh chính của cả pha trước khi tạo residual.
PLC đặt residual ứng với lớp cũ về 0 ở pha tăng dần; base phase giữ
toàn residual. Suy luận cộng X_M W_M+C X_C W_C.

Residual pha cũ giữ nguyên như lúc được tạo, dù W_M tiếp tục đổi. Đây
là khác biệt quan trọng với nhánh chính học nhãn one-hot cố định.

## Hai solver độc lập

- `rls`: Woodbury cập nhật R và W qua batch.
- `stats`: cộng dồn G=gamma I+sum X^TX, Q=sum X^TY rồi giải Cholesky
  cuối pha. Cùng mục tiêu/nghiệm trong số học chính xác, chi phí khác.

Cả hai chỉ giữ thống kê, không exemplar. Kiểm thử đối chiếu với nghiệm
ridge trực tiếp và kiểm tra ảnh hưởng batch size. Không đánh đồng runtime
của hai solver.

## Độ phức tạp

Đặt m=chiều buffer, c=số lớp, b=batch, N=số mẫu. Hai ma trận tương quan
cần O(m²), hai head O(mc), phép chiếu O(dm). Trạng thái không tăng theo
số ảnh lịch sử khi m,c cố định, nhưng vẫn tăng theo số lớp. Hai ma trận
m=8192 float64 chiếm 1 GiB, chưa tính tensor tạm và phép giải.

RLS mỗi batch: khoảng O(bm²+b²m+b³+bmc), tùy thứ tự phép toán. Stats:
O(Nm²+Nmc) cộng O(m³+m²c) mỗi lần giải. Tính riêng backbone, cache feature
và suy luận. Công khai solver khi đối sánh thời gian.

## Protocol và số của tác giả

Datasets: CIFAR-100, ImageNet-100, ImageNet-Full. Base chứa nửa số lớp,
phần còn lại chia qua K pha. CIFAR dùng ResNet-32, có thêm ResNet-18 để
so sánh một số phương pháp. Thí nghiệm 500 pha thuộc ImageNet-Full.

A_k đánh giá trên tất cả lớp đã thấy. A-bar=(sum A_k)/(K+1), gồm pha0;
A_K là pha cuối. Thay K làm đổi các tập đánh giá trung gian, nên trọng
số cuối giống nhau cũng không buộc A-bar giống nhau.

Table 1, CIFAR-100 / ResNet-32 (%, số của tác giả):

| K | ACIL A-bar | DS-AL A-bar | ACIL A_K | DS-AL A_K |
|---:|---:|---:|---:|---:|
| 5 | 66.30 | 66.39 | 57.78 | 58.26 |
| 25 | 65.95 | 66.20 | 57.65 | 58.32 |
| 50 | 66.01 | 66.33 | 57.83 | 58.37 |

Số CIFAR đặt trong ngoặc ở bảng gốc thuộc ResNet-18, không dùng làm mốc
cho ResNet-32 của nhóm.

## Chi tiết tái hiện

Supplement C: SGD160 epochs, lr0.1 giảm tại80/120, momentum0.9, weight
decay5e-4, batch128 cho CIFAR/ResNet-32. Có crop/flip/normalization ở
base training, không augmentation ở AL.

README hiện tại của tác giả dùng scheduler/augmentation khác và lời mô
tả augmentation trong paper không khớp Supplement C. Nhóm bám Supplement.
PDF chưa đủ để biết chính xác phân phối projection và class order từng
run; nhóm công khai Normal(0,1), không bias, NumPy RandomState class order.
Tác giả trung bình ba run; một seed của nhóm chỉ là kết quả sơ bộ.

Nguồn: DS-AL công thức (1)-(19), Figures1-5, Tables1-2, Supplement A-C.
