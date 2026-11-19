# Kiểm tra cuối: DS-AL Milestone 2 + Lab 1, v2

Ngày thực hiện: 19/11/2026. Phiên bản mới tách riêng; giữ nguyên PPTX/PDF, nguồn tác giả slide và bằng chứng của v1. Không thay mã phương pháp/pipeline, không chạy thêm benchmark hoặc tạo/sync/sửa run W&B.

## Các vấn đề đã xử lý

| Hạng mục | Kết quả v2 |
|---|---|
| Slide 1 | Đầy đủ Lâm Hoàng Vũ – 23122056; Nguyễn Bá Nam – 23122043; Chung Tín Đạt – 23122024. Tên và MSSV căn theo ba hàng cân đối |
| Slide 22 | E2 ghi rõ chuyển ImageNet-Full/C=1,4 sang CIFAR-100/C=0,6; không tái hiện nguyên Table 2. Notes không khẳng định đã được giảng viên chấp nhận |
| Slide 25 | Thay thông báo repo/checklist công việc bằng thiết kế đối sánh: cùng biểu diễn, protocol, solver; chỉ rõ yếu tố thay đổi ở E2/K/buffer |
| Slide 26–33 | Giữ nguyên số đo đã xác minh. Paper mean±std vẫn gắn nhãn kết quả tác giả; kết quả benchmark nhóm là seed 0. Không thêm std/error bar giả |
| Slide 29 | Ghi E2 là ablation chuyển dataset và seed 0 ngay trên slide; giữ đầy đủ bảng ACIL/DAC/PLC và các mức chênh lệch |
| Slide 30 | ACIL nét đứt/marker vuông; DAC nét gạch-chấm/marker tam giác; DS-AL nét liền/marker tròn, ba màu riêng. Phóng trục Y 50–80% có thông báo rõ. Bổ sung bảng pha cuối, giữ các chênh lệch base/novel |
| Slide 33 | Hai biểu đồ native đặt cạnh nhau cho accuracy (%) và fit (s), hai trục cột bắt đầu từ 0. Bảng giữ đủ bốn buffer và timing; nhấn mạnh +5,41 pp cùng thời gian fit ×96,0 khi tăng m từ 512 lên 8192 |
| Slide 37 | Ghi rõ controlled synthetic input, cùng dữ liệu/nhãn/projection, đổi batch của mã tham chiếu 20→4. Phân biệt sai khác max-absolute của main/compensation/score. Không quy kết mã tác giả sai nói chung hoặc đã giải thích được gap CIFAR |
| Slide 40 | Thay checklist trước nộp bằng tổng hợp học thuật: bảo đảm main ridge, quan sát K và tác dụng DAC/PLC theo protocol |
| Citations | Tăng lên 12 pt, giữ số IEEE nhất quán tại chân slide, nguồn đầy đủ và URL trong notes. Không có trang References riêng |
| W&B | Thay URL dài bằng nhãn có hyperlink 14 pt. Full URL vẫn có trong notes và bảng mapping. Kiểm tra đích link trong cả PPTX lẫn PDF; 11/11 run dùng trong deck đọc công khai được qua GraphQL không xác thực |
| Các trang còn lại | Rà soát toàn bộ notes và bố cục. Điều chỉnh tick epoch ở slide 9 để PDF dễ đọc; dọn câu mô tả thao tác rà soát trên slide 24 |

## Xác nhận chất lượng

- [x] 40 slide, bao gồm phụ lục, đúng giới hạn 20–40.
- [x] 40 slide có speaker notes; notes dài nhất 278 từ, tính cả trích dẫn và URL.
- [x] 9 biểu đồ native có workbook nhúng; bảng, sơ đồ và chữ chỉnh sửa được trong phần mềm PowerPoint có chức năng chỉnh sửa hoạt động.
- [x] Các series accuracy cũ giữ nguyên toàn bộ giá trị. Series thời gian mới lấy đúng `fit_seconds` từ log đã có, không tạo thí nghiệm mới.
- [x] Bảng paper, ablation, gap và khảo sát K giữ nguyên số; kiểm tra lại bảng buffer và đối chiếu mã tác giả.
- [x] Công thức học thuật được đối chiếu với v1; không đổi objective, padding, gain, DAC/PLC hoặc điều kiện theorem vì thiết kế.
- [x] Render đầy đủ 40 trang và kiểm tra từng ảnh ở 1600×900. Đã sửa hai bảng chạm hàng link và nhãn epoch quá dày; các trang sửa được render/xem lại.
- [x] Kiểm tra package OOXML không có finding, chữ PDF nằm trong trang, không có đối tượng ghi nhận vượt canvas.
- [x] 104 tệp v1/snapshot đã ghi nhận trước đợt này giữ nguyên SHA-256; 58 file thực nghiệm/checkpoint trong manifest bảo vệ giữ nguyên.
- [x] Không thay quyền GitHub, không thay môi trường `.venv`/PyTorch/CUDA, không sửa W&B.

Kết quả máy đọc, hash PPTX/PDF và biên bản xem ảnh nằm tại `qa/v2/`. Kiểm tra hình học không thay thế kiểm tra trực quan.

## Những việc nhóm cần làm sau

1. **Chạy thêm seed 1 và 2 khi nhóm sẵn sàng.** Đợt này không chạy. Giữ protocol/siêu tham số tương đương và backbone riêng cho mỗi seed; giữ seed 0 nguyên trạng. Sau khi run hoàn tất, xác minh config/history/summary và URL thật rồi mới tính mean/std. Ghi số seed, cách tính std (ví dụ sample std, ddof=1), đơn vị %, pp và timing. Ba seed của thí nghiệm synthetic không thay cho ba seed CIFAR.
2. **Xác nhận phạm vi E2 với giảng viên.** Chưa có thông tin chấp nhận ablation chuyển ImageNet-Full sang CIFAR. Nếu yêu cầu đúng Table 2, cần đánh giá tài nguyên/thời gian cho protocol đó trước; không gọi kết quả CIFAR là bản tái hiện nguyên Table 2.
3. **Repository công khai: hiện đã đạt.** GitHub connector xác nhận `vtpy23/IntroductionToMachineLearningGroup3` có visibility `public` trong đợt này. Không cần đổi quyền lúc này và không có thao tác đổi quyền. Trước nộp, thử link ở cửa sổ không đăng nhập và bảo đảm bản v2 cùng nguồn tương ứng có trên commit được nộp. Các file v2 của đợt này được lưu riêng trong workspace, không tự đẩy commit mới trong nhiệm vụ chỉnh sửa này.
4. **Kiểm tra Office trên máy trình chiếu.** PowerPoint trên máy hiện tại báo tài khoản trường không còn hoạt động và sản phẩm chưa cấp phép, nên COM không mở được cả bản sao v1 lẫn v2. PDF v2 được xuất từ chính PPTX bằng LibreOffice Portable 26.2.4, rồi render bằng Poppler để kiểm tra. Chưa thể xác nhận một lượt render v2 bằng PowerPoint native. Khi tài khoản Office hoạt động hoặc dùng máy khác, mở thử bản v2, kiểm tra font/chart/hyperlink và xuất lại PDF nếu có khác biệt. Không cần sửa môi trường thực nghiệm để xử lý việc này.
5. **Chuẩn bị nộp Moodle.** Kiểm tra hạn nộp và ID chính thức. Nếu yêu cầu `03.pptx`, tạo bản sao của phiên bản đã chốt trong một thư mục nộp mới, không ghi đè `03.pptx` cũ. PPTX và URL repo là các mục nộp riêng theo hướng dẫn. Các thành viên cần giải thích được toàn bộ phương pháp, protocol và giới hạn.

## Nguồn chỉnh sửa và cách cập nhật nhiều seed

Chỉ thêm các nguồn trình bày v2; không đổi nguồn triển khai DS-AL:

| Tệp | Vai trò |
|---|---|
| `prepare_v2.py` | Copy học thuật, thông tin nhóm, notes và metadata v2; đọc evidence seed 0 đã khóa |
| `slide_content_v2.json`, `SLIDE_CONTENT_v2.md` | Nội dung và nguồn theo từng slide, dễ review |
| `build_slides_v2.mjs` | Bố cục, bảng/chart/diagram native; không ghi đè v1 |
| `render_v2_local.ps1` | Xuất PDF và ảnh bằng renderer portable cục bộ |
| `render_v2.ps1` | Phương án xuất bằng PowerPoint COM khi Office đã hoạt động |
| `validate_v2.py` | Kiểm tra notes, số đo, native charts, links, bảo toàn v1 và log |

Khi có thêm seed: tạo snapshot evidence phiên bản mới, không sửa `assets/verified_evidence.json` của v1. Gộp theo **cùng tên biến thể và cùng metric**, giữ từng run/seed trong mapping. Chuyển cách biểu diễn từ “seed 0” sang “mean ± std, n=3” chỉ khi đủ ba run hợp lệ. Cập nhật bảng/chart và đồng thời các câu phân tích ở slide 27–35/40, notes, gap với paper và timing; không chỉ thay một ô. Builder tập trung số đo tại `R[name].summary`/`R[name].phases`, nên các bảng và series vẫn chỉnh sửa/tái tạo được. Nhãn ngắn không thay đổi URL thật trong notes/mapping.

Để tái tạo snapshot v2 hiện tại từ repo root:

```powershell
.\.venv-cpu\Scripts\python.exe -X utf8 reports/milestone2_final/prepare_v2.py
$env:DSAL_V2_OUTPUT = (Join-Path (Get-Location) 'reports/milestone2_final/.build/v2/candidate.pptx')
node reports/milestone2_final/build_slides_v2.mjs
Remove-Item Env:DSAL_V2_OUTPUT
powershell -NoProfile -ExecutionPolicy Bypass -File reports/milestone2_final/render_v2_local.ps1
pdftotext -bbox reports/milestone2_final/.build/v2/candidate.pdf reports/milestone2_final/.build/v2/pdf-bounds.html
.\.venv-cpu\Scripts\python.exe -X utf8 reports/milestone2_final/validate_v2.py
```

Không chạy lại `prepare_v2.py` sau khi chỉ sửa JSON trực tiếp nếu chưa chuyển thay đổi đó về nguồn Python. Sau khi export lại, xem đủ 40 trang rồi mới thay bản v2 cuối trong cùng đợt làm việc hoặc tạo v3 cho lần cập nhật tiếp theo.

Renderer portable được lấy từ trang LibreOffice chính thức, hash SHA-256 `4bde93374aef4409243505b20d16561a4628ac7591457dd01fc6e1ccf571ba65`, chữ ký Authenticode hợp lệ của RARE IDEAS, LLC. Bản portable chỉ được giải nén dưới `artifacts/render-tools/`, không cài vào môi trường Python hay đưa vào Git. Tham khảo [trang bản portable chính thức](https://hr.libreoffice.org/download/portable-versions/).
