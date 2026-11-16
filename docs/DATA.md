# Dữ liệu

- HF dataset: `uoft-cs/cifar100`.
- Revision tải: `aadb3af77e9048adbea6b47c21a81e47dd092ae5`.
- Train/test gốc50.000/10.000 ảnh RGB32×32, 100 fine classes.
- Mục tiêu: `fine_label`, không phải coarse label.
- Tải parquet qua HF hub, đọc bằng pyarrow/Pillow, không chuẩn bị thủ công.
- Normalize mean=(0.5071,0.4867,0.4408), std=(0.2675,0.2565,0.2761).
- Base training có RandomCrop32 padding4 và horizontal flip.
- Trích feature/AL chỉ normalize, không augmentation.
- Lưu nguyên class order trong checkpoint/config. 50 lớp base,50 lớp sau
  chia qua K pha. Smoke giới hạn số ảnh mỗi lớp, không dùng đối sánh paper.

HF card ghi license `unknown`, không tự gán MIT/CC-BY cho dữ liệu.
Nguồn: https://huggingface.co/datasets/uoft-cs/cifar100 và
https://www.cs.toronto.edu/~kriz/cifar.html . Không commit ảnh vào Git.

Cache ở `data/cache/`, checkpoint ở `checkpoints/`. Cache feature gắn
hash checkpoint, revision dataset, class order, transform và giới hạn
mẫu để tránh dùng nhầm feature khác protocol.
