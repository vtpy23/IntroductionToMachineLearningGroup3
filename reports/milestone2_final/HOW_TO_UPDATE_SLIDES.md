# Cập nhật bộ slide DS-AL

Bản hiện hành là **DSAL_Milestone2_Lab1_3Seeds_Final.pptx**, dùng kết quả seed 0/1/2 đã xác minh. Xem [báo cáo kiểm định](FINAL_VALIDATION_REPORT.md) cho các lệnh tái tạo, [kết quả ba seed](THREE_SEEDS_RESULTS.md) cho bảng số liệu và [nguồn PptxGenJS](build_three_seeds.mjs). File nộp theo ID nhóm là `submission_3seeds/03.pptx`. Pipeline mới dùng gói v3 làm nền và giữ nguyên các bản lịch sử.

Phần hướng dẫn dưới đây mô tả pipeline seed 0 trước đây; dùng báo cáo kiểm định ở trên để tạo bản ba seed.

Chạy từ repository root bằng PowerShell. Không cần cài/nâng cấp thư viện, không thay PyTorch/CUDA. Các lệnh dưới chỉ đọc W&B và tạo file local; không gọi `wandb.init`, `sync`, upload hay push GitHub.

## Tệp nguồn

| Tệp | Vai trò |
|---|---|
| `audit_evidence.py` | Đọc config/summary/history local, đối chiếu W&B Forge và quyền đọc public |
| `assets/verified_evidence.json` | Snapshot đã xác minh, gồm run URL thực và manifest source SHA-256 |
| `build_content.py` | Copy học thuật, citations IEEE, notes và danh sách run sử dụng |
| `slide_content.json`, `SLIDE_CONTENT.md` | Nội dung được sinh để review; sửa lâu dài ở Python để không bị ghi đè |
| `build_slides.mjs` | Nguồn PptxGenJS: native text/shapes/tables/charts |
| `render.ps1` | PowerPoint COM: xuất PDF/40 PNG, đo text overflow; không đóng presentation người dùng đang mở |
| `validate_final.py` | Kiểm tra package, notes, nguồn số liệu/chart, PDF và file thực nghiệm được bảo toàn |
| `assets/diagrams`, `assets/charts` | PNG preview tự tạo; đối tượng chỉnh sửa nằm trong PPTX và mã JS |

Đầu ra chính `DSAL_Milestone2_Lab1_Final.pptx/.pdf`; `03.pptx` là bản sao byte-identical để đặt tên theo ID nhóm 03 do người dùng cung cấp. Giữ bản cũ hoặc copy cả thư mục sang một revision mới trước khi cập nhật đáng kể.

## 1. Xác minh số đo

```powershell
.\.venv\Scripts\python.exe -X utf8 reports/milestone2_final/audit_evidence.py
```

Dùng môi trường SDK 0.31.0 để đọc; endpoint khóa ở `https://api.forge.coreweave.com`, entity `vu-lam-vnuhcm-university-of-science`, project `intro-ml-group3-dsal`. Credential lấy từ đăng nhập cục bộ, không dán API key vào file hoặc chat. Kiểm tra script không có mutation trước khi mở rộng. Nếu audit lỗi mạng/quyền/khác số đo, dừng công bố bản mới; không sửa local để ép khớp server.

Thêm run chỉ khi run thật đã completed/finished, có config, class order/revision/checkpoint, local history và URL do API trả về. Nếu run đang offline thì việc sync là thao tác riêng, **không thuộc lệnh audit này**; chưa được tự sync trong nhiệm vụ hiện tại.

Không sửa giá trị nhóm trong `paper_table1`: đó là Table 1 của tác giả. Nếu thêm seed1/2, giữ seed0; xác minh mọi seed trước khi tính mean/std và ghi rõ mẫu số, số seed, sample/population std. Không coi seed tổng hợp là seed benchmark CIFAR.

## 2. Sinh lại nội dung và deck

```powershell
.\.venv-cpu\Scripts\python.exe -X utf8 reports/milestone2_final/build_content.py
node reports/milestone2_final/build_slides.mjs
powershell -NoProfile -ExecutionPolicy Bypass -File reports/milestone2_final/render.ps1
.\.venv-cpu\Scripts\python.exe -X utf8 reports/milestone2_final/validate_final.py
```

Node dùng `pptxgenjs` 4.0.1 đã có ở `reports/node_modules`; không cần npm install trong môi trường thực nghiệm. Windows có Microsoft PowerPoint dùng để export PDF nhằm khớp font và chart. Mở PDF kiểm tra đủ trang và xem tất cả ảnh `.build/rendered/slide-01.png` đến `slide-40.png` ở kích thước đọc được.

Build tự tạo alias `03.pptx` giống bản tên đầy đủ. Có thể kiểm tra thêm PDF bằng Poppler hiện có: tạo thư mục `.build/pdf-rendered`, rồi chạy `pdftoppm -png -scale-to 1600 reports/milestone2_final/DSAL_Milestone2_Lab1_Final.pdf reports/milestone2_final/.build/pdf-rendered/page`. Không cần sửa môi trường Python nếu PyMuPDF không import được.

Giá trị bảng/chart chính lấy từ evidence; một số takeaway, annotation và đoạn notes đang viết cho snapshot seed0 (ví dụ +0.31 pp, +0.63 pp, 56.87%). Khi thêm/thay run phải sửa và kiểm lại các câu này trong `build_content.py` và `build_slides.mjs`, không chỉ thay JSON. Validator cũng khóa snapshot số đo hiện tại và phải được cập nhật có review khi đổi protocol; không vô hiệu hóa assertion để bỏ qua mismatch.

## 3. Review và đặt tên nộp

1. Đếm 20–40 trang gồm phụ lục, mỗi notes ≤500 từ kể cả nguồn/URL, không có trang References riêng.
2. Kiểm tra công thức padding/gain/residual/PLC và conditions; giữ nhãn “paper”, “nhóm”, “minh họa” rõ.
3. Kiểm tra tất cả số, chart series, đơn vị %, pp, relative gap và nguồn timing; không thêm error bar nếu chưa có nhiều seed.
4. Xem từng trang, đặc biệt bảng và chân URL: `text-fit.json` không bắt mọi overlap. Citations/URL được cố ý nhỏ hơn body; link vẫn click được và có bản đầy đủ trong notes/mapping.
5. Sau khi render và validate thành công, kiểm hash alias `03.pptx` bằng bản tên đầy đủ. PDF phải được render lại sau mọi thay đổi PPTX.
6. Xem `SLIDE_REVIEW_REPORT.md`: repo đã được xác nhận public và người dùng đã cho phép push cả slide. Việc giảng viên chấp nhận adapted ablation và benchmark nhiều seed còn mở.

Nguồn truy vết: `EXPERIMENT_TRACEABILITY.md` và `README_EXPERIMENT_TABLE.md`. Người chỉnh trực tiếp PPTX cần lưu bản riêng, vì chạy JS sẽ thay thế đầu ra trong thư mục này. Các thư mục `outputs`, `checkpoints`, `.venv`, `.venv-cpu` không bị sửa bởi bước build.

Trong clone mới không có `outputs/`, builder/audit/validator dùng snapshot `experiments/evidence/` để đọc log/config/summary. Để chạy validator bố cục cần chạy `render.ps1` trước để tạo `.build/text-fit.json`; geometry được JS sinh khi build. Kiểm tra không thể xác nhận checkpoint không có trên máy và sẽ ghi rõ giới hạn đó. QA đã thực hiện trên máy gốc được giữ trong `qa/`.
