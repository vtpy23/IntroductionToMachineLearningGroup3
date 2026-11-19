# FINAL STRICT REVIEW

> Publication update 2026-11-20: see [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md). The team reports submission and has authorized publishing this revision. References below to an unpushed/local-only revision describe the original 2026-11-19 review. Original files and their manifest are archived in [history](history/review-delivery-20261119.zip). The review score is not an official grade.

## Kết luận chấm nghiêm

**Ước lượng cho riêng bộ slide Milestone 2 + Lab 1: 8,4/10. Chưa có căn cứ cam kết 9/10.** Đây là thang phân tích do người rà soát đề xuất, không phải rubric con hoặc điểm chính thức của giảng viên. Văn bản học phần quy định slide 45%, poster 50%, discipline 5%, chưa cho thang điểm chi tiết như bảng dưới. Không dùng 8,4 để nhận đã hoàn thành hoặc dự báo điểm toàn đồ án.

| Tiêu chí rà soát | Điểm ước lượng | Căn cứ |
|---|---:|---|
| Đọc hiểu và phương pháp |24/25 | Bài toán hình thức, ridge/C-RLS/proof/PLC, giới hạn Theorem 1, normal equations của residual, tiền nhiệm và complexity |
| Bao phủ và độ trung thành tái hiện |18/25 | Headline CIFAR ba seed, K seed 0, sensitivity Tanh/C, triển khai độc lập; thiếu toàn bộ activation/ImageNet và controls chẩn đoán gap |
| Phân tích có bằng chứng |17/20 | Mean/SD, paired gain, base/novel, prediction counts và đối chiếu code/config; chưa tách được tác động từng giả thuyết |
| Tái lập và truy vết |11/15 | 24 run đọc công khai đầy đủ, raw configs/hashes; môi trường sạch chưa xác minh, host Forge cần xác nhận, additions chưa push |
| Artifact và thiết kế |14/15 | 40 slide đã render và đọc từng trang, notes, native charts/tables, IEEE; một số bảng kỹ thuật vẫn cần đọc notes |
| Tổng |84/100 | Không tính điều chưa chứng minh như đã hoàn tất |

Không nhận con số 6,8 cũ là điểm chính thức hoặc dùng chênh điểm đó làm bằng chứng. Điểm 8,4 cũng là phán đoán có giới hạn. Nếu giảng viên xem nhánh Tanh của Figure 4 chưa đủ quan trọng để tính thí nghiệm thứ hai, phần Core có thể bị trừ nhiều hơn ước lượng này.

## Phân loại bằng chứng

| Hạng mục | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| E1: ACIL/DS-AL ở phần CIFAR ResNet-32 của Table 1 | PASS | Ba seed độc lập; các phương pháp ghép cặp trong seed; logs/W&B khớp |
| Tái hiện nguyên bản Table 2 ImageNet-Full | FAIL | Chưa thực hiện. E2 là adapted CIFAR và slide đã nói rõ |
| Hai thí nghiệm Core quan trọng | PARTIAL | E1 + E4 Tanh/C cùng khảo sát K có cơ sở, nhưng chưa có xác nhận mức bao phủ subset Figure 4 |
| Phân tích buffer/time do nhóm thiết kế | PASS | Số đo thật, nêu rõ một seed, projection không lồng nhau và tải CPU chưa được kiểm soát |
| Mean ± sample SD | PASS | Tách mean qua pha và qua seed, ddof=1, không tạo SD khi thiếu seed |
| Kết luận ý nghĩa thống kê | UNVERIFIED | Chưa kiểm định; slide không khẳng định significance |
| Nguyên nhân reproduction gap | PARTIAL | Đã xác định khác biệt cụ thể; chưa có can thiệp chứng minh số pp do từng yếu tố |
| Tuyên bố DAC luôn cải thiện | FAIL nếu đưa ra | Dữ liệu hiện tại không hỗ trợ; slide không còn diễn giải như vậy |
| Giải thích PLC qua base/novel | PASS | So DAC: base +2,29 pp, novel −1,35 pp; counts khớp gain tổng |
| Số paper, biểu đồ và notes | PASS theo audit | Table 1/Supplement đã đọc; 9 chart cũ bảo toàn, chart mới chỉ dùng 33 điểm đo thật |
| W&B public data | PASS kỹ thuật | Anonymous đọc config/summary/history của 24 run, tất cả finished |
| Forge được chấp nhận thay wandb.ai | UNVERIFIED | Chưa có xác nhận ngoài bằng chứng public access |
| GitHub public | PASS | Connector xác nhận visibility public; không đổi quyền |
| Revision mới đã public | FAIL tại bàn giao | Tuân thủ yêu cầu không push; BLOCKED trước nộp đến khi nhóm cho phép công bố |
| Môi trường sạch chạy từ đầu | UNVERIFIED | Venv kế thừa packages hệ thống; pip check còn 7 conflicts ngoài dự án |
| Source và core tests | PASS có giới hạn | 21 pytest đạt và audit artifacts; không phải chứng nhận không có mọi bug hoặc không sao chép tuyệt đối |
| Resume | PASS trong kiểm thử cùng backend | Không chứng minh CUDA→CPU của seed 0 tương đương từng bit |
| Nộp Moodle, hạn và chấp nhận phạm vi | UNVERIFIED | Nhóm cần kiểm tra/thực hiện qua kênh chính thức |
| Poster cuối và workshop | PARTIAL | Poster vẫn là draft; không dùng bộ slide này nhận hoàn tất phần poster |

## Rủi ro bị trừ điểm còn lại

1. **Core có thể chưa đủ rộng.** Hai thí nghiệm quan trọng không được định nghĩa bằng số hàng trong bảng. E4 chỉ là Tanh/CIFAR; E2 không phải Table 2. Nếu cần, activation sweep là phương án củng cố phù hợp hơn việc đổi nhãn.
2. **Gap chưa được giải thích nhân quả.** Projection, initialization, class order và residual đều có khác biệt được xác minh với checkout, nhưng chưa biết mỗi yếu tố đóng góp bao nhiêu. Gain gần paper không chứng minh backbone là nguyên nhân duy nhất.
3. **Tracking host.** Public data trên Forge được xác minh mạnh, nhưng văn bản học phần nêu wandb.ai. Cần xác nhận cách áp dụng quy định, không biến test API thành quyết định của giảng viên.
4. **Public traceability.** Additions hiện chỉ ở máy. Nếu nộp trước khi công bố source/evidence mới, những nội dung mới sẽ chưa đáp ứng yêu cầu truy về GitHub.
5. **Môi trường sạch.** Import/test đang hoạt động không thay cho cài đặt và chạy từ môi trường độc lập. Không nên giải quyết bằng nâng Torch hoặc gỡ công cụ ngoài phạm vi; đã chuẩn bị config và lệnh cho venv riêng.
6. **Ba seed và backend.** Cỡ mẫu nhỏ, cùng tập ảnh, seed 0 đổi thiết bị. Không dùng SD nhỏ, ba dấu dương hoặc pooled counts để nhận significance/tính tổng quát.
7. **Một seed cho K/buffer.** Không có SD nhiều seed hoặc kiểm soát tải CPU; projection khác chiều không lồng nhau. Hai biểu đồ buffer không chứng minh scaling trên mọi máy.
8. **Chỉ có final heads cho C-sweep.** Không có A-bar hoặc residual lịch sử ở các C khác. Không được tạo chúng bằng giả định từ classifier cuối.
9. **Nhóm phải hiểu và bảo vệ công việc.** AI hỗ trợ không thay trách nhiệm từng thành viên; workshop có thể kiểm tra bất kỳ phần nào của mã, công thức và kết quả.

Mức 9/10 cần được hỗ trợ bằng bằng chứng và đánh giá phạm vi. Các phần có thể xử lý ngay đã được sửa; phần cần tài nguyên hoặc quyết định ngoài dữ liệu được ghi tại [BLOCKED_AND_FOLLOWUP.md](BLOCKED_AND_FOLLOWUP.md). Đây là điểm dừng trung thực của đợt rà soát, không phải tuyên bố đồ án đã hoàn tất toàn bộ.
