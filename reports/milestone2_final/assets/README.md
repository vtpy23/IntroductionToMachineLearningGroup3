# Tài nguyên tự tạo

Không dùng screenshot figure/table của tác giả trong slide. Diagram, bảng và công thức chỉnh sửa được nằm trong `../DSAL_Milestone2_Lab1_Final.pptx`, sinh từ `../build_slides.mjs`.

- `verified_evidence.json`: snapshot 13 run đã đối chiếu chỉ đọc, full config/source hashes/summary/phases, paper Table 1 và phân tích tổng hợp.
- `chart_data.json`: số đo gốc để cập nhật chart, không có dữ liệu nghiên cứu giả.
- `diagrams/slide-NN.png`: preview cả trang đã render từ chính các đối tượng native, gồm ví dụ/timeline, replay, architecture, buffer, padding, C-RLS, proof, DAC, PLC và fusion. PNG chỉ để xem/đối chiếu; sửa hình ở PPTX hoặc JS, không sửa PNG.
- `charts/slide-NN.png`: preview trang có chart native: huấn luyện, activation toán học, metric, paper-vs-group, phase curves, buffer survey và thí nghiệm cơ chế.

Biểu đồ activation là phép tính hàm ReLU/tanh, không phải kết quả benchmark. Ví dụ PLC/padding là minh họa đại số. Những trang có thí nghiệm thật mang URL W&B và notes truy vết. File ảnh preview được cập nhật sau khi render bản cuối; ảnh của đủ 40 trang nằm tại `../.build/rendered/`.
