# Phản biện lý thuyết và thí nghiệm kiểm chứng

## Ba điểm mạnh

**S1. Mục tiêu toàn cục rõ ràng.** Ridge với gamma>0 và embedding cố định
lồi nghiêm theo W. Theorem1/Woodbury giải thích khả năng đạt nghiệm học
gộp không cần replay. Kiểm thử đối chiếu nghiệm trực tiếp xác nhận hợp
đồng toán học này cho bản triển khai.

**S2. Trạng thái đủ không phải exemplar.** Ma trận tương quan/head thay
cho ảnh cũ, nên bộ nhớ không tăng theo số mẫu khi chiều/số lớp cố định.
Điều này không tương đương differential privacy hay chống suy luận dữ liệu.

**S3. DAC tăng lớp hàm dự đoán trong khi backbone cố định.** Embedding
thứ hai và head bù học residual. Table2 của tác giả hỗ trợ lợi ích thực
nghiệm của DAC/PLC. Không suy ra bảo đảm accuracy tăng trên mọi dữ liệu.

## L1: Bảo đảm nhánh chính chưa đủ cho bất biến pha của toàn DS-AL

Nhánh chính học one-hot cố định. Nhánh bù học nhãn tạo bởi W_M khi mỗi
pha kết thúc. Đổi phân hoạch pha làm đổi W_M trung gian và nhãn bù lịch
sử. PLC thêm phụ thuộc vào các lớp nào xuất hiện cùng pha. Vì vậy, cùng
dữ liệu cuối không đủ suy ra cùng W_C cuối.

**Kiểm chứng:** cùng dữ liệu, nhãn, projection, gamma,C, dtype/solver;
chỉ đổi số pha mới1/2/5. Đo delta tương đối W_M,W_C,scores và accuracy
held-out trên Gaussian class clusters, ba seed0/1/2. Nguồn đo:
`experiments/empirics/phase-dependence.json`.

Đã quan sát W_M khác ở cỡ sai số số học, W_C/scores thay đổi. Điều này
bác bỏ cách hiểu bất biến **chính xác** của toàn mô hình trong mọi phân
hoạch. Không bác bỏ accuracy gần ổn định trên benchmark cụ thể của tác
giả. Không đồng nhất delta trọng số với suy giảm accuracy lớn.

**F1:** lưu moment chéo giữa embedding để cập nhật mục tiêu residual
theo head chính hiện tại. Với objective residual toàn cục không PLC,
duy trì Q_CY=sum X_C^TY, H_CM=sum X_C^TX_M và dùng
W_C=(G_C+gamma_C I)^(-1)(Q_CY-H_CM W_M). Đây là hướng phương pháp mới,
cần phân tích chi phí và PLC riêng, không phải DS-AL đang tái hiện.

## L2: Diễn giải residual như null-space cần điều kiện thêm

Với E=Y-XW và nghiệm ridge, điều kiện dừng cho **X^TE=gamma W**. Khi
gamma>0 và W khác0, residual nói chung không trực giao với không gian
cột của X. OLS không regularization có tính trực giao quen thuộc dưới
điều kiện thích hợp. Residual trên riêng dữ liệu pha hiện tại còn không
tự kế thừa điều kiện toàn cục. Phải phân biệt null-space trái/phải và
kích thước ma trận.

Đây là hạn chế trong diễn giải hình học của DAC, không phải chứng minh
ridge sai hoặc toàn thuật toán không hoạt động.

**Kiểm chứng:** quét gamma1e-4..100 trên embedding cố định, đo norm X^TE
và norm(X^TE-gamma W) để phân biệt sai khác thật với lỗi triển khai.
Nguồn: `experiments/empirics/ridge-residue.json`. Phép đo kiểm tra đẳng
thức hình học, chưa đo lợi ích accuracy của phương pháp bù thay thế.

**F2:** phát biểu phép bù trực giao chính xác, hoặc giải thích bằng
residual regression có điều chuẩn. Đối sánh với DAC theo accuracy,
calibration và chi phí để xem ràng buộc trực giao có ích thực tế không.

## Hạn chế bổ sung chưa chứng minh

- Backbone cố định có thể mất thông tin phân biệt cho lớp/domain mới.
  Cần domain shift và baseline thích nghi feature để kiểm tra.
- Không exemplar vẫn tốn O(m²). Scaling đo runtime minh họa chi phí,
  chưa đủ kết luận tốc độ tiệm cận từ số lần đo ít.
- C cố định tạo đánh đổi base/new. Quét C trên test là phân tích hậu
  nghiệm; không dùng test để chọn C tốt nhất cho kết quả chính.

## Poster

Đặt L1 và L2 cạnh số đo tương ứng, ghi rõ dữ liệu tổng hợp/ba seed và
phạm vi kết luận. Chỉ gắn số nhóm với W&B URL sau khi sync và xác minh
quyền đọc công khai. Trước đó, poster là bản làm việc chưa đủ điều kiện
nộp. Không dùng smoke accuracy làm bằng chứng tái hiện hay phê bình.
