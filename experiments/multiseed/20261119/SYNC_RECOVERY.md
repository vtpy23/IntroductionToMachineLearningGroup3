# Khôi phục bước đồng bộ W&B ngày 19/11/2026

Seed 1 hoàn thành backbone 160 epoch và cả ba phương pháp. Bộ điều phối dừng lúc 12:35 (UTC+7) khi lệnh `wandb sync` đã báo upload ACIL thành công nhưng API chưa trả về đầy đủ trạng thái `finished`/summary hoàn tất. Khi đọc lại, run `i0jt6hm8` đã hoàn tất và khớp dữ liệu cục bộ. Không có lỗi huấn luyện hoặc mất checkpoint được phát hiện.

## Sửa tối thiểu

Chỉ thay đổi `scripts/sync_wandb.py` trong bộ source đã đóng băng: làm mới cache SDK và chờ API phản ánh trạng thái hoàn tất sau khi CLI upload. Bổ sung chế độ khôi phục upload dở, phải bật tường minh bằng `--recover-verified-existing`.

Chế độ khôi phục chỉ nhận run chưa có dấu hash sau khi config, toàn bộ scientific summary và từng giá trị history khớp bằng chứng cục bộ. Run đã có hash khác vẫn bị từ chối. Không upload đè số liệu của run đã được xác minh; chỉ bổ sung metadata xác nhận đồng bộ và URL. Thư mục offline gốc, config, metrics, summary, classifier và checkpoint được giữ nguyên.

15 kiểm thử qua, gồm kiểm thử trạng thái API chậm cập nhật và kiểm thử từ chối history sai khác. Không thay đổi dataset loader, model, thuật toán analytic, training, đánh giá hoặc cấu hình thí nghiệm. Seed 1 không được huấn luyện lại.

## Ghi nhận phiên bản

- Bản source ban đầu vẫn ở `outputs/multiseed-20261119/source_snapshot/`.
- Bản support đã sửa ở `outputs/multiseed-20261119/source_snapshot_sync_v2/`.
- `verification/sync-support-revision-v2.json` ghi đúng file thay đổi và hash trước/sau. `provenance.json` có lịch sử revision.
- Config/provenance của các run seed 1 vẫn phản ánh đúng phiên bản đã thực sự tạo số liệu. Seed 2 dùng cùng mã học thuật; chỉ công cụ sync có bản sửa.

Bước khôi phục không thay đổi protocol và không tính mean/SD trước khi đủ ba seed hợp lệ. Báo cáo kết quả tự động tiếp tục ở `RESULTS.md`; giới hạn backend GPU→CPU của seed 0 vẫn được ghi tại `PREFLIGHT.md`.
