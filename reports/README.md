# Xuất và cập nhật báo cáo

## Bản hiện tại: Milestone 2 + Lab 1, 40 slide

- [PPTX nộp theo ID 03](milestone2_final/03.pptx) và [bản tên đầy đủ](milestone2_final/DSAL_Milestone2_Lab1_Final.pptx).
- [PDF xem trước](milestone2_final/DSAL_Milestone2_Lab1_Final.pdf).
- [Nguồn PptxGenJS](milestone2_final/build_slides.mjs), [nội dung/notes](milestone2_final/SLIDE_CONTENT.md), [hướng dẫn cập nhật](milestone2_final/HOW_TO_UPDATE_SLIDES.md).
- [Báo cáo rà soát](milestone2_final/SLIDE_REVIEW_REPORT.md), [mapping thí nghiệm](milestone2_final/EXPERIMENT_TRACEABILITY.md), [snapshot log/config công bố](../experiments/evidence/README.md).

Đây là bản mới cập nhật seed 0 đã hoàn tất, không có số benchmark giả. Repo được xác nhận public khi công bố. Benchmark nhiều seed và việc giảng viên chấp nhận ablation chuyển dataset còn mở. Nguồn Python/JS, JSON và assets được giữ để cập nhật; file tạm `.build` và `node_modules` không đưa lên Git.

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
