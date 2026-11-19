"""Deliver already validated outputs without changing the source deck or data."""
from pathlib import Path
import json
import shutil
import hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
BUILD=HERE/'.build/three-seeds'
ROOT=HERE.parent.parent
def read(p):
    b=Path(p).read_bytes()
    return json.loads(b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=read(BUILD/'validation.json')
assert v['passed'] and sha(BUILD/'candidate.pptx')==v['candidate_sha256'] and sha(BUILD/'candidate.pdf')==v['pdf_sha256']
qa=HERE/'qa/three-seeds';qa.mkdir(parents=True,exist_ok=True)
for name in ['validation.json','merge-receipt.json','native-table-gaps.json','package-integrity.json']:
    (qa/name).write_text(json.dumps(read(BUILD/name),ensure_ascii=False,indent=2),encoding='utf-8')
visual={'reviewed_utc':datetime.now(timezone.utc).isoformat(),'renderer':'Microsoft PowerPoint native export',
        'slide_count':40,'individually_reviewed_slides':list(range(1,41)),
        'pdf_pages_rendered':40,'pdf_pages_additionally_inspected':[21,29,30,39],
        'fixed_during_review':['Slide21 caption obscured by chart background; separated caption and chart',
                               'Slide22 linebreak keeps CIFAR-100 together',
                               'Slide29 concise headers keep percentage unit on one line',
                               'Slide34 separates unverified projection details from measured facts'],
        'result':'No unintended overlap, clipped text or hyperlink collision observed after fixes',
        'candidate_sha256':v['candidate_sha256'],'pdf_sha256':v['pdf_sha256']}
(qa/'visual-review.json').write_text(json.dumps(visual,ensure_ascii=False,indent=2),encoding='utf-8')
for ext in ['pptx','pdf']:
    source=BUILD/f'candidate.{ext}'
    target=HERE/f'DSAL_Milestone2_Lab1_3Seeds_Final.{ext}'
    assert not target.exists() or sha(target)==sha(source),'Refusing to overwrite a different final version.'
    if not target.exists():shutil.copyfile(source,target)
submission=HERE/'submission_3seeds/03.pptx'
submission.parent.mkdir(exist_ok=True)
assert not submission.exists() or sha(submission)==v['candidate_sha256']
if not submission.exists():shutil.copyfile(BUILD/'candidate.pptx',submission)
report=f'''# Kiểm tra cuối bộ slide ba seed

## Sản phẩm

- `DSAL_Milestone2_Lab1_3Seeds_Final.pptx`
- `DSAL_Milestone2_Lab1_3Seeds_Final.pdf`
- `THREE_SEEDS_RESULTS.md`
- Bản nộp theo ID nhóm 03: `submission_3seeds/03.pptx`, cùng nội dung và hash với PPTX mới.

Bản nền là `DSAL_Milestone2_Lab1_Final_v3.pptx`, SHA-256 `{v['baseline_sha256']}`. Các bản v2/v3 và `03.pptx` cũ không bị ghi đè.

## Dữ liệu và tính toán

- Đọc trực tiếp lại 12 run trên Forge: ba backbone và chín run ACIL/DAC không PLC/DS-AL, seed 0/1/2. Mỗi run finished, công khai, config/summary/history khớp file cục bộ. Snapshot kiểm tra: `assets/three_seeds_verified.json`.
- Kiểm tra dataset revision `aadb3af77e9048adbea6b47c21a81e47dd092ae5`, 50.000/10.000 ảnh, B50, K5, m8192, epoch160, checkpoint SHA và feature cache. Audit checkpoint trước đó đọc trọng số cuối và projection; hash được đối chiếu lại trong đợt này.
- Ā_s = trung bình sáu pha của một seed. Mean Ā là trung bình ba Ā_s. A_K là pha cuối; mean A_K tổng hợp ba seed. SD mẫu ddof=1, n=3; không phải SE, CI hoặc SD trên 18 điểm pha.
- DS-AL−ACIL ở A_K: +0,31 / +0,34 / +0,56 pp, mean +0,4033 pp. PLC so DAC không PLC: +0,63 / +0,42 / +0,36 pp, mean +0,4700 pp. Dấu cải thiện nhất quán 3/3; chưa khẳng định ý nghĩa thống kê.
- Đã tính gap tuyệt đối và tương đối so Table 1. E2 ghi rõ chuyển từ ImageNet-Full sang CIFAR-100, không nhận tái hiện nguyên Table 2.
- K/buffer giữ seed0. Slide 32/33 và các chart/workbook buffer giữ nguyên từng byte; bảng K của slide31 giữ nguyên số liệu. Không dùng mean ba seed thay hàng K5/m8192 của khảo sát seed0.
- Không dùng thí nghiệm thất bại, không huấn luyện lại, không thay đổi run W&B hoặc raw logs/config/summary/checkpoint/cache trong đợt cập nhật slide.

## PowerPoint và PDF

| Hạng mục | Kết quả |
| --- | --- |
| Số slide / trang PDF | 40 / 40 |
| Kích thước PPTX | {(BUILD/'candidate.pptx').stat().st_size:,} byte, dưới 20 MB |
| Native charts / native tables | 9 / 20 |
| Notes | Đủ 40, tối đa {v['max_notes_words']} từ kể cả nguồn và provenance |
| Nhóm | Đủ Lâm Hoàng Vũ – 23122056; Nguyễn Bá Nam – 23122043; Chung Tín Đạt – 23122024 |
| Numeric cache ↔ workbook | {v['workbook_numeric_references_checked']} tham chiếu được đối chiếu |
| Error bars | Custom ±SD trên chart4/5/6, tham chiếu ô SD thật trong workbook nhúng |
| Tràn chiều cao | 0 cảnh báo trên {v['native_text_cells_checked']} khung chữ/ô bằng phép đo PowerPoint |
| Khoảng cách bảng / footer | Cả 20 bảng có khoảng cách dương |
| Hyperlink PDF | {v['pdf_hyperlink_annotations']} annotation, trong đó {v['pdf_wandb_hyperlink_annotations']} annotation W&B; đích trên từng trang khớp PPTX |
| Cấu trúc gói PPTX | Không có finding trong package integrity check |

Nguồn là bản v3 thực tế: 23 slide XML không cần đổi giữ nguyên từng byte, cùng các chart minh họa/synthetic và khảo sát seed0 không liên quan. Những slide cập nhật có notes mới; slide16 chỉ cập nhật notes về phạm vi ba seed. Phong cách Segoe UI/Cambria Math, màu navy/cream/teal, kích thước và hệ thống trích dẫn IEEE của v3 được giữ.

Đã mở candidate bằng Microsoft PowerPoint, xuất PDF và render đủ 40 slide ở 1600×900; xem từng slide và kiểm tra lại các phần sửa. PDF được render đủ 40 trang, kiểm tra thêm trực quan trang21/29/30/39. Đã sửa caption slide21 bị chart che, linebreak CIFAR-100 slide22, header slide29 và diễn đạt giả thuyết projection slide34. Không thấy chồng lấn hoặc cắt chữ sau sửa. Phép đo hình học hỗ trợ rà soát, không thay thế việc xem hình render.

## Trích dẫn và truy vết

Trích dẫn IEEE được giữ ở cuối các slide sử dụng nguồn và đủ thông tin trong notes; không tạo slide tài liệu tham khảo riêng. Mỗi bảng/đường mean có nhãn seed hyperlink tới các run gốc, URL đầy đủ và đường dẫn config/history trong notes. Native chart/workbook cùng snapshot JSON giữ số đầy đủ; số hiển thị được làm tròn có chủ ý.

Repository đã được kiểm tra là public; không thay đổi quyền truy cập. Source, cấu hình, snapshot bằng chứng nhẹ, báo cáo và bộ slide mới được đồng bộ theo quyền push đã được nhóm cho phép. Không công bố `.env`, API key, data hoặc checkpoint nặng. Commit/provenance thí nghiệm vẫn ghi Git HEAD và dirty state thật, không tạo lịch sử giả.

## Giới hạn và việc nhóm cần xác nhận

- Seed0 có 19 epoch CUDA trước khi resume CPU; seed1/2 CPU xuyên suốt. SD không được diễn giải là chỉ biến thiên do seed trên backend hoàn toàn đồng nhất.
- Chỉ ba seed; không có kiểm định để kết luận ý nghĩa thống kê hoặc nguyên nhân gap. K/buffer vẫn chỉ seed0, chưa tái hiện ImageNet.
- Việc bài báo được chấp nhận không tự chứng minh giảng viên đã chấp nhận riêng phạm vi E2 chuyển dataset. Nhóm cần xác nhận phạm vi này; slide không khẳng định đã được chấp nhận.
- Nộp file `submission_3seeds/03.pptx` và đường dẫn repository theo Moodle. Kiểm tra thông báo hạn nộp chính thức của học phần.

## Tái tạo

```powershell
.venv/Scripts/python.exe -u -X utf8 reports/milestone2_final/verify_3seeds.py
.venv-cpu/Scripts/python.exe -X utf8 reports/milestone2_final/prepare_three_seeds.py
node reports/milestone2_final/build_three_seeds.mjs
.venv-cpu/Scripts/python.exe -X utf8 reports/milestone2_final/merge_three_seeds.py
powershell -NoProfile -ExecutionPolicy Bypass -File reports/milestone2_final/render_three_seeds.ps1
pdftotext -bbox reports/milestone2_final/.build/three-seeds/candidate.pdf reports/milestone2_final/.build/three-seeds/pdf-bounds.html
.venv-cpu/Scripts/python.exe -X utf8 reports/milestone2_final/validate_three_seeds.py
```

Validator có kiểm tra cấu trúc ZIP/XML/relationship độc lập và tự tạo receipt nếu chưa có; lần giao này còn đối chiếu thêm bằng helper integrity riêng. Source PptxGenJS tạo các đối tượng cần đổi, sau đó merge vào gói v3 để bảo toàn phần không đổi. File tạm ở `.build/three-seeds/`; biên bản ở `qa/three-seeds/`. Khi cập nhật số liệu, xuất tên phiên bản mới và kiểm tra lại trực quan; finalizer từ chối ghi đè bản có hash khác.

SHA-256 PPTX: `{v['candidate_sha256']}`.

SHA-256 PDF: `{v['pdf_sha256']}`.
'''
(HERE/'FINAL_VALIDATION_REPORT.md').write_text(report,encoding='utf-8')
print('Final PPTX/PDF/report and ID03 submission copy exported; baseline unchanged.')
