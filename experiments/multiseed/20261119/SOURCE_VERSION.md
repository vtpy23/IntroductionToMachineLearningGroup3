# Phiên bản mã nguồn của đợt chạy

`provenance.json` ghi Git HEAD/dirty state thật và SHA-256 trên byte gốc của các file Windows. Git có thể chuẩn hóa newline của source ở thư mục gốc khi checkout trên hệ điều hành khác; điều đó không phải thay đổi công thức hay protocol.

Để đối chiếu SHA-256 độc lập với newline của Git, `source_snapshot/` lưu nguyên byte các file trong manifest lúc bắt đầu đợt chạy. `source_snapshot_sync_v2/` lưu phiên bản hỗ trợ đồng bộ W&B sau đó. Hai snapshot chỉ khác `scripts/sync_wandb.py`; chi tiết trước/sau có trong `verification/sync-support-revision-v2.json`. Toàn bộ mã số học, huấn luyện, dataset và cấu hình thí nghiệm giữ nguyên. Các snapshot là bản ghi lịch sử, không thay thế module chạy ở `src/`, `scripts/` và `configs/`.

Quy tắc `.gitattributes` giữ nguyên byte của toàn bộ thư mục bằng chứng này. Không chứa API key, dữ liệu ảnh, feature cache hay trọng số checkpoint.
