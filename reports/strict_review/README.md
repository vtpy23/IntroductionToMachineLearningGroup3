# Bàn giao StrictReview, 19/11/2026

Cập nhật công bố 20/11/2026: người dùng xác nhận đã nộp Milestone 2 + Lab 1 và cho phép đưa bản mới lên GitHub để cả nhóm theo dõi. Xem [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md) cho trạng thái hiện hành. Chưa kiểm tra biên nhận/file trên Moodle. Các báo cáo ngày 19/11 và receipt cũ là snapshot tại thời điểm review; nguyên bản được giữ trong [archive lịch sử](history/review-delivery-20261119.zip), không sửa kết quả hay tự đổi điểm ước lượng.

Phiên bản này giữ kết quả ba seed và thiết kế hiện có, bổ sung kiểm chứng cùng phân tích nhẹ từ classifier đã lưu. Không chạy lại backbone hoặc refit thí nghiệm lịch sử trong đợt công bố.

- [PowerPoint mới](../milestone2_final/DSAL_Milestone2_Lab1_3Seeds_StrictReview_Final.pptx)
- [PDF mới](../milestone2_final/DSAL_Milestone2_Lab1_3Seeds_StrictReview_Final.pdf)
- [Bản tên 03.pptx cho Moodle](../milestone2_final/submission_strict_review/03.pptx)
- [Đánh giá nghiêm ngặt và rủi ro điểm](FINAL_STRICT_REVIEW.md)
- [Những vấn đề đã xử lý](CHANGES.md)
- [Yêu cầu giảng viên → slide](REQUIREMENTS_TO_SLIDES.md)
- [Kiểm chứng số liệu](NUMERICAL_VERIFICATION.md)
- [Thí nghiệm → script → config → run](EXPERIMENT_MAPPING.md)
- [Đánh giá Core scope](CORE_SCOPE_REVIEW.md)
- [Bảng audit protocol và reproduction gap](GAP_PROTOCOL_AUDIT.md)
- [Vấn đề còn mở / thí nghiệm đề xuất](BLOCKED_AND_FOLLOWUP.md)
- [Hướng dẫn chạy và cập nhật slide](RUNBOOK.md)
- [Bằng chứng kỹ thuật](evidence/)

Nguồn mới: `prepare_strict_content.py`, `layout_overrides.mjs`, `merge_strict.py`, `validate_and_finalize.py`; PptxGenJS entrypoint tại `../milestone2_final/build_strict_review.mjs`. Bản trước `3Seeds_Final.pptx` và các file thực nghiệm vẫn nguyên vẹn. Chart/workbook của bản trước giữ nguyên byte; chart sensitivity mới dùng dữ liệu đo thật, kèm SD mẫu và workbook có thể chỉnh sửa.

Nhóm tiếp tục theo dõi phản hồi chấm bài và chuẩn bị poster/workshop. Không dùng đánh giá ước lượng như điểm chính thức hoặc xác nhận hoàn tất poster cuối. Phạm vi Core do nhóm biện minh và giảng viên đánh giá; tài liệu không nêu một thủ tục duyệt riêng bắt buộc cho Core/E2, cũng không nêu rõ lệnh cấm Forge. Chi tiết tại trang bàn giao nhóm.
