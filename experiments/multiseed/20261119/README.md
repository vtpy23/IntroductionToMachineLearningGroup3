# Chạy bổ sung hai seed độc lập

Xem [kiểm tra trước khi chạy](PREFLIGHT.md) và [báo cáo kết quả](RESULTS.md).

**Đã hoàn thành lúc 16:53 ngày 19/11/2026 (UTC+7).** Xem [báo cáo hoàn tất và kiểm tra cuối](COMPLETION_REPORT.md): đủ ba seed, không còn thiếu thí nghiệm trong phạm vi ba phương pháp chính; mean/sample SD đã được tính từ kết quả được xác minh. Không sửa slide.

Lỗi xác minh trạng thái W&B sau seed 1 và bản sửa support được ghi tại [SYNC_RECOVERY.md](SYNC_RECOVERY.md). Mã học thuật và cấu hình thí nghiệm giữ nguyên; không huấn luyện lại seed 1.

Lưu ý khi diễn giải ba seed: seed 0 có các attempt CUDA rồi resume trên CPU; seed 1/2 dùng CPU xuyên suốt. Protocol dữ liệu, tham số và đánh giá giữ nguyên, nhưng không coi đây là ba lượt giống hệt backend hoặc dùng thời gian giữa các seed làm benchmark phần cứng được kiểm soát. Chi tiết và bằng chứng ở `PREFLIGHT.md`.

Trạng thái thực tế nằm ở `outputs/multiseed-20261119/status.json`. Trạng thái `completed` chỉ được ghi khi đủ ba phương pháp × ba seed, đã sync W&B và xác minh history. Bảng chưa đủ seed không có mean/SD.

## Xem tiến độ

Chạy từ thư mục gốc repository:

```powershell
$state = Get-Content -Raw outputs/multiseed-20261119/status.json | ConvertFrom-Json
$state
Get-Content -LiteralPath $state.log -Tail 5
```

Khi huấn luyện, trường `base/epoch` là epoch vừa hoàn thành, đích là 160. Các checkpoint được ghi sau từng epoch. Sau huấn luyện, pipeline tự trích feature, chạy ACIL → DAC không PLC → DS-AL, sync/xác minh W&B rồi chuyển sang seed tiếp theo.

## Tiếp tục sau gián đoạn

Chỉ chạy khi controller cũ đã dừng. Không thay đổi source/config hoặc virtual environment giữa các công đoạn. Nếu source/config đã thay đổi, cần kiểm tra lại, không bỏ qua guard hoặc dùng lại thư mục cũ cho thí nghiệm mới.

```powershell
.venv/Scripts/python.exe -u -X utf8 -m scripts.core_multiseed run
```

Pipeline chỉ chấp nhận checkpoint có signature khớp; model, optimizer, scheduler và RNG được khôi phục. Analytic dở được lưu riêng rồi tính lại toàn run, vì sufficient statistics giữa pha chưa được checkpoint trong pipeline gốc.

Để yêu cầu dừng an toàn, tạo `.stop-project` ở thư mục gốc; huấn luyện dừng tại ranh giới epoch, suite dừng tại ranh giới phương pháp. Kiểm tra trạng thái đã dừng trước khi xóa cờ để tiếp tục. Không chạy `scripts.multiseed` mặc định cho đợt này vì script đó sẽ mở rộng lại toàn bộ suite K/buffer.

## Cập nhật lại báo cáo

```powershell
.venv/Scripts/python.exe -X utf8 -m scripts.core_multiseed_report
```

Lệnh chỉ tổng hợp bằng chứng đã xác minh, không huấn luyện và không thay đổi slide. Source dùng cho thí nghiệm và hash nằm trong `provenance.json` cùng bản sao tại `outputs/multiseed-20261119/source_snapshot/`. Raw outputs/checkpoints bị Git ignore; báo cáo nhẹ và các cấu hình có thể công bố riêng sau khi kiểm tra.
