# Nội dung và speaker notes v2

## 01. DS-AL
Đọc hiểu, tự triển khai và tái hiện trên CIFAR-100

Nhóm gồm Lâm Hoàng Vũ – 23122056, Nguyễn Bá Nam – 23122043, Chung Tín Đạt – 23122024 nghiên cứu DS-AL của Zhuang và cộng sự tại AAAI 2024. Bộ slide trình bày phương pháp bằng ký hiệu thống nhất, sau đó kiểm chứng bằng triển khai độc lập và thực nghiệm thật. Chọn Core scope vì máy có RTX 4050 6 GB và RAM 16 GB, trong khi bài báo còn đánh giá ImageNet. Toàn bộ benchmark ở đây là seed 0 trên CPU. Những kết quả từ bài báo, số đo của nhóm và suy luận của nhóm được gắn nhãn riêng. Bộ slide là sản phẩm đọc hiểu và tái hiện, không tuyên bố tái hiện toàn bộ SOTA. Chuyển sang tình huống cần học lớp mới mà vẫn nhận ra lớp cũ.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670

## 02. Học thêm lớp, vẫn nhận ra lớp cũ
Bộ phân loại phải xử lý tất cả các lớp đã gặp

Ví dụ minh họa do nhóm xây dựng: hệ thống nhận diện động vật học chó và mèo, sau đó học chim và cá. Ở pha sau, đầu vào vẫn có thể là ảnh mèo. Không có task ID cho biết ảnh đến từ giai đoạn nào. Vì thế bài toán là phân loại trên hợp các lớp đã gặp, không phải chọn một head riêng khi đã biết nhiệm vụ. Lịch sử này mô tả vấn đề chứ không phải một kết quả thực nghiệm. Các thí nghiệm thật dùng CIFAR-100 với 50 lớp base. Điều quan trọng ở đây là thay đổi không gian nhãn và sự cạnh tranh giữa lớp cũ với lớp mới.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670

## 03. Exemplar-free và replay
DS-AL giữ trạng thái đại số thay cho ảnh replay

Replay lưu một phần dữ liệu cũ rồi trộn với dữ liệu mới. Điều đó hỗ trợ cập nhật biểu diễn, nhưng cần ngân sách exemplar và quyền lưu dữ liệu. DS-AL giữ backbone cố định, phép chiếu, head và ma trận thống kê, không cần replay ảnh cũ trong bước học tăng dần. Tuy nhiên, lưu thống kê không phải một chứng minh differential privacy và không có nghĩa mọi thông tin về dữ liệu bị xóa. Trong triển khai phục vụ kiểm chứng, dataset và feature cache vẫn có trên đĩa để đánh giá; lời khẳng định exemplar-free chỉ áp dụng việc fit mỗi pha không lấy mẫu cũ trở lại.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[5] S.-A. Rebuffi, A. Kolesnikov, G. Sperl, and C. H. Lampert, “iCaRL: Incremental Classifier and Representation Learning,” CVPR, pp. 2001–2010, 2017. https://openaccess.thecvf.com/content_cvpr_2017/html/Rebuffi_iCaRL_Incremental_Classifier_CVPR_2017_paper.html

## 04. Từ distillation đến analytic learning
Mỗi hướng giải quyết một phần của bài toán

LwF dùng distillation trên dữ liệu mới để giữ hành vi cũ. Khi dữ liệu pha mới không đại diện cho dữ liệu cũ, ràng buộc này có thể không giữ đủ khả năng phân biệt, nên cần cân bằng hai mục tiêu. iCaRL sử dụng exemplar để hỗ trợ phân loại và học biểu diễn, nhưng yêu cầu lưu dữ liệu cũ. ACIL giữ đặc trưng cố định và nghiệm ridge qua thống kê, nên tránh cập nhật gây lệch nghiệm head; hạn chế là năng lực biểu diễn của một ánh xạ tuyến tính trong embedding mở rộng. Đây là hạn chế mà DS-AL nhắm đến bằng nhánh bù. Các mô tả là phân tích cơ chế, không phải thứ hạng từ một benchmark mà nhóm chưa chạy.

[3] H. Zhuang et al., “ACIL: Analytic Class-Incremental Learning with Absolute Memorization and Privacy Protection,” Advances in Neural Information Processing Systems, vol. 35, pp. 11602–11614, 2022. https://proceedings.neurips.cc/paper_files/paper/2022/hash/4b74a42fc81fc7ee252f6bcb6e26c8be-Abstract.html
[4] Z. Li and D. Hoiem, “Learning without Forgetting,” IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 40, no. 12, pp. 2935–2947, 2018, doi:10.1109/TPAMI.2017.2773081. https://doi.org/10.1109/TPAMI.2017.2773081
[5] S.-A. Rebuffi, A. Kolesnikov, G. Sperl, and C. H. Lampert, “iCaRL: Incremental Classifier and Representation Learning,” CVPR, pp. 2001–2010, 2017. https://openaccess.thecvf.com/content_cvpr_2017/html/Rebuffi_iCaRL_Incremental_Classifier_CVPR_2017_paper.html

## 05. Khoảng trống và đóng góp
Thêm khả năng khớp mà vẫn giữ cấu trúc cập nhật đại số

Bài báo nêu ba loại đóng góp. Về lý thuyết, C-RLS cho nhánh chính trùng nghiệm ridge học gộp khi thỏa điều kiện. Về kỹ thuật, DAC học phần dư với activation bổ sung, còn PLC áp cấu trúc lớp mới vào mục tiêu bù. Về thực nghiệm, tác giả đánh giá trên CIFAR-100 và ImageNet với các số pha khác nhau. Ba đóng góp có mức độ bảo đảm khác nhau: định lý của head chính là đẳng thức toán học, còn tăng accuracy nhờ nhánh bù là kết quả thực nghiệm. Không suy ra nhánh bù luôn giúp mọi dữ liệu. Triển khai và ablation của nhóm sẽ kiểm tra cụ thể điều đó.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670

## 06. Kiến trúc tổng thể DS-AL
Đóng băng biểu diễn, cập nhật hai head rồi cộng điểm

Ảnh đi qua CNN đã huấn luyện trên lớp base. Đầu ra 64 chiều của ResNet-32 được mở rộng bằng phép chiếu cố định B. Cùng một Z tạo hai embedding: ReLU cho main stream và tanh cho compensation stream. Main stream học nhãn one-hot, sau đó tạo residual cho nhánh bù. Pha mới dùng PLC trước khi cập nhật compensation head. Khi dự đoán, cộng score của nhánh chính với C lần score nhánh bù rồi lấy argmax. Luồng tạo nhãn bù chỉ tồn tại khi huấn luyện và được vẽ riêng với luồng suy luận. Hình do nhóm dựng lại từ mô tả và Algorithm 1–2, không dùng hình tác giả.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 07. Protocol CIFAR-100 B50
50 lớp base, 50 lớp mới chia đều qua K pha

CIFAR-100 có 50.000 ảnh train và 10.000 ảnh test. Sau khi remap theo class order, 50 lớp đầu chỉ dùng để huấn luyện backbone. Phần còn lại chia thành K pha disjoint. Với K=5, mỗi pha thêm 10 lớp; K=25 thêm 2 lớp; K=50 thêm 1 lớp. Mỗi pha đánh giá trên tất cả lớp đã gặp với test split cố định, không cung cấp task ID. Backbone không cập nhật trong analytic learning. Nhóm dùng checkpoint epoch cuối thay vì chọn checkpoint có test accuracy tốt nhất. Dataset tải bằng mã từ Hugging Face và lưu revision cụ thể.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 08. Ký hiệu và kích thước
X là embedding theo hàng mẫu, W mở rộng theo số lớp

Tại pha k, n_k là số mẫu hiện tại, c_k là tổng số lớp đã gặp, d là chiều feature backbone và m là chiều buffer. X_M,k và X_C,k đều có n_k hàng, m cột. Y_k là one-hot đã đặt vào hệ chỉ số nhãn toàn cục, có c_k cột. W_M,k và W_C,k có m hàng, c_k cột. R là nghịch đảo tương quan kích thước m×m. K là số pha tăng dần sau pha base, nên có K+1 lần đánh giá. Gamma điều chuẩn ridge, C là hệ số hợp nhất score. Dùng chỉ số này xuyên suốt để tránh nhầm số lớp của riêng pha với số lớp tích lũy.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670

## 09. Backbone học một lần trên lớp base
160 epoch hoàn tất, checkpoint cuối được giữ cố định

Đường cong là log huấn luyện thật của nhóm trên 50 lớp base, không phải accuracy cuối trên đủ 100 lớp. ResNet-32 dùng SGD, momentum 0,9, batch 128, learning rate 0,1 và weight decay 5e-4. Scheduler giảm learning rate tại epoch 80 và 120, phù hợp Supplement C. Augmentation crop và flip chỉ dùng lúc huấn luyện backbone. Khi kết thúc epoch 160, test accuracy trên lớp base là 76,92%. Đây là checkpoint cuối chứ không chọn đỉnh đường cong theo test set. Thực nghiệm chạy CPU với PyTorch 2.5.1+cpu; không đối chiếu tốc độ với RTX 3090 của tác giả.

[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning
[6] K. He, X. Zhang, S. Ren, and J. Sun, “Deep Residual Learning for Image Recognition,” CVPR, pp. 770–778, 2016. https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html
base-training: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/zuc29egg

## 10. Một phép chiếu, hai embedding
ReLU và tanh tạo hai không gian đặc trưng bổ sung

Buffer ở đây là phép mở rộng feature ngẫu nhiên, không phải replay buffer. Triển khai lấy B từ phân phối chuẩn với độ lệch chuẩn 1, không bias, seed cố định. Z=f(x)B đi vào cả hai activation. Nhánh chính dùng ReLU, nhánh bù dùng tanh theo cấu hình CIFAR-100 trong paper. Đồ thị ReLU/tanh chỉ minh họa định nghĩa toán học, không phải đo trên dataset. Hai activation khác nhau làm tăng lớp hàm score có thể biểu diễn. Việc tăng lớp hàm chưa bảo đảm tăng accuracy kiểm tra. Khác biệt phân phối projection chưa được PDF mô tả đầy đủ là một giả thuyết cần kiểm chứng khi phân tích gap.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 11. Ridge regression của nhánh chính
Cân bằng độ khớp nhãn và độ lớn trọng số

Mục tiêu là tối thiểu hóa tổng bình phương sai số giữa Y và XW cộng gamma lần bình phương Frobenius của W. Gamma dương làm ma trận XᵀX+gamma I xác định dương, cho nghiệm duy nhất ngay cả khi feature thiếu hạng. Nhánh chính tuyến tính trong embedding, nhưng pipeline từ pixel đã phi tuyến nhờ CNN và ReLU. Công thức nghịch đảo diễn đạt nghiệm; mã dùng Cholesky solve để tránh tính nghịch đảo tường minh trong chế độ stats. Gamma được cộng đúng một lần cho mục tiêu tích lũy. Đây là nền tảng để xem học tăng dần như cập nhật thống kê của cùng một bài toán ridge.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670

## 12. Padding khi xuất hiện lớp mới
Giữ các cột cũ và thêm cột 0 đúng hệ chỉ số nhãn

Minh họa dùng hai lớp cũ và hai lớp mới, không phải giá trị thực nghiệm. Khi tổng lớp tăng từ hai lên bốn, head cũ được thêm hai cột 0. Nhãn của dữ liệu mới có bốn cột, với phần cũ bằng 0. Đồng thời cross-correlation của dữ liệu quá khứ được padding 0 cho các lớp chưa xuất hiện lúc đó. Nếu one-hot chỉ chứa các lớp trong minibatch mà không remap về nhãn toàn cục, các cột bị trùng ý nghĩa và định lý không còn áp dụng. Padding chỉ là bước chuẩn bị; cập nhật tiếp theo vẫn có thể thay đổi score lớp cũ.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670

## 13. C-RLS cập nhật nghiệm ridge
Gain Lₖ truyền sai số pha hiện tại vào head đã padding

L_k là gain kích thước m×n_k, không phải learning rate tối ưu gradient. Trước tiên tính gain từ R cũ và embedding pha hiện tại. Sau đó cập nhật R và head đã padding bằng residual với head trước cập nhật. Công thức dùng L_k tương đương Eq. 11 vì Supplement A.11 chứng minh L_k=R_k X_kᵀ. Nghịch đảo ở đây có kích thước minibatch, trong khi chế độ stats giải hệ m×m ở cuối pha. Điều kiện ban đầu có thể viết R trước dữ liệu bằng gamma⁻¹I. Bản minh họa đã thống nhất Y_k là nhãn toàn cục n_k×c_k, tránh nhầm kích thước trong ký hiệu gốc.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 14. Vì sao C-RLS bằng học gộp?
Thống kê cộng dồn giữ cùng một hệ phương trình chuẩn

Đặt G_k=gamma I+ tổng các X_iᵀX_i và Q_k là tổng cross-correlation X_iᵀY_i đã padding. Khi đó W_k=G_k⁻¹Q_k. Thêm pha chỉ cộng vào G và Q; không cần đọc lại mẫu cũ. Dùng Woodbury cho G_k⁻¹ thu được cập nhật R. Sau đó thế Q đã padding và dùng L_k=R_k X_kᵀ sẽ thu được Eq. 11. Phép cộng thống kê không phụ thuộc cách chia nhóm trong số học chính xác. Trên máy tính, thứ tự cộng và giải hệ có sai số làm tròn, vì thế kiểm tra dùng tolerance. Phác thảo này trình bày ý chính của Supplement A, không chép toàn bộ chứng minh.

[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 15. Phạm vi của Theorem 1
Tương đương nghiệm head chính có điều kiện

Bảo đảm cần backbone, phép chiếu và activation chính cố định, gamma cố định, padding đúng và cập nhật đủ dữ liệu. Đó là tương đương với ridge học gộp trên cùng feature, không phải tương đương huấn luyện joint CNN trên tất cả ảnh. Accuracy lớp cũ vẫn có thể giảm vì lớp mới cạnh tranh và vì biểu diễn được học chủ yếu trên base. Residual của DAC được tạo ở từng thời điểm khác nhau, nên không tự suy ra toàn bộ DS-AL bất biến chính xác theo phân hoạch pha. Các test số học xác nhận main head ở tolerance đã nêu; chúng không thay thế chứng minh hoặc benchmark rộng.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 16. RLS và sufficient statistics
Cùng objective, khác cách giải và chi phí tính toán

Nhóm triển khai cả Woodbury RLS và stats. RLS duy trì R rồi cập nhật qua batch; stats duy trì G=gamma I+XᵀX cùng Q=XᵀY rồi giải Cholesky khi kết thúc pha. Benchmark seed 0 dùng stats, float64. Vì thế thời gian đo không thể nhận là runtime của công thức RLS trong paper. Test đối chiếu hai solver và nghiệm joint ridge cho thấy chúng giải cùng objective trong sai số cho phép. Với batch b, RLS có các thành phần O(m²b+mb²+b³). Stats tích lũy khoảng O(Nm²) rồi giải O(m³) mỗi lần finalize. Đây là bậc chi phí chính khi số lớp và chiều backbone nhỏ hơn m; còn có tích XᵀY, projection và giải nhiều vế phải. Các công thức là phân tích toán học, không phải profiling RAM/CPU.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670

## 17. DAC học phần dư sau toàn bộ pha
Hoàn tất main stream trước khi tạo nhãn bù

Ở pha k, nhóm cập nhật main head bằng toàn bộ dữ liệu pha hiện tại rồi mới tạo E_k=Y_k-X_M,k W_M,k. Nhánh bù dùng activation khác và học E_k bằng ridge. Không recompute mục tiêu cũ khi sang pha sau; lịch sử residual vì thế là một phần của cơ chế DAC. Nếu tạo residual ngay sau từng minibatch, head chính chưa phải nghiệm cuối của pha và kết quả sẽ phụ thuộc chunk size. Đây là vị trí mà nhóm đối chiếu với mã tác giả trên đầu vào nhỏ. Các vector minh họa trên slide là phép tính giáo dục, không phải một sample test đã được log.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 18. PLC trước và sau làm sạch nhãn
Đặt phần residual của lớp cũ bằng 0 ở pha mới

Ví dụ giả định có hai lớp cũ và hai lớp mới. Nhãn one-hot của mẫu mới bằng 0 trên các cột cũ. Dự đoán của main head thường khác 0 ở các cột đó, nên residual cũ là số âm. PLC thay đúng hai cột cũ bằng 0 và giữ nguyên phần residual mới, kể cả phần tử âm trong những cột mới không phải lớp đúng. Pha base không áp PLC. Đây là điều kiện cấu trúc nhãn, không phải đóng băng trọng số cũ hoặc bảo đảm điểm lớp cũ bất biến. Ví dụ được tính lại từng ô để người đọc thấy tác dụng mà một ma trận toàn 0 sẽ không thể hiện.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 19. Hợp nhất hai nhánh khi dự đoán
C điều khiển đóng góp của compensation score

Điểm dự đoán bằng X_M W_M cộng C X_C W_C. Chọn lớp bằng argmax trên tất cả cột đã gặp. Score ridge không mặc nhiên là xác suất đã hiệu chỉnh, nên không gọi các giá trị trong sơ đồ là confidence được calibrated. C càng lớn thì đóng góp nhánh bù càng lớn, nhưng tính chính xác có thể tăng hoặc giảm tùy cân bằng lớp cũ và mới. Paper dùng C=0,6 cho CIFAR-100, 0,8 cho ImageNet-100, 1,4 cho ImageNet-Full. Nhóm giữ 0,6 trong suite CIFAR để đối sánh. Chưa chạy grid search của riêng nhóm và không chọn C từ test tốt nhất.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670

## 20. Bộ nhớ trạng thái và chi phí thực tế
Hai ma trận FP64 tại m=8192 chiếm đúng 1 GiB

Số 1 GiB được tính từ 2×8192²×8 byte, chỉ gồm hai ma trận tương quan hoặc nghịch đảo tương quan. Nó không phải tổng RAM đo khi chạy. Với cùng m và FP64, ACIL cần một ma trận này, 512 MiB; DS-AL cần hai. Replay còn cần O(M lần kích thước ảnh) cho M exemplar và có thể huấn luyện lại CNN; không có một runtime chung cho mọi phương pháp replay. Với m và số lớp c cố định, trạng thái không tăng theo số mẫu lịch sử, nhưng head vẫn tăng theo c với O(mc). Phép chiếu có O(dm). Workspace Cholesky, cross-correlation, head, backbone và feature cache làm RAM thực tế lớn hơn. Nhóm không có phép đo peak RAM đủ tin cậy cho suite CPU, nên không tạo đường cong RAM đo. Thời gian fit báo riêng từ log, không gộp thời gian huấn luyện CNN.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[3] H. Zhuang et al., “ACIL: Analytic Class-Incremental Learning with Absolute Memorization and Privacy Protection,” Advances in Neural Information Processing Systems, vol. 35, pp. 11602–11614, 2022. https://proceedings.neurips.cc/paper_files/paper/2022/hash/4b74a42fc81fc7ee252f6bcb6e26c8be-Abstract.html
[5] S.-A. Rebuffi, A. Kolesnikov, G. Sperl, and C. H. Lampert, “iCaRL: Incremental Classifier and Representation Learning,” CVPR, pp. 2001–2010, 2017. https://openaccess.thecvf.com/content_cvpr_2017/html/Rebuffi_iCaRL_Incremental_Classifier_CVPR_2017_paper.html

## 21. Hai thước đo, hai góc nhìn
A-bar mô tả tiến trình, A_K mô tả trạng thái cuối

A_k là phần trăm phân loại đúng trên các lớp đã gặp ở pha k. A-bar lấy trung bình K+1 giá trị, bao gồm pha base. A_K là accuracy ở pha cuối sau khi học đủ 100 lớp. Đường cong minh họa lấy từ DS-AL K=5 của nhóm; test set mở rộng từ 50 đến 100 lớp nên accuracy giảm không thể đọc đơn giản là quên hoàn toàn lớp cũ. Khi so K=5 với K=50, A-bar còn thay đổi vì số điểm và tập lớp ở thời điểm trung gian khác nhau. Vì vậy cần nhìn đồng thời A_K và A-bar.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 22. Phạm vi tái hiện: Core scope
E1 đối sánh chính, E2 ablation chuyển dataset, E3 khảo sát buffer

Phạm vi thực nghiệm gồm E1 đối sánh ACIL với DS-AL trên CIFAR-100 B50, tương ứng phần CIFAR-100 ResNet-32 của Table 1. E2 kiểm tra cơ chế DAC/PLC bằng cách chuyển thí nghiệm ablation từ ImageNet-Full với C=1,4 trong Table 2 sang CIFAR-100 với C=0,6. Vì dataset, backbone và hệ số C thay đổi, E2 không phải tái hiện nguyên Table 2. Chưa có bằng chứng giảng viên đã chấp nhận phạm vi chuyển này. Kết quả E2 chỉ diễn giải trong protocol CIFAR đã nêu. E3 do nhóm thiết kế để khảo sát accuracy và thời gian fit khi thay chiều buffer trên cùng feature cache. Benchmark nhóm hiện chỉ có seed 0; không dùng các seed tổng hợp để thay thế benchmark nhiều seed.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 23. Thiết lập và khả năng tái lập
Giữ cùng backbone, dữ liệu và seed giữa các biến thể

Dataset tải từ uoft-cs/cifar100 trên Hugging Face, revision được pin trong feature identity. Class order là permutation 100 lớp của NumPy RandomState(0). Suite dùng cùng feature cache và checkpoint SHA-256; gamma=0,1, tanh, C=0,6, projection chuẩn không bias. Phiên bản khi thực nghiệm là Python 3.11.8, torch 2.5.1+cpu, torchvision 0.20.1+cpu và W&B 0.23.1. SDK hiện dùng để đọc/sync là 0.31.0, không gán nó thành phiên bản đã chạy benchmark. Chỉ có seed 0 cho CIFAR; các thí nghiệm tổng hợp ba seed là bộ bằng chứng khác.

[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 24. Nhóm tự triển khai và kiểm tra gì?
11 kiểm thử đạt, gồm hợp đồng toán học và tính toàn vẹn

Core nằm trong AnalyticRidge và DualStreamAnalytic, độc lập với mã tác giả. Các test xác nhận hai solver bằng nghiệm joint ridge khi mở rộng nhãn; mục tiêu compensation dùng main head cuối pha và PLC; chunk size không đổi ngữ nghĩa pha; dữ liệu vi phạm disjoint bị từ chối; checkpoint resume khôi phục chính xác quỹ đạo. Các test sync bổ sung bảo vệ file gốc và chặn remote ID collision. Kết quả 11 passed được chạy lại trong đợt kiểm tra này. Tái sử dụng torch, torchvision và bộ nạp dữ liệu là thành phần hỗ trợ được ghi nhận. Đối chiếu mã tác giả là kiểm chứng riêng, không dùng code đó trong benchmark.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 25. Điều kiện đối sánh giữa các biến thể
Dùng chung biểu diễn và protocol, thay đổi thành phần đang kiểm tra

Các phép đối sánh của nhóm dùng cùng CIFAR-100, checkpoint ResNet-32, class order và seed 0. Vì vậy mỗi cặp có thể tập trung vào thành phần đang kiểm tra. E1 so ACIL với DS-AL đầy đủ. E2 so ACIL, DAC không PLC và DAC có PLC, nhằm tách đóng góp của nhánh bù và bước làm sạch nhãn trong protocol CIFAR. Khảo sát số pha thay K=5/25/50, còn khảo sát buffer thay m=512/1024/2048/8192 với K=5. Gamma, C, activation và solver của khảo sát buffer giữ cố định. Khi thay m, projection dùng cùng seed nhưng các ma trận không lồng nhau; vì thế quan sát cũng chịu ảnh hưởng của một realization projection. Đây là thiết kế ghép cặp trong một seed, chưa là ước lượng biến thiên giữa các seed.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning
base-training: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/zuc29egg
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 26. Kết quả gốc trên CIFAR-100
DS-AL: ResNet-32, mean ± std từ 3 lần chạy

Bảng này là kết quả của tác giả, không phải của nhóm. Đã đối chiếu trực quan Table 1, chỉ lấy hàng CIFAR-100 ResNet-32, không lấy các giá trị trong ngoặc của ResNet-18. Với DS-AL, paper nêu mean và standard deviation của ba lần chạy; các con số 58,26/58,32/58,37 là A_K cho K=5/25/50. A-bar tương ứng là 66,39/66,20/66,33. ACIL là baseline trong cùng bảng. Đây là nguồn đối sánh E1; ablation Table 2 của paper dùng ImageNet-Full nên không trộn vào bảng CIFAR của nhóm.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 27. Paper và tái hiện trên cùng protocol CIFAR
DS-AL seed 0 đạt A_K = 56,87%

Đối sánh dùng CIFAR-100 B50, ResNet-32, K=5, buffer 8192, gamma 0,1 và C 0,6 cho DS-AL. ACIL của nhóm đạt A-bar 65,7880%, A_K 56,56%; DS-AL đạt 65,8219% và 56,87%. Paper tương ứng 66,30/57,78 cho ACIL và 66,39/58,26 cho DS-AL. Các thanh đồ thị bắt đầu từ 0 để không phóng đại chênh lệch. Nhóm chỉ chạy một seed, trong khi paper lấy mean ba run. Vì vậy kết quả gần về protocol nhưng chưa chứng minh tái hiện đúng phân phối thống kê. Các URL đầy đủ dẫn đến run tương ứng, không dùng nhãn “đã có URL”.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
acil-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/h2sljkd5
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 28. Định lượng sai lệch ở pha cuối
Khoảng cách DS-AL là −1,39 điểm phần trăm

Delta tuyệt đối theo điểm phần trăm bằng kết quả nhóm trừ paper. Độ lệch tương đối bằng 100×(nhóm−paper)/paper. ACIL: 56,56−57,78=−1,22 pp, tương đối khoảng −2,11%. DS-AL: 56,87−58,26=−1,39 pp, tương đối khoảng −2,39%. A-bar của ACIL thấp hơn khoảng 0,512 pp, DS-AL khoảng 0,568 pp. Không gọi chênh lệch 1,39 pp là giảm 1,39% tương đối. Những giá trị này mô tả khoảng cách của seed 0; chúng không xác định nguyên nhân. Phần thảo luận sau tách khác biệt đã kiểm tra khỏi các giả thuyết cần chạy thêm.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
acil-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/h2sljkd5
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 29. Ablation DAC và PLC
E2: CIFAR-100, seed 0; chuyển từ ImageNet-Full, không tái hiện nguyên Table 2

Tất cả biến thể dùng cùng backbone, feature cache, class order, projection seed và gamma. Khi thêm DAC nhưng không PLC, A_K từ 56,56 giảm xuống 56,24, chênh −0,32 pp. Khi bật PLC, A_K tăng từ 56,24 lên 56,87, tức +0,63 pp. DS-AL đầy đủ hơn ACIL +0,31 pp ở pha cuối, nhưng A-bar chỉ hơn khoảng 0,034 pp. Dữ liệu hỗ trợ nhận định PLC hữu ích trong cấu hình này, không cho phép khẳng định DAC đơn lẻ luôn cải thiện. Thí nghiệm là bản ablation chuyển từ ImageNet-Full sang CIFAR, không phải các giá trị Table 2 của tác giả. Một seed chưa có kiểm định ý nghĩa thống kê. E2 là bản chuyển dataset từ ImageNet-Full/C=1,4 của paper sang CIFAR-100/C=0,6; không suy ra mức tác dụng PLC trên ImageNet. Không có thông tin xác nhận giảng viên đã chấp nhận phạm vi này.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
acil-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/h2sljkd5
dac-no-plc-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/gpx1ehdu
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 30. Accuracy theo từng pha tăng dần
CIFAR-100, seed 0; màu, kiểu nét và marker phân biệt ba biến thể

Đường cong vẽ accuracy trên các lớp đã gặp ở mỗi pha, lấy trực tiếp từ phases.json. Cả ba biến thể dùng cùng protocol K=5. Ở pha cuối, ACIL có base accuracy 69,56% và novel accuracy 43,56%; DS-AL có 67,58% và 46,16%. Vì base và novel đều có 5.000 ảnh test, trung bình hai giá trị bằng accuracy tổng. DS-AL tăng novel +2,60 pp đồng thời giảm base −1,98 pp, tạo lợi ích tổng +0,31 pp. Đây phù hợp cơ chế đánh đổi stability/plasticity của paper, nhưng chỉ là mô tả của seed 0 và chưa chứng minh tổng quát. Không so hai nhóm có số ảnh khác nhau mà bỏ qua trọng số. Biểu đồ v2 dùng trục accuracy 50–80% để phân biệt tiến trình, được ghi rõ trên slide. Các đường có màu, marker và kiểu nét khác nhau. Bảng pha cuối giữ nguyên giá trị chính xác đã đo. Phóng trục không thêm quan sát và không xác lập ý nghĩa thống kê.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
acil-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/h2sljkd5
dac-no-plc-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/gpx1ehdu
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 31. Khảo sát số pha K
A_K dao động 0,04 pp khi K thay đổi từ 5 tới 50

Dùng cùng backbone và cùng phép chiếu ở seed 0, K=5/25/50 cho A_K lần lượt 56,87/56,83/56,87%. A-bar tương ứng 65,8219/65,5433/65,5361%. Đường cong cuối gần nhau hỗ trợ quan sát ổn định ở cấu hình này. Tuy nhiên, khác biệt 0,04 pp không chứng minh head bù hoặc score bất biến chính xác theo pha. Thay K còn làm thay đổi các điểm đánh giá trung gian nên A-bar cần diễn giải thận trọng. Paper khảo sát tới K=500 trên ImageNet-Full, còn đây là mở rộng vừa sức trên CIFAR-100. Không ghi đã tái hiện thí nghiệm 500 pha.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme
dsal-k25: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/c0niqv2k
dsal-k50: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/mb9xncbl

## 32. Phân tích tự thiết kế: chiều buffer
Đánh đổi accuracy với thời gian fit khi thay m

Câu hỏi là giảm chiều buffer tiết kiệm bao nhiêu thời gian và phải đánh đổi accuracy thế nào trên cùng feature CIFAR-100. Đây là khảo sát nhóm khai báo trong suite, không phải sao chép một bảng m tương ứng của DS-AL. Giả thuyết làm việc là m lớn tăng năng lực biểu diễn nhưng tăng chi phí tính toán; đây là giả thuyết trước diễn giải kết quả, không phải định lý về accuracy. Giữ dữ liệu, backbone, thứ tự lớp, seed, gamma, C, activation và solver; thay m trong 512/1024/2048/8192. Các ma trận projection cùng seed nhưng khác shape không lồng nhau, nên hiệu ứng còn có thể chứa khác biệt hiện thực hóa ngẫu nhiên. Cần nhiều seed để tách yếu tố đó.

buffer-512: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/k64nfaxk
buffer-1024: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/ec7ki95r
buffer-2048: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/rugifzey
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 33. Accuracy và thời gian theo buffer
Seed 0, 512 → 8192: +5,41 pp accuracy, thời gian fit ×96,0

Bảng kết hợp các giá trị thực đo: m=512/1024/2048/8192 có A_K 51,46/53,36/54,97/56,87%. Thời gian fit lần lượt khoảng 0,901/1,672/5,177/86,513 giây, cộng trên sáu pha và không gồm base training, trích feature hay logging. Không thay bằng elapsed_seconds vì chỉ số đó bao gồm chi phí khác. Xu hướng accuracy tăng trong bốn cấu hình này phù hợp giả thuyết về capacity, nhưng chưa bảo đảm tính đơn điệu cho seed hoặc dataset khác. Runtime còn phụ thuộc máy CPU và tải hệ thống; không so với thời gian GPU của paper. Không có số đo peak RAM, vì vậy chỉ báo accuracy/time thực đo trên slide này. Hai biểu đồ dùng cùng thứ tự chiều buffer và hai đơn vị riêng: accuracy (%) và thời gian fit (s). Hai trục cột đều bắt đầu từ 0. Bảng giữ giá trị fit đến ba chữ số thập phân và accuracy đến hai chữ số. Tỷ số thời gian và chênh lệch pp được tính từ số đo chưa làm tròn; đây là thống kê mô tả một seed trên CPU này, không phải khẳng định độ phức tạp thực nghiệm trên mọi máy.

buffer-512: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/k64nfaxk
buffer-1024: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/ec7ki95r
buffer-2048: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/rugifzey
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 34. Đã biết gì về reproduction gap?
Phân biệt khác biệt đã thấy và nguyên nhân chưa được đo

Đã xác minh: paper dùng mean ba run trên RTX 3090, nhóm có một seed CPU; benchmark dùng stats thay vì đường chạy RLS; ablation chuyển dataset; phép so sánh với mã tác giả cho thấy khác biệt residual khi chia minibatch. Nhưng chưa đo thí nghiệm đối chứng để quy gap 1,39 pp cho từng yếu tố. Class order, khởi tạo backbone, phân phối projection, phiên bản thư viện và chi tiết kiến trúc có thể ảnh hưởng. Nói chúng là giả thuyết, không phải nguyên nhân đã chứng minh. Hardware giải thích chênh runtime, không tự giải thích chênh accuracy. Các tests tương đương solver giảm khả năng lỗi phương trình, nhưng không xác nhận toàn bộ pipeline giống hệt tác giả.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning
reference-comparison: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/nv8x5tld

## 35. Kết luận trong phạm vi seed 0
Đã tái dựng được cơ chế và đo rõ lợi ích cùng giới hạn

Nhóm đã tự triển khai main ridge, DAC và PLC, kiểm tra bằng tests và đầu ra mã tham chiếu, rồi hoàn tất tám biến thể CIFAR-100 seed 0. DS-AL K=5 đạt A_K 56,87%, cao hơn ACIL 0,31 pp và thấp hơn paper 1,39 pp. Trong ablation, PLC giúp +0,63 pp so với DAC không PLC. Khảo sát K cho kết quả pha cuối gần nhau, còn tăng m cải thiện accuracy ở seed đang xét với chi phí fit tăng mạnh. Giới hạn còn lại là một seed, ablation chuyển miền và chưa tái hiện ImageNet. Bước tiếp theo là nhiều seed và xác minh cấu hình chưa nêu rõ, không điền thêm số khi chưa chạy. Phụ lục cung cấp chứng cứ kỹ thuật để người đọc kiểm tra.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
acil-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/h2sljkd5
dac-no-plc-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/gpx1ehdu
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 36. Phụ lục: gain và kích thước ma trận
Lₖ = RₖXₖᵀ là mắt xích trong chứng minh

Từ Woodbury, R_k=R_prev−R_prev Xᵀ(I+X R_prev Xᵀ)⁻¹X R_prev. Nhân hai vế với Xᵀ và dùng I−(I+A)⁻¹A=(I+A)⁻¹, thu R_k Xᵀ=R_prev Xᵀ(I+X R_prev Xᵀ)⁻¹=L_k. Đặt W_prev đã padding có kích thước m×c_k thì Y_k−X_k W_prev có n_k×c_k. Nhân L_k tạo cập nhật m×c_k đúng kích thước. Điều này nối hình thức gain phổ biến trong RLS với Eq. 11 của paper. Ma trận I trong gain là n_k×n_k, còn I trong regularization là m×m. Tách hai kích thước là điểm cần chú ý khi giải thích.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning

## 37. Đối chiếu mã tác giả trên đầu vào tổng hợp
Cùng dữ liệu, nhãn và projection; thay batch của mã tham chiếu từ 20 xuống 4

Nhóm dùng checkout 0afd6bf để kiểm chứng trên đầu vào tổng hợp nhỏ, cùng projection và nhãn. Khi mỗi pha là một batch 20 mẫu, sai số score tối đa khoảng 7,88e-13 và head bù khoảng 2,32e-12, phù hợp sai số số học. Khi mã tác giả chia batch 4, head chính vẫn gần nhau nhưng head bù lệch tối đa 0,2257 và score lệch 0,0815. Đây là bằng chứng hai cách xác định thời điểm tạo residual khác nhau. Không từ đó kết luận toàn bộ mã tác giả sai hay rằng đã tìm được nguyên nhân gap CIFAR. Benchmark nhóm giữ residual sau main head cuối pha theo Algorithm 1 của supplementary. Các sai khác trên slide là max absolute difference so với triển khai của nhóm, không phải accuracy. Chỉ thay batch size trong đường chạy mã tác giả; triển khai nhóm giữ residual sau nghiệm main cuối pha. Phạm vi là đầu vào tổng hợp nhỏ tại official checkout 0afd6bf87622e808ce7f730f8556e78229b9e758. Kết quả cho thấy hai đường chạy không tương đương với minibatch nhỏ trong thiết lập này, không chứng minh mã tác giả sai nói chung và không định lượng nguyên nhân gap trên CIFAR.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning
reference-comparison: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/nv8x5tld

## 38. Phụ lục: phạm vi của bất biến pha
Head chính gần bất biến, head bù có thể đổi

Đây là thí nghiệm cơ chế tổng hợp hỗ trợ đọc hiểu và là bằng chứng Lab 2, không dùng thay benchmark CIFAR của Lab 1. Giữ dữ liệu, projection và gamma, thay số pha 1/2/5 trên ba seed. W_M cuối khác nhau khoảng cỡ 1e-14, còn W_C và score thay đổi rõ. Điều đó cho thấy không thể dùng riêng Theorem 1 để kết luận toàn DS-AL bất biến chính xác theo cách chia pha. Nó không phủ nhận quan sát accuracy gần ổn định trên dataset ảnh. Kết luận cần phân biệt nghiệm của main head, trọng số compensation, score và accuracy; chúng là bốn phát biểu khác nhau.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
phase-dependence: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/hh31425p

## 39. Phụ lục: cấu hình và provenance
Một run cần nhiều hơn một nhãn seed

Phụ lục ghi lại seed, class order, revision dữ liệu, checksum checkpoint và feature cache, cùng phiên bản đã chạy. Đây là thông tin truy vết, không phải dữ liệu thay thế kết quả. Config dùng revision main để bắt đầu, nhưng loader resolve một lần và feature identity giữ commit SHA của dataset; chạy lại phải giữ SHA này. Random projection không bias và chuẩn độ lệch chuẩn 1 là lựa chọn công khai của nhóm khi paper không cho đủ chi tiết. Provenance có git_dirty=true nên cần giữ manifest source SHA-256, không chỉ checkout commit. Không đưa API key vào bất kỳ config công khai hoặc slide nào.

dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme

## 40. Phạm vi của các kết luận
Phân biệt tương đương nghiệm, ổn định accuracy và tác dụng thực nghiệm

Ba loại phát biểu cần được phân biệt. Thứ nhất, Theorem 1 bảo đảm main head bằng nghiệm joint ridge khi feature, projection, activation và gamma cố định, padding đúng và dữ liệu được cập nhật đầy đủ. Thứ hai, accuracy pha cuối của DS-AL gần nhau khi đổi K trong benchmark seed 0 là quan sát thực nghiệm, không suy ra trọng số toàn DS-AL bất biến chính xác. Thứ ba, lợi ích DAC/PLC phụ thuộc protocol; trong CIFAR seed 0, PLC tăng 0,63 pp so DAC không PLC, còn DAC đơn lẻ thấp hơn ACIL. Các seed của bài kiểm tra cơ chế là dữ liệu tổng hợp, không phải các lần lặp CIFAR. Do đó không dùng bảo đảm main ridge để khẳng định không quên ở cấp CNN, tính bất biến của compensation hoặc ý nghĩa thống kê của một chênh lệch accuracy.

[1] H. Zhuang, R. He, K. Tong, Z. Zeng, C. Chen, and Z. Lin, “DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 15, pp. 17237–17244, 2024, doi:10.1609/aaai.v38i15.29670. https://doi.org/10.1609/aaai.v38i15.29670
[2] H. Zhuang et al., “Supplementary Material for DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning,” Sec. A: proof, Sec. B: algorithms, Sec. C: training details, 2024. Local source: docs/references/DS-AL-supplementary.pdf. https://github.com/ZHUANGHP/Analytic-continual-learning
dac-no-plc-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/gpx1ehdu
dsal-k5: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme
phase-dependence: https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/hh31425p
