# Yêu cầu giảng viên → slide / bằng chứng

> Publication update 2026-11-20: see [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md). The team reports submission and has authorized publishing this revision. References below to an unpushed/local-only revision describe the original 2026-11-19 review. Original files and their manifest are archived in [history](history/review-delivery-20261119.zip). The review score is not an official grade.

Áp dụng bộ40slide StrictReview mới. PASS là có bằng chứng trong sản phẩm, không phải giảng viên đã xác nhận điểm. Các phần Reading/Reproduction/Analysis/Empirics được đọc từ PDF yêu cầu nhóm cung cấp.

| Yêu cầu | Slide / file | Trạng thái |
|---|---|---|
| Bài toán và ví dụ nhóm |2–3; hình tự dựng | PASS |
| Ít nhất2tiền nhiệm, ý tưởng / hạn chế / hệ quả |4; notes20 | PASS |
| Đóng góp lý thuyết / kỹ thuật / thực nghiệm, tính mới |5 | PASS; không nhận RLS là phát minh mới |
| Bài toán hình thức và ký hiệu |7–8 | PASS |
| Pipeline tự vẽ |6,9–10 | PASS |
| Ridge objective và nghiệm |11 | PASS |
| Padding, C-RLS, proof sketch |12–14; gain cũ gộp vào notes13 | PASS |
| Theorem1 và điều kiện, giới hạn |15; notes16 | PASS |
| Residual / activation / PLC / score |10,17–19; notes17 phân biệt E_k và E_joint | PASS |
| Độ phức tạp và so predecessor |16,20; notes4/20 | PASS về phân tích; không có benchmark runtime LwF/iCaRL |
| Dataset/methodology/metrics |7,21,23,25 | PASS |
| Core: hai thí nghiệm quan trọng + phân tích nhóm |22,27–33,36 | PARTIAL: headline đầy đủ phần CIFAR; Figure4 chỉ Tanh/CIFAR; cần đánh giá mức bao phủ |
| K25/50 đối chiếu paper |26,31 | PASS cho seed0, không SD nhiều seed |
| Số paper và nhóm cạnh nhau, gap tương đối |26–28,31 | PASS |
| Phân tích sai lệch, không đoán nguyên nhân |28,34,37; GAP_PROTOCOL_AUDIT.md | PASS cho phân loại evidence; PARTIAL về chẩn đoán nguyên nhân định lượng |
| DAC/PLC không cải thiện đơn điệu |29,30,40 | PASS; có paired counts, base/novel |
| Một phân tích nhóm |32–33 buffer/time | PASS trong giới hạn một seed |
| Mỗi số nhóm có W&B |Các slide số liệu và notes, EXPERIMENT_MAPPING.md | PASS kỹ thuật:24finished/public; UNVERIFIED về host Forge có được chấp nhận thay wandb.ai |
| Source độc lập, mã tác giả chỉ đối chiếu |24,37; src/methods/analytic.py | PASS theo provenance/code review; không là chứng nhận plagiarism tuyệt đối |
| Dataset programmatic từ HF/Kaggle |src/datasets/cifar100.py; RUNBOOK.md | PASS cho HF loader đã dùng; môi trường sạch chưa rerun toàn pipeline |
| README script/run mapping |README.md; EXPERIMENT_MAPPING.md | PASS local; bản sửa chưa public theo yêu cầu không push |
|20–40slide, dưới20MB |40slide; QA receipt và file thực tế | PASS sau final validation |
| Notes mọi slide≤500từ |40notes, QA receipt ghi max thực tế | PASS sau final validation |
| IEEE bottom, không slide References riêng |Số theo thứ tự xuất hiện1–7; URL hyperlink | PASS sau kiểm tra package và render |
| Thành viên/MSSV |1 | PASS |
| Mọi nội dung truy vết về repo public |Local source/JSON/log; main84b9564 chứa bản trước | BLOCKED cho additions StrictReview đến khi nhóm cho phép công bố |
| Nộp PPTX và repo URL riêng Moodle |RUNBOOK.md | UNVERIFIED / nhóm thực hiện |
| Milestone3:3strengths,2theoretical limits,2directions |docs/THEORY_CRITIQUE.md; mechanism evidence | PARTIAL ở mức nội dung; không chấm như poster cuối |
| Lab2poster A2 dọc / workshop |reports/output/03-poster-draft.pptx | PARTIAL: vẫn là draft, chưa chứng nhận bản nộp cuối |
