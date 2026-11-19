# Kiểm tra bố cục bản v3

## Sản phẩm

- `DSAL_Milestone2_Lab1_Final_v3.pptx`
- `DSAL_Milestone2_Lab1_Final_v3.pdf`

Bản v2 được giữ nguyên. Bản v3 vẫn có 40 slide.

## Các chỉnh sửa

Chiều cao hàng khai báo trong một số bảng nhỏ hơn không gian cần thiết cho chữ và lề ô. Khi PowerPoint mở bảng, hàng có thể giãn xuống vùng liên kết hoặc chú thích. Bản sửa đồng bộ chiều cao khung bảng với tổng chiều cao hàng, giảm lề trên/dưới trong ô xuống 0,035 inch, giữ nguyên cỡ chữ và toàn bộ nội dung.

| Slide | Điều chỉnh | Kết quả trong PowerPoint |
| --- | --- | --- |
| 25 | Bảng bắt đầu tại 4,22 inch, mỗi hàng cao 0,43 inch; chuyển vùng W&B xuống dưới bảng | Đáy bảng 5,94 inch, cách nhãn W&B 0,38 inch |
| 33 | Bảng bắt đầu tại 4,80 inch, mỗi hàng cao 0,40 inch; dành vùng riêng cho hyperlink | Đáy bảng 6,00 inch, cách nhãn W&B 0,32 inch; hàng Fit (s) và tất cả giá trị hiển thị đủ |
| 30 | Đồng bộ hàng và khung bảng, mỗi hàng cao 0,40 inch | Giữ khoảng cách với phần diễn giải phía dưới |
| 32 | Đồng bộ hàng và khung bảng, mỗi hàng cao 0,425 inch | Giữ khoảng cách với phần diễn giải và W&B |
| 36 | Tăng chiều cao hàng lên 0,52 inch, giảm lề ô | Bảng cách vùng trích dẫn 0,41 inch |
| 9 | Tắt tự ngắt dòng nhãn epoch trên trục hoành | Nhãn epoch nằm ngang; không thay đổi chuỗi nhãn, dữ liệu hay workbook |

Không thay đổi bố cục biểu đồ ở slide 33 vì hai biểu đồ đã có đủ khoảng cách với bảng sau khi sửa chiều cao hàng.

## Kiểm tra

- Mở PPTX bằng Microsoft PowerPoint, xuất PDF và render lại đủ 40 slide ở 1600 × 900; kiểm tra trực quan từng slide.
- Kiểm tra thêm hình render từ PDF của slide 25 và 33. Không còn chồng lấn tại hai vị trí được báo.
- Kiểm tra 730 khung chữ/ô bảng bằng kích thước chữ thực tế của PowerPoint: không có trường hợp vượt chiều cao khả dụng theo phép đo này.
- Kiểm tra 20 bảng bằng chiều cao hàng thực tế: tất cả đều cách vùng W&B hoặc trích dẫn phía dưới.
- PDF có 40 trang; 190 hyperlink trên các trang đã được đối chiếu với đích liên kết trong PPTX.
- Cả 40 phần speaker notes giữ nguyên từng byte, tối đa 278 từ/slide. Toàn bộ văn bản slide, bao gồm công thức và số liệu trong bảng, giữ nguyên so với v2.
- Cả 94 phần quan hệ trong gói PPTX giữ nguyên từng byte, bảo toàn đích hyperlink. Dữ liệu của 9 biểu đồ và cả 9 workbook nhúng giữ nguyên.
- Chỉ 6 phần XML thay đổi: bố cục tại slide 25, 30, 32, 33, 36 và thuộc tính ngắt dòng của trục biểu đồ trên slide 9. Các thuộc tính khác được đối chiếu tự động.
- Kiểm tra cấu trúc gói PPTX: không có lỗi được phát hiện.
- Hash của PPTX/PDF v2, snapshot bằng chứng và 58 file kết quả/checkpoint được bảo vệ không thay đổi.

Không chạy thí nghiệm, không thay đổi seed 0 và không cập nhật W&B trong đợt sửa này. Các phép kiểm tra hình học hỗ trợ rà soát; kết luận bố cục còn dựa trên việc xem từng trang render.

## Tái tạo bản sửa

Chạy từ thư mục gốc repository:

```powershell
.venv-cpu/Scripts/python.exe -X utf8 reports/milestone2_final/repair_layout_v3.py
powershell -NoProfile -ExecutionPolicy Bypass -File reports/milestone2_final/render_v3_powerpoint.ps1
pdftotext -bbox reports/milestone2_final/.build/v3/candidate.pdf reports/milestone2_final/.build/v3/pdf-bounds.html
.venv-cpu/Scripts/python.exe -X utf8 reports/milestone2_final/validate_layout_v3.py
```

Script sửa trực tiếp bản sao OOXML của v2 để bảo toàn nội dung, notes, hyperlink và workbook. File trung gian nằm trong `.build/v3/`; bằng chứng kiểm tra của phiên bản giao nằm trong `qa/v3/`. Khi nội dung nghiên cứu thay đổi sau này, cần tạo bản đầu vào mới rồi rà soát lại bố cục; đợt sửa này chỉ áp dụng cho bản v2 hiện tại.
