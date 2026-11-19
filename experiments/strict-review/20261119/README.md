# Phân tích classifier đã lưu, 19/11/2026

Chỉ suy luận trên final heads, không fit lại hoặc thay kết quả seed0/1/2. Ba run sensitivity có config, parent run IDs, hash artifact gốc, history11 điểm, và counts corrected/harmed. C0 khớp ACIL; C0,6 khớp DS-AL cũ ở accuracy tổng/base/novel. C0,6 vẫn là benchmark đã khai báo trước. Không có A-bar mới cho các C khác.

Nguồn chạy ở `source_snapshot/` giữ byte của hai file mới dùng tạo kết quả; provenance đầy đủ trong từng config. Thay đổi sau đó ở reporting/docs không thay thí nghiệm đã đo. Snapshot thí nghiệm train/fit gốc ở `experiments/multiseed/20261119/`. Không chứa dữ liệu ảnh, feature cache, checkpoint hay credentials.

Đợt rà soát này chưa push GitHub theo yêu cầu người dùng. Xem `reports/strict_review/` cho audit, mapping và giới hạn.
