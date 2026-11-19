# Rà soát Core scope

> Publication update 2026-11-20: see [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md). The team reports submission and has authorized publishing this revision. References below to an unpushed/local-only revision describe the original 2026-11-19 review. Original files and their manifest are archived in [history](history/review-delivery-20261119.zip). The review score is not an official grade.

Nguồn chuẩn: bản yêu cầu học phần được nhóm cung cấp, phần Reproduction trang8–10 của bản dịch; paper Table1/2, Figure4 và SupplementC. Không có các file Markdown riêng `index.md`, `reading.md`, `reproduction.md`, `analysis.md`, `empirics.md` trong working tree. Đã đọc PDF `index.pdf` và bản yêu cầu14 trang chứa các phần tương ứng. Chưa đối chiếu được bản Markdown/Moodle mới hơn, vì chưa có URL/quyền truy cập cho nguồn đó. Hash của tài liệu đã đọc nằm trong `evidence/strict-audit.json`.

| Hạng mục | Bằng chứng | Đánh giá nghiêm ngặt |
|---|---|---|
| E1: headline CIFAR B50/K5 | ACIL và DS-AL, ba backbone/class order/projection riêng, ghép cặp trong seed, finished/public | PASS cho đối sánh phần CIFAR ResNet32 của Table1; PARTIAL về khớp implementation gốc. Không gọi exact reproduction |
| K25/50 | Cùng checkpoint/cache/projection seed0, 26/51 pha đánh giá, đặt cạnh Table1 | PASS cho đối sánh K trên một seed; không thay cho ImageNet500 pha hoặc ba seed K |
| E2: DAC/PLC CIFAR | Ba seed ACIL/DAC/DS-AL, matched cache và protocol | PASS như ablation chuyển dataset; không được tính mặc nhiên là tái hiện nguyên Table2 |
| E3: buffer512/1024/2048/8192 | Cùng cache/solver/K5, accuracy và fit thực đo | PASS cho phân tích nhóm thiết kế. PARTIAL về tổng quát do một seed, projection không lồng nhau, runtime không kiểm soát tải máy |
| E4 mới: Tanh/C sensitivity | C0…1, ba final classifier đã lưu; xác nhận C0/C0,6, ba run thật | PASS cho nhánh Tanh/CIFAR final accuracy của Figure4. PARTIAL cho toàn thí nghiệm Figure4 vì thiếu các activation/dataset khác và A-bar |
| Full scope | Chưa có ImageNet100/Full, activation grid đầy đủ, 500pha | FAIL nếu nhận Full; nhóm không chọn Full |

Core cần ít nhất hai thí nghiệm quan trọng gồm headline và một phân tích nhóm. E1 + E4 là lập luận mạnh hơn E1 + adapted E2; khảo sát K củng cố Table1, E3 đáp ứng phần tự thiết kế. Tuy vậy, các hàng trong cùng Table1 có thể bị giảng viên xem là một thí nghiệm, và nhánh Tanh của Figure4 có thể bị xem là chưa đủ rộng. Vì thế **PARTIAL về khả năng khẳng định chắc chắn đã đủ Core**, không tự xác nhận giảng viên đã chấp thuận.

Lựa chọn hiệu quả nhất đã làm ngay: E4 dùng C chỉ tại inference, không cần huấn luyện hoặc fit lại; giữ C0,6 của benchmark, không chọn điểm test tốt nhất để thay kết quả. Mean có dạng tăng rồi giảm tương tự mô tả paper, nhưng vị trí đỉnh nhóm0,7/0,8 khác paper quanh0,6. Không số hóa hay tự tạo tọa độ paper không được công bố.

Lựa chọn tiếp theo nếu cần tăng mức bao phủ: activation × C trên cache cũ. Phải refit từng activation vì X_C thay đổi. Nên ưu tiên Tanh/Mish/Hardswish và giữ main stream/checkpoint/projection cố định. Đây là thí nghiệm nhiều phút, cần nhóm đồng ý trước. Kế hoạch và tiêu chí ở [BLOCKED_AND_FOLLOWUP.md](BLOCKED_AND_FOLLOWUP.md). ImageNet-Full không phải phương án phù hợp nhất trên máy16GB trước hạn nộp.
