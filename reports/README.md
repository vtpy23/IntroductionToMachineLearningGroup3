# Xuất và cập nhật báo cáo

## Bản hiện hành: StrictReview

[Bàn giao cho nhóm](../TEAM_HANDOFF.md) ghi trạng thái nộp theo xác nhận ngày 20/11/2026 và liên kết đúng bản đã chuẩn bị. Bộ mới có 40 slide, 10 chart / 22 bảng native; xem [PPTX](milestone2_final/DSAL_Milestone2_Lab1_3Seeds_StrictReview_Final.pptx), [PDF](milestone2_final/DSAL_Milestone2_Lab1_3Seeds_StrictReview_Final.pdf), [03.pptx](milestone2_final/submission_strict_review/03.pptx) và [source/báo cáo](strict_review/README.md). Thí nghiệm gốc giữ nguyên; sensitivity C chỉ suy luận từ classifier đã lưu.

## Bản trước: Milestone 2 + Lab 1, ba seed, 40 slide

- [PPTX nộp theo ID 03](milestone2_final/submission_3seeds/03.pptx) và [bản tên đầy đủ](milestone2_final/DSAL_Milestone2_Lab1_3Seeds_Final.pptx).
- [PDF xem trước](milestone2_final/DSAL_Milestone2_Lab1_3Seeds_Final.pdf).
- [Nguồn PptxGenJS](milestone2_final/build_three_seeds.mjs), [nội dung/notes](milestone2_final/slide_content_three_seeds.json), [kiểm tra và tái tạo](milestone2_final/FINAL_VALIDATION_REPORT.md).
- [Thống kê ba seed](milestone2_final/THREE_SEEDS_RESULTS.md), [bằng chứng từng seed](../experiments/multiseed/20261119/README.md).

Đây là bản dùng số đo thật seed 0/1/2, mean ± SD mẫu cho ba phương pháp chính. K và buffer giữ seed 0. Các bản Final/v2/v3 và alias 03.pptx cũ được giữ để truy vết. Việc giảng viên chấp nhận riêng phạm vi E2 chuyển dataset chưa được xác nhận. Nguồn Python/JS, JSON và assets được giữ để cập nhật; file tạm `.build` và `node_modules` không đưa lên Git.

## Bản cũ và poster nháp

Các hướng dẫn dưới đây thuộc bộ 30 slide trước đây. Chúng không thay thế quy trình cập nhật bộ 40 slide trong `milestone2_final/HOW_TO_UPDATE_SLIDES.md`.

- [03.pptx](output/03.pptx): bộ30 slide, chỉnh sửa trực tiếp trong PowerPoint.
- [03.pdf](output/03.pdf): bản xem trước xuất bằng Microsoft PowerPoint.
- [build_slides.mjs](build_slides.mjs): source PptxGenJS giữ lại để cập nhật.
- [SLIDES.md](SLIDES.md): nội dung học thuật và speaker notes.
- [deck_content.json](deck_content.json): đặc tả nội dung mà renderer đọc.
- Poster A2 có bản làm việc riêng, chưa phải bản nộp.

ID03 theo thông tin nhóm cung cấp. Bản hiện tại giữ placeholder
**Chờ kết quả thực nghiệm** ở nơi benchmark chưa hoàn tất. Đúng định dạng
file không đồng nghĩa Lab1 đã hoàn thành; cần kết quả thực đo và W&B công khai.

## Xuất lại

```powershell
npm --prefix reports ci
.venv-cpu/Scripts/python.exe -X utf8 -m scripts.refresh_reports --group-id 03
```

Nếu cần lấy kết quả mới từ W&B sau khi đã đăng nhập và điền entity trong `.env`:

```powershell
.venv-cpu/Scripts/python.exe -X utf8 -m scripts.refresh_reports --group-id 03 --from-wandb
```

Renderer không đổi nội dung học thuật trong SLIDES.md/deck_content.json.
Để giữ chỉnh sửa qua các lần xuất lại, cập nhật nội dung ở `deck_content.json`
và bố cục ở `build_slides.mjs`. Các chỉnh sửa trực tiếp trong PowerPoint
cần được chuyển lại vào nguồn trước lần tái tạo tiếp theo.
Nó đọc kết quả local hoàn tất và file `wandb_results.json` do fetch từ
W&B tạo, loại smoke khỏi bảng so paper, giữ placeholder nếu thiếu số đo.
Không tạo kết quả ngẫu nhiên hoặc nội suy vào ô chưa có dữ liệu.

Bảng/biểu đồ/sơ đồ dùng object native. Chữ, số liệu và nhãn sửa được.
`render_reports.ps1` mở chính PPTX trong PowerPoint, xuất PDF/PNG và đo
text bounds. Script không đóng các presentation có sẵn của người dùng.
`validate_reports.py` kiểm tra số slide, notes, dung lượng, cấu trúc native
và số trang PDF. PNG/diagnostics nằm ở `.build/`, không phải file nộp.

PptxGenJS4.0.1 khai báo thừa slideMaster trong content types cho file nhiều
slide. Builder loại đúng những khai báo trỏ tới part không tồn tại; không
sửa mã thư viện hay nội dung slide. Native table dùng `valign=middle`
để có giá trị DrawingML hợp lệ. File được kiểm tra bằng PowerPoint thực tế.
