# Những vấn đề đã xử lý

> Publication update 2026-11-20: see [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md). The team reports submission and has authorized publishing this revision. References below to an unpushed/local-only revision describe the original 2026-11-19 review. Original files and their manifest are archived in [history](history/review-delivery-20261119.zip). The review score is not an official grade.

- Đọc yêu cầu học phần gồm Reading/Reproduction/Analysis/Empirics trong PDF cung cấp, bài chính và SupplementA–C, source nhóm, tests/configs, toàn bộ40slide và notes. Không mặc định bản cũ đúng.
- Xác minh24run finished, đầy đủ config/summary/history qua kết nối anonymous tới Forge. Snapshot audit mới riêng, không ghi đè snapshot thí nghiệm cũ.
- Kiểm tra52file gốc bằng SHA-256 sau phân tích. Không train lại backbone, không fit lại main/comphead, không thay số seed0/1/2/K/buffer.
- Thêm phân tích thực đo C-sensitivity trên ba final classifier; checkpoint/cache/hash đúng, C0khớpACIL và C0,6khớpDS-AL. Ba run mới riêng: i2c96w3y, cu5nowzq, xq49tulq. Giữ benchmark C0,6, không thay bằng Ctest tốt nhất.
- Thêm paired prediction corrections/harm, giải thích base/novel cho DAC/PLC từ artifact thật. Không vẽ train-residual lịch sử chưa được lưu.
- Phân loại Core, không nhận E2CIFAR là Table2ImageNet. Đưa E4Figure4Tanh/C vào lập luận phạm vi, vẫn giữ phần chưa đầy đủ.
- Slide4/5 làm rõ tiền nhiệm, hệ quả thực tế và phần kế thừa ACIL; slide8 phát biểu hình thức CIL; slide17 sửa cách hiểu null space với normal equations đúng cho residual joint; gain phụ lục cũ gộp vào notes13.
- Slide16/20 làm rõ chi phí và so baseline, tách storage lý thuyết/peakRAM/runtime đo. Slide28 thêm gain paper0,48pp so nhóm0,40pp và giới hạn diễn giải.
- Slide31 đặt K25/50 cạnh số paper; slide34 phân loại projection/classorder/init/solver/residual đã xác minh; slide36 là C-sensitivity; slide40 là base/novel.
- Thay câu README “chưa có mean/std” lỗi thời và thêm mapping ba seed/commands; tài liệu môi trường phân biệt haiSDK và backend seed0.
- Phát hiện lỗi mô tả backend trong generator `scripts/core_multiseed_report.py`: trước đây câu “seed0 cũng CPU” bỏ qua19epoch CUDA. Chỉ sửa chuỗi báo cáo; không đổi thuật toán, config train/fit hay dữ liệu đã ghi. Không chạy generator để ghi đè các báo cáo lịch sử.
- Bổ sung6test có ý nghĩa: class remap, local seed, multi-phase chunks cho2solver, C0/main equivalence, weighted accuracy/paired counts và ridge residual geometry. Tổng21test đạt; không che lỗi bằng nới tolerance. Test residual dùng identity float64 để không đưa sai sốfloat32 vào oracle.
- Tăng độ mạnh của test resume hiện có: đổi RNG của tiến trình trước khi resume, xác nhận chỉ epoch còn lại được chạy và checkpoint khác signature bị từ chối. Điều này tránh trường hợp một lần restart deterministic từ đầu cũng vô tình vượt qua phép so trọng số cuối.
- Đọc `pip check/list/pyvenv.cfg`, ghi7conflicts kế thừa ngoài dự án; không gỡ/nâng các package không liên quan. Clean pipeline mới chưa được tự nhận pass.
- Chuẩn bị script/config projection control ở chế độ plan-only, không chạy6refit nặng. Config tái lập sạch mới pin dataset và tách output/checkpoint khỏi lịch sử.
- IEEE được đánh số lại theo lần xuất hiện đầu, nguồn Supplement dẫn đúng file tại commit, sourcecode đối chiếu có citation riêng.
- PPTX mới dùng package3Seeds_Final làm nền. Toàn bộ9chart và workbook cũ giữ byte; thêm chart10 native cùng errorbar/workbook chỉnh sửa được. Notes cập nhật40trang, tên/MSSV giữ đúng. Bản cũ còn nguyên.

Kết quả layout/numeric/hyperlink cuối cùng được ghi bằng số thực trong `evidence/final-validation.json`, kèm biên bản xem từng slide. Không tự push GitHub trong đợt này.
