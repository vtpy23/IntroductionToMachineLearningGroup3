# Vấn đề còn mở và thí nghiệm bổ sung

> Publication update 2026-11-20: see [TEAM_HANDOFF.md](../../TEAM_HANDOFF.md). The team reports submission and has authorized publishing this revision. References below to an unpushed/local-only revision describe the original 2026-11-19 review. Original files and their manifest are archived in [history](history/review-delivery-20261119.zip). The review score is not an official grade.

## BLOCKED hoặc chưa xác minh ngoài dữ liệu hiện có

1. **BLOCKED – Công bố revision mới:** yêu cầu hiện tại cấm tự push. GitHub public main84b9564 chứa kết quả ba seed/bản trước; code, sensitivity evidence và slide StrictReview mới chỉ ở máy. Nhóm cần kiểm tra rồi cho phép một đợt push riêng trước nộp. Không đổi quyền repository.
2. **UNVERIFIED – Forge/CoreWeave thay wandb.ai:** đã đọc config/summary/history24run không auth, không cookie/netrc, tất cả finished. Điều này chứng minh public data kỹ thuật. Văn bản học phần nêu nền tảng tại wandb.ai, chưa có xác nhận giảng viên chấp nhận host Forge. Cần hỏi giảng viên hoặc dẫn quyết định hiện có. Không tự sync sang host khác, không tạo run thay thế hoặc đổi ID.
3. **PARTIAL – Core coverage:** E1headline + E4Tanh/C sensitivity + E3buffer có cơ sở tốt hơn trước, nhưng E4 chỉ một nhánh Figure4 và K là các cột cùng Table1. Giảng viên có thể yêu cầu activation sweep hoặc thí nghiệm khác quan trọng hơn. Không nhận E2CIFAR là Table2ImageNet.
4. **UNVERIFIED – Clean environment:** hai venv kế thừa packages toàn hệ thống. Pip check có7conflicts ngoài dự án; các module dự án và21test hoạt động. Chưa cài mới/rerun full pipeline trong venv độc lập. Không gỡ torchaudio/OpenCV/Paddle/PDF tools hoặc đổiTorch/CUDA để sửa package ngoài phạm vi. Dùng RUNBOOK tạo env riêng khi nhóm đồng ý kiểm tra.
5. **BLOCKED – Nguyên nhân gap định lượng:** chưa có factorial/one-factor controls đủ để tách projection, init, class order, residual hoặc training. Biết vị trí khác chưa chứng minh nó gây1,49pp gap.
6. **BLOCKED – Train residual lịch sử:** final classifier không đủ tái tạo residual của từng pha tại thời điểm tạo. Phải chạy lại các pha và lưu diagnostics, không vẽ giả từ final heads.
7. **UNVERIFIED – Tài liệu Moodle mới nhất và nộp bài:** không có URL/quyền Moodle trong ngữ cảnh. Đã đọc PDF cung cấp, không tự nhận đã kiểm tra hạn/điểm/chấp nhận E2 hoặc host. Nhóm kiểm tra thông báo chính thức và nộp hai mục riêng.
8. **PARTIAL – Poster/workshop:** draftposter chưa là sản phẩm cuối được rà soát trong đợt bàn giao slide này. Nhóm cần hoàn thiện A2dọc, bảo vệ hai hạn chế lý thuyết có bằng chứng và chuẩn bị mọi thành viên giải thích mã/kết quả.

## Ưu tiên tiếp theo nếu được đồng ý chạy

| Ưu tiên | Thiết kế | Chi phí / giới hạn | Tiêu chí kiểm chứng |
|---|---|---|---|
|1 | Distribution projection, ACIL/DS-AL ×3seed trên cache cũ |6refit8192FP64; tham chiếu elapsed cũ393,38s, không gồm chờ/hash/sync. Cần RAM gần analytic gốc |Config chỉ đổi distribution và metadata/path; parentcache/checkpoint SHA không đổi; paired gap; giữ bản cũ |
|2 | Tanh/Mish/Hardswish ×C0,1…1 trên cùng backbone/cache/projection, ba seed |Phải refit compensation theo activation. Không thể chỉ đổi activation lúc inference của head Tanh. Ước lượng sau pilot được duyệt |Giữ main cố định; C0khớpACIL; Tanh/C0,6khớpbaseline; Figure4subset rõ ràng; không tune benchmark theo test |
|3 | Phase-final vs minibatch residual trên cùng cache |Cần implement đường control riêng, refit và log; tiny comparison hiện có không đủ định lượng accuracy gap |Main weights khớp; chỉ thời điểm residual khác; PLC cùng chính sách; chỉ báo cơ chế ở subset nếu không chạy full |
|4 | Backbone augmentation/init control |Cần train160epoch/seed; vài giờ theo log. Không tự chạy |Cùng class order/data/trainbudget; khai báo checkpointselection trước; đánh giá cả ACIL/DS-AL trên backbone ấy |

Đã chuẩn bị đầy đủ control ưu tiên1:

```powershell
# Chỉ đọc metadata và lập kế hoạch, không refit:
.venv-cpu/Scripts/python.exe -m scripts.controlled_projection_followup

# CHỈ sau khi nhóm đồng ý chạy refit:
.venv-cpu/Scripts/python.exe -u -m scripts.controlled_projection_followup --execute --tracking online
```

Config: `configs/proposed_projection_control.json`. Runner từ chối output đã tồn tại, giữ checkpoint/cache gốc, gắn lab1-reproduction, lưu từng config/phase/history/summary/provenance qua Tracker. Chạy tuần tự; khi gián đoạn không ghép attempt, chọn output root mới để chạy lại phương pháp bị gián đoạn vì analytic chưa resume giữa pha.

Đã chuẩn bị thêm runner/config cho activation control:

```powershell
# Plan-only; không refit:
.venv-cpu/Scripts/python.exe -m scripts.controlled_activation_followup
# Chỉ sau khi nhóm đồng ý:
.venv-cpu/Scripts/python.exe -u -m scripts.controlled_activation_followup --execute --tracking online
```

Config `configs/proposed_activation_control.json`: Mish/Hardswish trên ba seed, dùng Tanh đã hoàn tất làm reference; sáu fit và sáu run phân tích C riêng, gắn parent run ID/hash. C0 phải khớp ACIL; main/projection phải khớp baseline. Chưa thực thi nhánh `--execute`, nên chưa nhận runner này đã được kiểm chứng ở full scale. Nếu giảng viên yêu cầu Figure4 rộng hơn để đủ Core, ưu tiên activation control trước projection; nếu mục tiêu là chẩn đoán gap, ưu tiên projection. Control residual/backbone hiện mới là thiết kế, chưa có runner đã kiểm chứng.
