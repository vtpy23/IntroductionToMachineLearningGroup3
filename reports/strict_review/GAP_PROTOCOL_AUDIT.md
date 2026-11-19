# Sai lệch protocol và reproduction gap

> Publication update 2026-11-20: see [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md). The team reports submission and has authorized publishing this revision. References below to an unpushed/local-only revision describe the original 2026-11-19 review. Original files and their manifest are archived in [history](history/review-delivery-20261119.zip). The review score is not an official grade.

Phải phân biệt **paper/Supplement**, **checkout mã tác giả0afd6bf** và **mã nhóm**. Checkout hiện tại không phải bằng chứng rằng từng run AAAI2024 dùng chính cấu hình ấy. Không dùng số cao hơn trong README hiện tại của tác giả làm mốc paper.

| Yếu tố | Paper / Supplement | Checkout đối chiếu | Nhóm | Phân loại và kiểm chứng |
|---|---|---|---|---|
| Dataset / protocol | CIFAR100, nửa lớp base, K5/25/50 | Có wrapper B50 | HF revision aadb3af77e9048adbea6b47c21a81e47dd092ae5, 50k/10k, fine labels | Đã xác minh phần cấu trúc protocol; không suy rằng cùng split lớp với paper |
| ResNet32 | Kiến trúc CIFAR | OptionA, 5block mỗi stage16/32/64 | Cùng số block/channel/shortcut, feature64D | Forward cùng weights trên4 input tổng hợp float64 khớp1,14e-13. Không là chứng minh cùng init/training |
| Backbone training | SGD160, LR0,1, giảm80/120, momentum0,9, WD5e-4, batch128 | README300/cosine/LR0,5 | Theo SupplementC | Khớp thông số paper được nêu; checkout thay training rõ ràng |
| Checkpoint selection | Không đủ thông tin chọn epoch trong từng run | Chưa xác minh checkpoint tác giả dùng cho Table1 | Final epoch160, không chọn test-best; log đủ160epoch | Phương án nhóm đã xác minh, quy trình paper chưa xác minh |
| Augmentation | SupplementC: crop/flip/normalize; analytic không augment | TrivialAugmentWide; README nói không augment trong paper, mâu thuẫn SupplementC | Crop32 padding4, horizontal flip, normalize; analytic deterministic | Nhóm theo SupplementC. Không tự coi mâu thuẫn README là bằng chứng paper thực tế dùng/no augment |
| Normalization | Chưa cho đủ chữ số | Mean/std cụ thể trong datasets/CIFAR.py | Mean0,5071/0,4867/0,4408, std0,2675/0,2565/0,2761 | Khác nhẹ với checkout đã xác minh; ảnh hưởng chưa đo |
| Class order | Không có permutation/seed của ba run paper | Python `Random(seed).shuffle` nếu bật | NumPy `RandomState(seed).permutation`; inverse đúng | Khác RNG với checkout; paper chưa xác minh. Ba seed không phải ba tên trên cùng backbone |
| Projection | Random expansion, phân phối chưa mô tả đủ | `Linear.reset_parameters`: Uniform±1/√d, không bias | Normal(0,1), không bias | Khác biệt phân phối đã xác minh; chưa có can thiệp tách tác động |
| Initialization | Không đủ chi tiết | Conv/Linear Kaiming normal mặc định fan_in | Conv fan_out, Linear mặc định | Khác initialization đã xác minh với checkout; không suy ra số pp gap |
| Ridge / C / activation | gamma theo ACIL; C0,6 CIFAR, mainReLU/compTanh | README gamma0,1; mặc định constructor DSAL khác tham số CLI | gamma0,1 hai stream, C0,6, ReLU/Tanh | Đã đối chiếu config thực tế, không dùng constructor default thay config chạy |
| Solver | C-RLS Eq11/12 | RecursiveLinear | Stats/Cholesky FP64; có RLS được test | Cùng objective main, không cùng runtime hoặc bitwise solution. Đã test direct ridge, không phải can thiệp gap8192 |
| Residual | Algorithm1: cập nhật main pha rồi tạo residual | DSAL.fit cập nhật main trước residual trong mỗi minibatch | Sau main cuối pha, rồi học compensation | Vị trí bắt đầu khác đã xác minh. Tiny input batch20 khớp; batch4 khác compensation. Chưa đo ảnh hưởng CIFAR8192 |
| PLC | Zero residual cột lớp cũ, base không áp | Cắt theo increase_size | Đúng cột old_classes; giữ residual âm của cột mới | Đã có oracle test và ablation; PLC không đóng băng old weights |
| Evaluation | Test mọi lớp đã thấy; A-bar gồm base | Cùng dạng cumulative evaluation |6/26/51 điểm theo K, sample accuracy | Công thức/mean/SD đã xác minh bằng logs và run |
| Backend | RTX3090 workstation | Không đại diện mọi lịch sử paper | Seed0 CUDA19epoch rồi CPU;1/2 CPU | Backend không hoàn toàn đồng nhất. Unit resume cùng backend đạt; không chứng minh CUDA→CPU bitwise equivalence |

Các khác biệt trên **có khả năng ảnh hưởng**, nhưng không phải mọi khác biệt đã được chứng minh là nguyên nhân reproduction gap. Dùng ba nhãn rõ ràng: cấu hình/khác biệt đã xác minh; giả thuyết có thể ảnh hưởng; tác động định lượng hoặc cấu hình run paper chưa xác minh.

ACIL gap A_K−1,4100pp, DS-AL−1,4867pp. Gain nhóm DS-AL−ACIL0,4033pp khá gần gain paper0,48pp; điều đó hỗ trợ việc hai cách so sánh cho cùng chiều lợi ích tương đối trong phạm vi này. Nó không chứng minh gap tuyệt đối chỉ do backbone, vì projection/residual/class order có thể tương tác.

Can thiệp ưu tiên đã chuẩn bị: đổi riêng distribution projection trên cùng cache, giữ mọi yếu tố còn lại và chạy ACIL/DS-AL theo cặp. Kế hoạch6run dùng tổng393,38s elapsed cũ làm tham chiếu, không phải cam kết thời gian. Chưa thực thi. Tiếp theo mới cân nhắc residual minibatch hoặc augmentation/init; các can thiệp backbone phải train lại, không chạy trước khi được đồng ý.
