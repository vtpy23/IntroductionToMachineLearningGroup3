# Nội dung bộ slide DS-AL

Bản làm việc. Số thực nghiệm và W&B được cập nhật từ run hoàn tất.

## 1. DS-AL

- Học tăng dần lớp không lưu mẫu cũ
- Đọc hiểu và tái hiện thực nghiệm
- Nhóm Vũ · Nam · Đạt

**Ghi chú thuyết trình:** Nhóm nghiên cứu DS-AL của Zhuang và cộng sự, AAAI 2024. Phần đọc hiểu trình bày phương pháp bằng hệ ký hiệu thống nhất. Phần tái hiện chỉ sử dụng số đo hoàn tất, phân biệt rõ smoke test với cấu hình đầy đủ. Bản nội dung này được cập nhật theo bằng chứng trong repository.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 2. Bài toán class-incremental learning

- Mỗi pha cung cấp các lớp mới
- Dự đoán trên toàn bộ lớp đã gặp
- Không có task ID khi suy luận

**Ghi chú thuyết trình:** Ví dụ do nhóm tự xây dựng: hệ thống phân loại động vật ban đầu học chó và mèo, sau đó nhận chim và cá. Sau pha mới, hệ thống vẫn cần nhận chó và mèo. Việc biết ảnh thuộc pha nào khi suy luận sẽ làm bài toán dễ hơn và không phù hợp đánh giá CIL ở đây.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 3. Ràng buộc exemplar-free

- Ảnh cũ không được giữ để replay
- Kiến thức cũ phải nằm trong trạng thái mô hình
- Thêm lớp làm tăng cạnh tranh giữa các đầu ra

**Ghi chú thuyết trình:** Không lưu ảnh không có nghĩa mô hình không giữ thông tin về dữ liệu. DS-AL duy trì các ma trận thống kê. Đó là khác biệt về dạng bộ nhớ, không phải một chứng minh bảo mật hình thức. Accuracy lớp cũ có thể giảm khi thêm lớp dù head đạt nghiệm học gộp.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 4. LwF và distillation

- Giữ đầu ra mạng cũ bằng một loss bổ sung
- Dữ liệu hiện tại đại diện gián tiếp cho kiến thức cũ
- Đánh đổi giữa học lớp mới và giữ lớp cũ

**Ghi chú thuyết trình:** LwF là một tiền nhiệm thuộc nhóm regularization. Khi dữ liệu pha hiện tại khác nhiều dữ liệu cũ, ràng buộc distillation trên dữ liệu hiện tại có thể không đại diện đủ cho phân biệt lớp cũ. Không suy ra rằng LwF thất bại ở mọi tình huống. DS-AL chọn cách giải đại số trên embedding cố định thay cho việc chỉ thêm ràng buộc vào BP.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [4] Z. Li and D. Hoiem, Learning without Forgetting, IEEE TPAMI, vol. 40, no. 12, pp. 2935–2947, 2018.

## 5. Replay và ACIL

- Replay giữ exemplar để học cùng dữ liệu mới
- ACIL giữ ma trận tương quan của feature cố định
- DS-AL bổ sung một nhánh học phần dư

**Ghi chú thuyết trình:** Replay như iCaRL cần ngân sách lưu mẫu, còn ACIL dùng thống kê bậc hai. ACIL là nền tảng trực tiếp để hiểu C-RLS. Hạn chế DS-AL muốn xử lý là khả năng khớp của một head tuyến tính trong không gian đặc trưng mở rộng.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [3] H. Zhuang et al., ACIL: Analytic Class-Incremental Learning with Absolute Memorization and Privacy Protection, NeurIPS, vol. 35, pp. 11602–11614, 2022. [5] S.-A. Rebuffi et al., iCaRL: Incremental Classifier and Representation Learning, CVPR, 2017.

## 6. Các đóng góp của DS-AL

- Lý thuyết: C-RLS và tương đương ridge học gộp của nhánh chính
- Kỹ thuật: DAC cùng PLC
- Thực nghiệm: đối sánh benchmark, ablation và nhiều pha

**Ghi chú thuyết trình:** Phân biệt đóng góp đã được chứng minh với quan sát thực nghiệm. Theorem 1 nói về head chính. Khả năng tăng accuracy nhờ DAC và độ ổn định ở nhiều pha được bài báo đánh giá bằng dữ liệu. Không coi các nhận định này là cùng một bảo đảm toán học.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 7. Protocol CIFAR-100 B50

- 50 lớp base
- 50 lớp còn lại chia đều qua K pha
- ResNet-32, kiểm tra trên tất cả lớp đã thấy

**Ghi chú thuyết trình:** CIFAR-100 có 50.000 ảnh train và 10.000 ảnh test. Thứ tự lớp được ghi trong từng run. Với K=5, mỗi pha mới có 10 lớp. K=25 có 2 lớp mỗi pha, K=50 có 1 lớp mỗi pha. Không dùng tập test để huấn luyện hoặc chọn checkpoint tốt nhất.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [7] A. Krizhevsky, Learning Multiple Layers of Features from Tiny Images, University of Toronto, 2009. Dataset: huggingface.co/datasets/uoft-cs/cifar100.

## 8. Hệ ký hiệu


**Ghi chú thuyết trình:** X_M và X_C là embedding theo hàng mẫu. W có số hàng bằng chiều buffer và số cột bằng số lớp đã gặp. Nhãn là one-hot trong hệ chỉ số đã remap theo class order. Một batch tính toán không được coi là một pha học mới.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 9. Quy trình DS-AL

- Huấn luyện CNN trên base
- Đóng băng CNN và phép chiếu
- Cập nhật head chính, tạo residual, cập nhật head bù

**Ghi chú thuyết trình:** Sơ đồ do nhóm tạo lại từ mô tả phương pháp. Ở mỗi pha, toàn bộ dữ liệu pha đó cập nhật nhánh chính trước. Sau đó mới tính residual bằng head chính đã hoàn tất. Các lớp cũ không được đưa trở lại để fit. Hai nhánh được kết hợp tại suy luận.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning.

## 10. Huấn luyện backbone

- SGD 160 epochs trên base classes
- Learning rate 0.1, giảm tại epoch 80 và 120
- Sau đó giữ cố định trọng số CNN

**Ghi chú thuyết trình:** Theo Supplement C cho CIFAR-100 ResNet-32: batch128, momentum0.9, weight decay5e-4. Dùng crop, flip và normalization khi base training, không augmentation trong AL. CNN cố định là điều kiện để thống kê feature lịch sử tiếp tục có cùng ý nghĩa.

**Nguồn tại chân slide:** [2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning. [6] K. He et al., Deep Residual Learning for Image Recognition, CVPR, 2016.

## 11. Buffer và hai embedding

- Z = f(x) B
- X_M = ReLU(Z)
- X_C = tanh(Z)

**Ghi chú thuyết trình:** Buffer ở đây là phép mở rộng feature ngẫu nhiên, không phải replay buffer. Dự án ghi rõ distribution, seed, chiều m và không bias. Phân phối chính xác từng run trong paper chưa được mô tả đủ bởi PDF, nên đây là một nguồn cần xem xét khi phân tích sai lệch.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 12. Bài toán ridge của nhánh chính

- min ||Y − X_M W_M||² + gamma ||W_M||²
- W_M = (X_MᵀX_M + gamma I)⁻¹ X_MᵀY
- gamma > 0

**Ghi chú thuyết trình:** Các chuẩn trong objective là Frobenius. gamma làm bài toán có nghiệm duy nhất ngay cả khi embedding không đủ hạng. Head tuyến tính trong embedding không đồng nghĩa mô hình tuyến tính trực tiếp trên pixel, vì CNN và ReLU đã tạo ánh xạ phi tuyến.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 13. Mở rộng không gian nhãn

- Thêm các cột 0 vào head cũ
- Nhãn pha mới dùng chỉ số lớp toàn cục
- Các lớp của những pha khác nhau không giao nhau

**Ghi chú thuyết trình:** Padding head và nhãn là phần thiết yếu của C-RLS. Nếu giữ one-hot chỉ trong các lớp mới mà không remap/pad đúng, số chiều có thể vẫn hợp lệ trong một số thao tác nhưng objective sẽ sai. Pipeline lưu class order và kiểm tra giả định disjoint.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 14. Cập nhật C-RLS

- R mới từ R cũ và X của pha hiện tại
- W mới từ W cũ đã padding và lỗi dự đoán hiện tại
- Không cần đọc lại ảnh cũ

**Ghi chú thuyết trình:** Công thức (12) dùng Woodbury để cập nhật nghịch đảo ma trận tự tương quan. Công thức (11) cập nhật head sau khi mở rộng nhãn. Implementation hỗ trợ RLS trực tiếp và tích lũy thống kê rồi Cholesky. Hai cách được kiểm tra với nghiệm ridge học gộp.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 15. Theorem 1 và phạm vi bảo đảm

- Head chính tăng dần bằng head ridge học gộp
- Giữ cùng feature, projection, gamma và dữ liệu
- Đánh giá trong số học chính xác

**Ghi chú thuyết trình:** Không mở rộng kết luận sang huấn luyện joint toàn bộ CNN. Không suy ra head bù bất biến theo pha. Cũng không suy ra accuracy lớp cũ luôn giữ nguyên vì tập lớp dự đoán tăng lên. Phân biệt điều kiện của định lý với các thông điệp tổng quát ở introduction.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning.

## 16. Ý tưởng chứng minh

- G = gamma I + tổng XᵀX
- Q = tổng XᵀY, với cột nhãn được padding
- W = G⁻¹Q và áp dụng Woodbury

**Ghi chú thuyết trình:** Supplement A dùng iACM và cross-correlation để xây dựng đệ quy. Tính cộng của thống kê giải thích vì sao không cần giữ exemplar cho mục tiêu chính. gamma phải được cộng một lần cho objective toàn cục, không cộng lại mỗi pha.

**Nguồn tại chân slide:** [2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning.

## 17. DAC học phần dư

- E_k = Y_k − X_M,k W_M,k
- Dùng activation khác cho nhánh bù
- Sinh E_k sau khi nhánh chính hoàn tất pha k

**Ghi chú thuyết trình:** DAC cố khớp phần tín hiệu head chính chưa khớp. Nhãn bù không phải nhãn one-hot gốc mà phụ thuộc head chính tại thời điểm tạo. Điều này tạo khả năng phụ thuộc lịch sử pha. Cách giải thích residual là null-space cần điều kiện toán học bổ sung khi có regularization.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 18. Previous Label Cleansing

- Pha0 giữ residual trên base classes
- Pha mới đặt cột residual của lớp cũ bằng0
- Giữ residual ứng với các lớp vừa xuất hiện

**Ghi chú thuyết trình:** PLC áp đặt cấu trúc nhãn disjoint vào nhánh bù. Nếu không PLC, dữ liệu lớp mới tạo mục tiêu âm trên các cột cũ thông qua head chính. Bài báo cho thấy lợi ích thực nghiệm của việc loại thành phần này. Mục tiêu không phải làm các trọng số head cũ bất động.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 19. Kết hợp hai nhánh

- scores = X_M W_M + C X_C W_C
- Chọn lớp có score lớn nhất
- C điều khiển mức độ bù

**Ghi chú thuyết trình:** Đầu ra ridge là score không chuẩn hóa, không tự diễn giải như xác suất calibrated. Paper dùng C0.6 trên CIFAR-100,0.8 trên ImageNet-100,1.4 trên ImageNet-Full. Dự án dùng C0.6 cho thiết lập chính CIFAR, quét C chỉ là phân tích bổ sung.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 20. Chi phí lưu trữ và tính toán

- Thống kê: O(m²)
- Head: O(mc), phép chiếu: O(dm)
- Hai ma trận8192² float64: 1 GiB

**Ghi chú thuyết trình:** Bộ nhớ không tăng theo số mẫu lịch sử khi m và c cố định, nhưng head vẫn tăng theo số lớp. RLS và stats có chi phí tính khác. Phải tách chi phí CNN, feature cache, fit và suy luận. Con số1GiB chỉ gồm hai ma trận, không phải tổng RAM cần dùng.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 21. Thước đo đánh giá

- A_k: accuracy trên các lớp đã gặp ở pha k
- A-bar: trung bình A_0 đến A_K
- A_K: accuracy sau pha cuối

**Ghi chú thuyết trình:** Trung bình gồm K+1 giá trị. Khi K thay đổi, các tập đánh giá trung gian thay đổi. Vì vậy so sánh A_K phù hợp hơn khi kiểm tra hệ quả của cùng trọng số cuối; A-bar vẫn hữu ích để mô tả toàn tiến trình.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 22. Kết quả công bố trên CIFAR-100


**Ghi chú thuyết trình:** Đây là số tác giả từ Table1 với ResNet-32. Không trộn với hàng trong ngoặc dùng ResNet-18. DS-AL cải thiện nhỏ so với ACIL ở CIFAR, nên phải thận trọng trước độ biến thiên seed và các khác biệt cấu hình. Bảng chưa chứa số đo nhóm.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 23. Phạm vi tái hiện của nhóm

- Core trên CIFAR-100 / ResNet-32
- So sánh chính và DAC/PLC ablation
- Thêm khảo sát K và chiều buffer

**Ghi chú thuyết trình:** Nhóm ưu tiên tự triển khai và bằng chứng có thể truy vết với RTX4050 6GB, RAM16GB. Ablation gốc dùng ImageNet-Full, còn nhóm chuyển sang CIFAR và phải nêu rõ thay đổi. Không tuyên bố tái hiện toàn bộ SOTA, ImageNet hoặc500 pha.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning.

## 24. Kiểm tra bản tự triển khai

- RLS và stats đối chiếu nghiệm ridge trực tiếp
- Kiểm tra padding nhãn, PLC và kích thước batch
- Đối chiếu đầu ra với checkout tác giả cô lập

**Ghi chú thuyết trình:** Tests kiểm tra các hợp đồng toán học thay vì chỉ chạy không lỗi. Checkout tác giả không được đưa vào src. Dữ liệu đối chiếu nhỏ dùng cùng phép chiếu để không quy sai khác do khởi tạo thành lỗi thuật toán. Kết quả cụ thể nằm trong comparison.json.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning.

## 25. Protocol và truy vết kết quả

- Revision dữ liệu, class order, seed và hash checkpoint
- W&B run riêng cho từng thí nghiệm
- Ghi solver, dtype, versions và thời gian

**Ghi chú thuyết trình:** Từng con số cần nguồn thực đo. Cache feature phải khớp checkpoint và preprocessing. Không chọn checkpoint hoặc siêu tham số theo test tốt nhất. Run offline là số đo cục bộ thật nhưng cần đồng bộ công khai trước khi nộp.

**Nguồn tại chân slide:**

## 26. Kết quả tái hiện đo được

- Bảng tự cập nhật từ run hoàn tất
- Smoke test được loại khỏi bảng đối sánh paper

**Ghi chú thuyết trình:** Renderer đọc experiments/reproduction/results.json, chỉ lấy run cấu hình đầy đủ khi so paper. Nếu chưa có run hoàn tất, hiển thị rõ chưa hoàn tất. Không điền số ước tính. Mỗi hàng cần W&B URL trước khi đủ điều kiện nộp.

**Nguồn tại chân slide:**

## 27. Đóng góp của DAC và PLC

- So sánh ba biến thể trên cùng backbone
- Giữ seed và projection trong cặp đối sánh
- Báo cả A-bar lẫn A_K

**Ghi chú thuyết trình:** RLS-only là baseline ACIL về cấu trúc head của triển khai nhóm. DAC không PLC và DS-AL đầy đủ giúp tách tác động hai thành phần. Khi chưa đủ ba run hoàn tất, không khẳng định một thành phần cải thiện accuracy.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 28. Ảnh hưởng của số pha và buffer

- K5/25/50 với cùng backbone và projection
- m512/1024/2048/8192
- Accuracy cùng fit time và bộ nhớ

**Ghi chú thuyết trình:** Đây là các phép đo bổ sung. Khi xét K, phân biệt biến động trọng số cuối, accuracy cuối và A-bar. Khi xét m, không kết luận từ timing đã lẫn base training. Phép chiếu theo seed cố định vẫn có thể không tạo các cột lồng nhau ở các m khác nhau; lưu config để không phóng đại tính paired.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670.

## 29. Phân tích sai lệch với bài báo

- Backbone, class order và random projection
- Supplement C so với README mã tác giả hiện tại
- Solver và thời điểm tạo residual

**Ghi chú thuyết trình:** Tách sai lệch có bằng chứng với giả thuyết chưa đo. Tính khoảng cách theo điểm phần trăm và độ lệch tương đối chỉ khi protocol đủ điều kiện đối sánh. Một seed chưa cho phép kết luận về độ biến thiên ba lần chạy. So sánh batch của mã gốc cho thấy sự khác biệt ngữ nghĩa cần công khai.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning.

## 30. Phạm vi kết luận hiện tại

- Bảo đảm toán học có điều kiện rõ
- Kết quả benchmark chỉ kết luận khi run hoàn tất
- Phản biện lý thuyết gắn với thí nghiệm cơ chế

**Ghi chú thuyết trình:** Nội dung kết thúc bằng phạm vi bằng chứng thực sự có. Lab2 có các kiểm chứng cơ chế trên dữ liệu tổng hợp và phải ghi rõ điều đó. Việc hiểu được giới hạn bảo đảm giúp nhóm trả lời vấn đáp và thiết kế mở rộng, không phải thay thế cho tái hiện benchmark.

**Nguồn tại chân slide:** [1] H. Zhuang et al., DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning, AAAI, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. [2] H. Zhuang et al., Supplementary Material for DS-AL, Sections A–C, 2024, github.com/ZHUANGHP/Analytic-continual-learning.
