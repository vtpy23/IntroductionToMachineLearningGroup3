# Kiểm tra và hoàn thiện Milestone 2 + Lab 1

Ngày đối chiếu: 19/11/2026. Báo cáo cho bộ mới 40 slide trong thư mục này. Bản cũ, checkpoint, log và kết quả thực nghiệm được giữ nguyên. Đợt thiết kế ban đầu không push. Sau đó người dùng cho phép công bố cả slide; trạng thái repository được kiểm tra lại là public, bản công bố kèm nguồn và snapshot log/config nhẹ. Không upload hoặc sửa W&B trong đợt công bố.

## Nguồn yêu cầu

- `index.pdf`, trang 1–2: hướng dẫn tổng quan tiếng Anh, yêu cầu repo công khai, truy vết, W&B và tính liêm chính.
- `Bản dịch Đồ án.pdf`, trang 5–7: Reading và định dạng bộ slide; trang 8–10: Reproduction; trang 11–14: Analysis/Empirics.
- Không tìm thấy các file `reading.md`, `reproduction.md`, `analysis.md`, `empirics.md` độc lập trong cây mã nguồn. Các trang tương ứng đã được tìm thấy trong PDF 14 trang do nhóm cung cấp, không suy đoán là thiếu hướng dẫn. Chưa có nguồn tiếng Anh riêng của các trang chi tiết để kiểm tra lại bản dịch.
- Bài DS-AL bản AAAI: `01653-AAAI24.ZhuangH.pdf`, 8 trang. Supplementary: `docs/references/DS-AL-supplementary.pdf`, 3 trang. Bảng 1, Eq. (11)–(19) và Algorithm 1 đã được đối chiếu thêm trên ảnh render PDF.

## Bảng kiểm tra ban đầu

| Hạng mục | Yêu cầu giảng viên | Hiện trạng bộ cũ | Đạt/Chưa đạt | Cần chỉnh sửa |
|---|---|---|---|---|
| Số slide | 20–40 gồm phụ lục, PDF yêu cầu trang 6 | 30 trang | Đạt | Giữ bản mới trong giới hạn |
| Notes | Mỗi slide có notes ≤500 từ, trang 6 | Có nhưng nhiều notes mô tả renderer thay vì giải thích | Đạt hình thức, cần cải thiện | Viết notes phục vụ đọc và bảo vệ nội dung |
| Trích dẫn | IEEE tại chân slide, không References riêng, trang 6 | Có nhưng cỡ chữ nhỏ | Cần cải thiện | Citation ngắn đủ thông tin trên slide, chi tiết/link trong notes |
| Minh họa | Nhóm tự dựng, không chép hình tác giả, trang 7 | Nhiều slide chỉ có ba dòng chữ | Chưa đạt mức trực quan mong muốn | Dựng native diagrams và chart từ dữ liệu |
| Nội dung lý thuyết | Ký hiệu, thành phần, theorem, trực giác và complexity, trang 6 | C-RLS/proof quá cô đọng, ví dụ PLC chưa thể hiện rõ tác dụng | Cần cải thiện | Phân tích điều kiện, padding, gain và trước/sau PLC |
| Phạm vi Core | ≥2 thí nghiệm quan trọng + phân tích nhóm tự thiết kế, trang 8 | Có headline CIFAR, ablation chuyển miền và các khảo sát | Đạt có giới hạn | Nêu rõ ablation được chuyển từ ImageNet-Full sang CIFAR, không coi là tái hiện nguyên Table 2 |
| Bảng paper/nhóm | So sánh và độ lệch tương đối, trang 9 | Có số đúng nhưng thiếu độ lệch và phân tích cụ thể | Chưa đủ | Bổ sung chênh lệch pp, relative %, phạm vi kết luận |
| W&B | Run thật, public; mỗi số có run; trang 9–10 | URL có trong một số notes, chữ “Đã có run URL” còn trên slide | Chưa đủ | Đặt URL thật có hyperlink, mapping từng kết quả |
| Tự triển khai | Core tự viết; mã tác giả chỉ kiểm chứng, trang 8 | Có `src/methods/analytic.py`, tests và comparison | Đạt trong phạm vi kiểm tra | Chỉ ra tests, source hash và khác biệt batch semantics |
| Phân tích bổ sung | Nhóm tự thiết kế, trang 8 | m=512/1024/2048/8192 có thật, paper không khảo sát m này | Đạt có giới hạn | RQ, hypothesis, biến kiểm soát, timing và hạn chế projection không lồng nhau |
| Bộ nhớ | Phân tích complexity, trang 6 | Hai ma trận 8192² FP64 =1 GiB là đúng nhưng dễ nhầm RAM đo | Cần nhấn mạnh | Tách storage lý thuyết, workspace, backbone và cache |
| Số lần chạy | Giảng viên yêu cầu seed/reproducibility, không thấy bắt buộc 3 seed ở trang 8–10 | Benchmark chỉ seed 0 | Hạn chế tái hiện | Supplement C dùng trung bình 3 runs; không tạo std của nhóm |
| Dung lượng | PPTX <20 MB, trang 7 | <1 MB | Đạt | Kiểm tra lại bản mới |
| Repo công khai | Bắt buộc, index trang 1 và bản dịch trang 7 | Cần kiểm tra metadata live | Chờ xác minh | Báo trạng thái thực, không đổi privacy |
| Deadline | Theo Moodle, index trang 1 | README có ngày nhóm ghi nhận | Không dùng làm nguồn chính thức | Không đưa deadline chưa kiểm tra Moodle vào slide |

## Ưu tiên triển khai

1. Khóa và xác minh bằng chứng local/W&B, không sửa số đo.
2. Rà soát công thức và phạm vi bảo đảm, sửa ví dụ PLC.
3. Tổ chức lại câu chuyện, viết phân tích định lượng và giới hạn.
4. Thiết kế lại toàn bộ deck với diagrams, charts và notes có căn cứ.
5. Xuất, render từng trang, kiểm tra bố cục/citation/hyperlink/số đo, rồi hoàn thiện mapping và hướng dẫn.

## Ghi chú phạm vi

Không chạy lại backbone hoặc thêm seed: một seed cần khoảng 4 giờ CPU theo log thực tế, hai seed bổ sung khoảng 8 giờ cộng phần analytic. Nhiệm vụ hiện tại ưu tiên hoàn thiện nội dung bằng kết quả hợp lệ đã có. Các kiểm thử nhỏ chạy lại để xác minh triển khai, không tạo benchmark mới.

## Kết quả đối chiếu cuối cùng

| Hạng mục | Trạng thái bản mới | Bằng chứng / giới hạn |
|---|---|---|
| 20–40 slide, không References riêng | Đạt: 40, gồm 5 trang phụ lục | PPTX/PDF và `slide_content.json` |
| Notes cho từng slide, ≤500 từ | Đạt | Validator đếm toàn bộ notes, bao gồm trích dẫn và URL |
| IEEE trên slide và nguồn đầy đủ | Đạt trong nguồn đã có | Chân trang đánh số [1]–[6], notes có đầy đủ metadata và URL; hai trang thuần provenance/readiness không cần paper citation |
| Sơ đồ và minh họa tự dựng | Đạt | Timeline, pipeline, padding, gain/proof, DAC, PLC, fusion là shape/table native; không dùng screenshot hình tác giả |
| Chart/bảng chỉnh sửa | Đạt | 8 chart native có workbook nhúng, bảng và chữ chỉnh sửa được; công thức là text native Cambria Math, không phải ảnh |
| Lý thuyết và tiền nhiệm | Đạt trong phạm vi đọc hiểu | LwF/iCaRL/ACIL, vai trò từng thành phần, điều kiện theorem, phác thảo chứng minh, gain, complexity; chi tiết trong notes |
| Số liệu / W&B | Đã xác minh 13 run | Finished; summary và numeric history khớp local; đọc public không xác thực thành công. 11 run được dùng trực tiếp trong deck; 2 run cơ chế khác được giữ trong evidence, không biến thành kết quả CIFAR |
| Headline comparison | Có kết quả seed 0 | CIFAR-100 B50/ResNet-32; so Table 1 đúng hàng, phân biệt paper và nhóm |
| Thí nghiệm quan trọng thứ hai | Có điều kiện về phạm vi | DAC/PLC chuyển ImageNet-Full/C=1.4 thành CIFAR-100/C=0.6. Chưa tái hiện nguyên Table 2; cần giảng viên chấp nhận bản chuyển protocol hoặc bổ sung thí nghiệm |
| Phân tích nhóm tự thiết kế | Có, kết luận giới hạn | Buffer 512/1024/2048/8192; xác định RQ, biến kiểm soát, accuracy/fit time; projection không lồng nhau, một seed |
| Nhiều seed của benchmark | Chưa có | Không dựng mean/std giả; 3 seed tổng hợp không thay 3 seed CIFAR. Không thấy quy định giảng viên bắt buộc chính xác 3 seed; đây là khác biệt với Supplement C |
| PPTX <20 MB, PDF tương ứng | Đạt | PDF xuất trực tiếp từ chính PPTX bằng PowerPoint; 40 trang; kiểm tra package, fonts và text fit |
| Công khai repository | Đạt khi công bố | GitHub connector kiểm tra lại `vtpy23/IntroductionToMachineLearningGroup3`: visibility public. Không thực hiện đổi privacy |
| Truy vết bản mới từ GitHub | Có trong bản công bố | Nguồn, PPTX/PDF, evidence, mapping và snapshot config/summary/history được công bố cùng README liên kết trực tiếp |
| Deadline / ID Moodle | Chưa xác minh trực tiếp Moodle | Alias `03.pptx` theo thông tin nhóm 3 do người dùng cung cấp; không đưa ngày hạn đoán vào deck |

## Rà soát từng slide cũ và cách xử lý

Nguồn: `reports/output/03.pptx`, trích xuất đủ text và notes vào `.build/old-slide-audit.json`. Bảng sau ghi nhận thiếu sót hoặc điểm giữ lại; không khẳng định slide cũ sai khi chỉ cần làm rõ.

| Cũ | Nhận xét | Cách xử lý trong bộ mới |
|---|---|---|
| 01 DS-AL | Tên bài/nhóm đúng; cần nhận diện phạm vi | 01: cover hai nhánh, ghi Milestone 2 + Lab 1 |
| 02 CIL | Nặng mô tả chữ | 02: ví dụ timeline động vật, không task ID |
| 03 Exemplar-free | Dễ hiểu thành xóa mọi dữ liệu/đảm bảo privacy | 03: replay vs trạng thái đại số, phân biệt cache phục vụ đánh giá |
| 04 LwF | Hạn chế thực tế chưa rõ | 04: cơ chế distillation và giới hạn dữ liệu mới |
| 05 Replay/ACIL | Thiếu đối chiếu với nhu cầu nhánh bù | 04–05: ba tiền nhiệm và khoảng trống |
| 06 Đóng góp | Trộn bảo đảm toán học với hiệu quả đo | 05: chia lý thuyết/kỹ thuật/thực nghiệm |
| 07 Protocol | Số lớp đúng; thiếu tiến trình cụ thể | 07: bảng B50 qua 5 pha |
| 08 Ký hiệu | Cần thống nhất kích thước và chỉ số | 08,36: thống nhất nₖ,cₖ,m,d; G là Gram, A là accuracy |
| 09 Quy trình | Luồng main/comp và nhãn bù khó theo | 06: native architecture tách suy luận và tạo residual |
| 10 Backbone | Cần log thật và ý nghĩa base accuracy | 09: chart 160 epoch, final base 76.92%, CPU |
| 11 Buffer | Chỉ có công thức | 10: projection, hai activation và chart hàm toán |
| 12 Ridge | Chưa nối objective và closed form | 11: hai biểu thức, gamma và feature cố định |
| 13 Padding | Mở rộng cột khó hình dung | 12: bảng trước/sau với cột 0 |
| 14 C-RLS | Bước cập nhật quá cô đọng | 13,36: gain/R/W và kiểm tra kích thước |
| 15 Theorem | Cần tránh hiểu không quên ở mức CNN | 15: điều kiện và phạm vi ridge trên fixed features |
| 16 Proof | Thiếu liên kết với công thức gain | 14,36: G/Q sufficient statistics và Woodbury |
| 17 DAC | Thời điểm tạo residual rất quan trọng | 17,37: sau main toàn pha, phân biệt batch semantics |
| 18 PLC | Ví dụ chưa bộc lộ rõ thay đổi | 18: residual âm ở lớp cũ, trước/sau từng ô |
| 19 Fusion | Cần ý nghĩa C và score | 19: hai nhánh vào tổng, score không tự là probability |
| 20 Complexity | 1 GiB dễ bị đọc thành peak RAM | 16,20: solver, bậc chi phí, storage lý thuyết; so ACIL/replay trong notes |
| 21 Metrics | Cần định nghĩa pha base trong A-bar | 21: K+1 lần đánh giá và curve thật |
| 22 Paper | Giữ đúng số; cần nguồn/table/backbone rõ | 26: ResNet-32 không ngoặc; DS-AL mean±std 3 runs |
| 23 Scope | Có nguy cơ coi CIFAR ablation là nguyên Table 2 | 22: ghi rõ chuyển dataset/C và điều kiện chấp nhận |
| 24 Implementation | Cần chứng cứ kiểm thử cụ thể | 24,37: 11 tests và đối chiếu official checkout |
| 25 Traceability | Chưa đủ URL thật trên slide | 25,39: config→log→W&B, full hyperlinks và SHA |
| 26 Results | Thiếu phân tích pp và relative gap | 27–28: native charts và bảng gap theo công thức rõ |
| 27 Ablation | Chưa tách tác dụng riêng của DAC/PLC | 29–30: −0.32/+0.63/+0.31 pp và old/new class |
| 28 K/buffer | Hai câu hỏi trộn cùng trang | 31–33: tách K, thiết kế buffer và accuracy/fit time |
| 29 Gap | Các khả năng dễ bị đọc như nguyên nhân đã chứng minh | 34: bằng chứng vs giả thuyết, không quy kết causal |
| 30 Conclusion | Cần nêu giới hạn và điều kiện nộp | 35,38–40: kết luận seed 0, phạm vi theorem, provenance/publication |

## Phát hiện học thuật và nội dung bổ sung

1. Table 1 đối chiếu trực quan tại trang PDF 5 (trang in 17241). Chỉ lấy ResNet-32, không lấy ResNet-18 trong ngoặc. DS-AL A_K gốc 58.26/58.32/58.37 và A-bar 66.39/66.20/66.33 cho K=5/25/50. Không sửa số tác giả thành số nhóm.
2. Nhóm DS-AL K=5 A_K=56.87 so paper 58.26: gap −1.39 pp, tương đối −2.39%. ACIL 56.56 so 57.78: −1.22 pp, tương đối −2.11%. Độ lệch không tự chứng minh nguyên nhân.
3. DAC không PLC: 56.24%; thêm PLC: 56.87%; riêng PLC +0.63 pp. DAC đơn lẻ so ACIL −0.32 pp; DS-AL đầy đủ +0.31 pp. A-bar tăng chỉ khoảng 0.03387 pp so ACIL. Không mô tả mọi nhánh bù đều giúp.
4. DS-AL vs ACIL ở pha cuối: lớp mới +2.60 pp, lớp base −1.98 pp. Bổ sung trade-off, không gọi accuracy tổng giảm là toàn bộ forgetting.
5. K=5/25/50 có A_K=56.87/56.83/56.87: khoảng 0.04 pp ở seed 0; chưa là bằng chứng bất biến chính xác toàn hệ DS-AL.
6. Buffer tăng 512→8192: A_K 51.46→56.87%, fit 0.901→86.513 s. Thời gian là cộng `fit_seconds` qua pha, không CNN/feature extraction/W&B; không so runtime với RTX 3090 tác giả.
7. Theorem main ridge cần feature/projection/activation/gamma cố định và padding đúng; không bảo đảm joint CNN hoặc differential privacy. Residual lịch sử không được tính lại khi pha đổi.
8. So mã tác giả cùng dữ liệu/projection: batch20 gần sai số số học; batch4 khác nhánh bù/score. Chỉ kết luận khác semantics thời điểm residual; chưa chứng minh đó là nguyên nhân gap CIFAR hay toàn bộ official code sai.
9. Minh họa PLC là giả định đại số, được gắn nhãn minh họa, không phải số liệu nghiên cứu; giữ residual âm ở lớp mới và chỉ xóa cột lớp cũ. Pha base không PLC.
10. Trạng thái hai ma trận FP64 bằng 1 GiB là phép tính 2×8192²×8 byte; head/cross-correlation/workspace/cache chưa tính. Không có peak RAM CPU hợp lệ để vẽ.

## Thiết kế và kiểm tra sản phẩm

- 16:9, Segoe UI và Cambria Math có trên máy; nền ivory/navy, màu teal/blue/orange nhất quán. Nội dung học thuật được mở rộng có nguồn, không thay số thực nghiệm.
- Render toàn bộ 40 trang bằng Microsoft PowerPoint, xem trực quan từng trang. Đã sửa line geometry âm làm PowerPoint không mở được, canh cột PLC, labels trục epoch, 6 vùng chữ vượt chiều cao, overlap chú thích/bảng ở trang 32, chú thích/run URL trang 34 và 37. Bản cuối không còn overflow candidate trong 665 vùng text/cell; kiểm tra mắt bổ sung cho overlap vì phép đo chiều cao không phát hiện mọi chồng lấn.
- Kiểm tra gói OOXML, slide/notes, citations, hyperlinks, chart caches và workbook native, PDF/page count và text, nguồn log, checkpoint hash; kết quả máy đọc trong `.build/final-validation.json`.
- 11 kiểm thử toán học/triển khai nhỏ chạy lại: **11 passed in 9.33s**, log `.build/tests.log`. Không rerun benchmark để làm đẹp số.
- Kết quả QA: **8 chart**, **18 bảng**, **11 run được hyperlink trực tiếp**, **13 run đã xác minh**, **58 file thực nghiệm/checkpoint giữ nguyên hash**. Notes tối đa và dung lượng/hash chính xác của bản công bố ghi trong `qa/final-validation.json`. Gói OOXML không có finding; alias `03.pptx` có cùng SHA-256 với bản tên đầy đủ.
- PDF được render thêm đủ 40 trang bằng Poppler để đối chiếu với ảnh xuất từ PowerPoint; các trang công thức, PLC và bar chart được kiểm tra trực quan thêm. PyMuPDF có sẵn nhưng DLL không import được nên dùng Poppler đang có, không sửa môi trường để phục vụ xuất slide. Poppler phát cảnh báo font fallback Symbol/ArialUnicode; các trang có công thức/tiếng Việt đã xem không bị mất ký tự, và font Segoe UI/Cambria Math xuất hiện trong PDF.
- Read-only W&B audit dùng SDK 0.31.0; provenance của các run benchmark vẫn ghi SDK 0.23.1, Python 3.11.8, torch 2.5.1+cpu. Không thay đổi môi trường.
- Git provenance benchmark `d8d485f6cbf10e266adf59b82a49a0265267e93c`, `git_dirty=true`: chỉ hash commit chưa đủ; manifest `source_sha256` được giữ trong evidence. Các thay đổi cũ ngoài thư mục này được giữ nguyên.

## Điểm còn mở trước khi nộp

- Trạng thái public và công bố nguồn đã được xử lý theo yêu cầu push mới của nhóm. Không nhầm commit công bố với commit thực nghiệm d8d485f; giữ provenance dirty/source hashes trong snapshot.
- Cần làm rõ với giảng viên việc E2 chuyển dataset; không ghi nhận là tái hiện nguyên Table 2. Nếu yêu cầu strict original protocol, cần đánh giá chi phí ImageNet riêng.
- Muốn so với mean±std của paper cần thêm seed benchmark; không có kết quả seed1/2 hiện tại. Ước lượng CPU là từ log máy này, không cam kết thời gian Colab/Kaggle.
- Chưa cô lập ảnh hưởng class order, projection, backbone initialization, phiên bản thư viện hoặc residual timing lên gap ảnh thật. Đây là các giả thuyết, không kết luận.
- Chưa xác minh Moodle deadline/ID tự động và chưa có bản tiếng Anh riêng của các trang hướng dẫn chi tiết. Không tự tạo thông tin còn thiếu.

Nguồn khoa học đầy đủ và link nằm trong `SLIDE_CONTENT.md` theo từng slide; nguồn PDF/hash trong `qa/source-documents.json`; mapping và URL thực tế trong `EXPERIMENT_TRACEABILITY.md`. File yêu cầu môn học và PDF bài báo gốc giữ local; bài báo được dẫn bằng URL/DOI. Không có thao tác upload W&B, sync, privacy change hay xóa dữ liệu. GitHub push gồm mã, tài liệu và sản phẩm đã được người dùng cho phép.
