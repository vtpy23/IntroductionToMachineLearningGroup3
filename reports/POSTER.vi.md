# DS-AL: giới hạn của hai diễn giải lý thuyết

BẢN LÀM VIỆC: cần đồng bộ và xác minh W&B công khai trước khi nộp

Kiểm chứng cơ chế trên đặc trưng tổng hợp cố định, ba seed độc lập

## Điểm mạnh

- Head chính đạt nghiệm ridge học gộp khi feature cố định
- Duy trì thống kê bậc hai thay cho exemplar
- DAC bổ sung mô hình học residual, có hỗ trợ thực nghiệm trong paper

## L1. Nhánh bù phụ thuộc cách chia pha

Residual phụ thuộc W_M ở thời điểm kết thúc mỗi pha. Đổi phân hoạch pha làm đổi nhãn bù lịch sử. Theorem1 của nhánh chính chưa bảo đảm W_C bất biến.

Thiết kế: Giữ dữ liệu, projection, gamma0.1, C0.6 và float64. Chỉ thay số pha mới1/2/5. Mười lớp, base5 lớp,40 mẫu/lớp,12 feature, buffer64. Dữ liệu kiểm tra độc lập.

Cùng dữ liệu cuối chưa bảo đảm cùng W_C hoặc cùng scores. Accuracy chỉ đổi nhỏ ở phép thử này, chưa chứng minh suy giảm lớn trên benchmark ảnh.

F1. Duy trì moment chéo để tính lại residual theo head hiện tại, rồi phân tích objective và PLC riêng.

## L2. Residual ridge không trực giao chính xác

Điều kiện tối ưu là XᵀE=gamma W. Với gamma>0, E nói chung không thuộc trực giao không gian cột của X. Diễn giải null-space cần điều kiện và không gian rõ ràng.

Thiết kế: Giữ dữ liệu/embedding. Quét gamma từ1e-4 đến100. Đo ||XᵀE|| và ||XᵀE−gamma W|| trên ba seed.

Normal equation khớp ở sai số số học trong khi XᵀE khác0. Đây là giới hạn của lý giải hình học, không phải bác bỏ nghiệm ridge hoặc hiệu quả DAC.

F2. Phát biểu bù trực giao chính xác hoặc residual regression có điều chuẩn, rồi đối sánh accuracy và chi phí.

## Nguồn

[1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.
[2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning.