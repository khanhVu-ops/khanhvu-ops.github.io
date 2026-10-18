# Nhập creative Veilnest — 18/10/2026

Theo yêu cầu của chủ studio, đã sao chép **ba thư mục** từ `IOS-Vault/Docs/Marketing/` sang `content/veilnest/videos/`. Bản gốc trong IOS-Vault được giữ nguyên; từ thời điểm nhập, repo studio quản lý các master và phiên bản creative mới.

| Bộ | Tình trạng sản xuất |
|---|---|
| `veilnest-us-pov-2026-10-04` | Animatic POV v1, tham chiếu lịch sử |
| `veilnest-us-pov-v2-2026-10-04` | Animatic POV v2, sửa tính liên tục của hành động |
| `veilnest-gemini-continuation-2026-10-04` | Kit nối clip Gemini; chưa có motion B mới |

## Bảo toàn và Git

Đã sao chép đủ **109 file, khoảng 89 MiB**. [Manifest JSON](IMPORT_2026-10-18.json) ghi đường dẫn nguồn/đích, kích thước và SHA-256 của từng file nguồn.

- Git lưu **file làm việc duy nhất, khoảng 41 MiB**: script, prompt, ảnh, subtitle, storyboard, video preview và báo cáo kiểm tra cũ.
- Các ZIP và thư mục `continuation-kit/` lặp lại bản bên ngoài, khoảng **48 MiB**, vẫn có tại máy này nhưng đã gitignore. Chúng không nằm trong clone mới; toàn bộ nội dung làm việc tương ứng đã được track. Có thể tạo lại handoff từ thư mục master khi cần.
- Ba README được thêm ghi chú nguồn/trạng thái; README và một báo cáo JSON của bộ Gemini được sửa đường dẫn cũ thành tên file/lệnh tương đối. Byte của các media và script nhập giữ nguyên. Bản duplicate local vẫn giữ nguyên bản nguồn. Manifest lưu hash **nguồn** để kiểm tra provenance, không phải hash mới của bốn file văn bản đã chỉnh.
- File gốc `gemini_generated_video_38e8ea4b.mp4` nằm ngoài ba thư mục nguồn và không được nhập; kit đã có opening cắt, reference, screen demo và end card. Không khẳng định đã backup file Downloads gốc.
- `assembly-check.json` là smoke check dùng video có sẵn làm B tạm, không chứng minh đã tạo B mới hay có final được duyệt.

Các ghi chú xác thực công cụ/quyền chạy model trong README cũ là lịch sử ngày 04/10; không xác nhận tình trạng kết nối hôm nay. Không chạy model có phí, đăng social hoặc render lại trong lần nhập này.

Xem [chỉ mục Veilnest](../../content/veilnest/README.md) để chọn hướng dựng tiếp.
