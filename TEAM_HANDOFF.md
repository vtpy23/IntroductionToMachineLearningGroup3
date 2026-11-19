# Bàn giao cho nhóm — 20/11/2026

**Đến ngày 20/11/2026, nhóm xác nhận đã nộp Milestone 2 + Lab 1.** Chưa truy cập Moodle để kiểm tra biên nhận hoặc đối chiếu byte của file đã tải lên. Kho mã lưu bản StrictReview mới nhất đã chuẩn bị; không tự nhận file này đã được xác minh là đúng file trên Moodle.

## Đọc và tải đúng phiên bản

- [03.pptx đã chuẩn bị theo ID nhóm](reports/milestone2_final/submission_strict_review/03.pptx).
- [PowerPoint tên đầy đủ](reports/milestone2_final/DSAL_Milestone2_Lab1_3Seeds_StrictReview_Final.pptx) và [PDF xem trước](reports/milestone2_final/DSAL_Milestone2_Lab1_3Seeds_StrictReview_Final.pdf).
- [Toàn bộ bàn giao, source tạo slide và các báo cáo](reports/strict_review/README.md).
- [Thí nghiệm → script → config → W&B](reports/strict_review/EXPERIMENT_MAPPING.md).
- [Kết quả và kiểm chứng số liệu](reports/strict_review/NUMERICAL_VERIFICATION.md).
- [Hướng dẫn môi trường, chạy và cập nhật slide](reports/strict_review/RUNBOOK.md).

Bản hiện tại: 40 slide, 10 biểu đồ và 22 bảng native, notes tối đa 382 từ; đã render và xem từng slide. SHA-256 PPTX: `4ea0e45d180bfb7456ca9076423c19bc0891b2a4ed273bcd2c7339986c943876`. Các bản seed 0 và ThreeSeeds trước đó vẫn được giữ làm lịch sử.

## Kết quả cả nhóm cần nắm

Mean ± SD mẫu của seed 0, 1, 2; SD dùng ddof=1. Ā là trung bình qua các pha của mỗi seed rồi mới tổng hợp ba seed, còn A_K là accuracy pha cuối.

| Phương pháp | Ā (%) | A_K (%) |
|---|---:|---:|
| ACIL |65,13 ± 0,57 |56,37 ± 0,32 |
| DAC không PLC |64,95 ± 0,48 |56,30 ± 0,15 |
| DS-AL |65,26 ± 0,49 |56,77 ± 0,19 |

- DS-AL hơn ACIL trung bình **0,40 pp A_K**, tăng ở cả ba seed. PLC so DAC không PLC tăng **0,47 pp**. Đây là thống kê mô tả, chưa khẳng định ý nghĩa thống kê.
- DAC không PLC tăng accuracy lớp novel nhưng mất accuracy lớp base nhiều hơn; không được nói DAC luôn tăng accuracy. PLC lấy lại một phần base accuracy và có đánh đổi ở novel.
- Khảo sát K và buffer vẫn **chỉ seed 0**, không có mean/SD ba seed cho các khảo sát này.
- Phân tích C mới chỉ suy luận từ final classifier đã lưu, không train/refit lại. C=0 khớp ACIL, C=0,6 khớp DS-AL cũ; benchmark vẫn giữ C=0,6. Không dùng điểm test tốt nhất để thay số benchmark.
- Ba run C mới: [seed 0 — i2c96w3y](https://app.forge.coreweave.com/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i2c96w3y), [seed 1 — cu5nowzq](https://app.forge.coreweave.com/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/cu5nowzq), [seed 2 — xq49tulq](https://app.forge.coreweave.com/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/xq49tulq). Config/history và parent run IDs ở [evidence mới](experiments/strict-review/20261119/).

## Phạm vi và giới hạn khi giải thích bài

- Nhóm chọn Core: quy định yêu cầu ít nhất hai thí nghiệm quan trọng, gồm đối sánh chính, cùng phân tích nhóm thiết kế. Nhóm phải biện minh phạm vi; **không có điều khoản bắt buộc xin một lần phê duyệt riêng cho Core/E2** trong tài liệu đã đọc. Giảng viên vẫn đánh giá mức bao phủ thực tế.
- E2 là ablation chuyển sang CIFAR-100, không phải tái hiện nguyên Table 2 trên ImageNet-Full. E4 chỉ là nhánh Tanh/CIFAR của Figure 4. Không nhận Full scope, toàn activation grid hoặc ImageNet 500 pha đã xong.
- Public config/summary/history trên Forge đã được kiểm chứng bằng kết nối không đăng nhập. Tài liệu giới thiệu W&B tại wandb.ai, nhưng **không nêu rõ lệnh cấm host Forge**. Chưa có hướng dẫn riêng về host; không tự kết luận Forge bị cấm hoặc đã được giảng viên xác nhận.
- Theorem 1 bảo đảm main head bằng joint ridge trên embedding cố định, không bảo đảm toàn compensation/accuracy bất biến hoặc joint CNN tương đương.
- Seed 0 có 19 epoch CUDA rồi resume CPU; seed 1/2 dùng CPU. Gap với paper chưa được giải thích bằng can thiệp định lượng. Clean environment chưa được chạy từ đầu; các xung đột package ngoài dự án đã được ghi nhận và chưa sửa bằng thay Torch/CUDA.

## Việc tiếp theo

1. Mỗi thành viên đọc notes và các run thuộc phần mình; cả nhóm cần giải thích được toàn pipeline khi workshop.
2. Chuẩn bị Milestone 3 + Lab 2 và poster A2 dọc. [Theory critique](docs/THEORY_CRITIQUE.md) và [bằng chứng cơ chế](experiments/empirics/) đã có; [poster hiện tại](reports/output/03-poster-draft.pptx) vẫn là bản nháp.
3. **Không cần chạy lại seed 0/1/2.** Projection/activation controls hiện chỉ có script và config đề xuất, chưa chạy refit. Mặc định hai entrypoint `controlled_*_followup` chỉ in kế hoạch; chỉ dùng `--execute` khi nhóm đã thống nhất tài nguyên/phạm vi.
4. Thí nghiệm mới phải có output/checkpoint/run riêng; không ghi đè số đo đã nộp, không trộn các cấu hình vào cùng một kết quả.

Đợt công bố ngày 20/11 được người dùng cho phép để cả nhóm truy cập source/evidence/slide mới. Các báo cáo review và receipt ngày 19/11 là **ảnh chụp trạng thái lúc bàn giao**, kể cả trường “chưa push” và điểm ước lượng 8,4; không phải điểm chính thức hay trạng thái công bố hiện tại. Bản gốc của toàn bộ 40 file trong delivery manifest được giữ tại [archive lịch sử](reports/strict_review/history/review-delivery-20261119.zip).
