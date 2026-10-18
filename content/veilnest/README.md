# Nội dung Veilnest

[Hồ sơ app](../../docs/apps/veilnest.md) · [Lịch](../../docs/content/CALENDAR.md) · [Nguồn nhập và lưu trữ](../../docs/content/IMPORT.md)

## Các bộ hiện có

| Creative ID / thư mục | Trạng thái | Cách dùng tiếp |
|---|---|---|
| [veilnest-us-pov-2026-10-04](videos/veilnest-us-pov-2026-10-04/README.md) | Bản POV v1, animatic 15s, chưa phải quảng cáo final | Giữ làm tham chiếu/lịch sử; ưu tiên xem v2 |
| [veilnest-us-pov-v2-2026-10-04](videos/veilnest-us-pov-v2-2026-10-04/README.md) | POV v2, animatic 15s, sửa tính liên tục owner → friend → owner | Hướng chính nếu chọn comedy POV; còn cần actor motion/voice và UI thật |
| [veilnest-gemini-continuation-2026-10-04](videos/veilnest-gemini-continuation-2026-10-04/README.md) | Kit nối opening Gemini có sẵn thành khoảng 18s; chưa có clip B mới | Hướng thay thế nếu giữ opening đã có; tạo/dựng đoạn B rồi ghép |

**V2 và Gemini continuation là hai hướng sản xuất**, không phải hai bản cuối đã sẵn sàng đăng. Các ảnh/UI là tài liệu dựng, không phải capture app thực. Các JSON verification cũ chứng minh kiểm tra kỹ thuật tại thời điểm dựng, không chứng minh chất lượng final hoặc kết quả marketing.

Đã chép đủ 109 file từ IOS-Vault ngày 18/10/2026 và để nguyên nguồn. Git lưu file làm việc/preview (~41 MiB). ZIP handoff và thư mục `continuation-kit/` trùng lặp vẫn ở local nhưng bị gitignore (~48 MiB); clone mới có toàn bộ nội dung làm việc duy nhất, không có các bundle trùng này. Xem [manifest](../../docs/content/IMPORT_2026-10-18.json).

## Preview

Từ gốc repo, chọn một storyboard:

```sh
python3 content/veilnest/videos/veilnest-us-pov-v2-2026-10-04/serve_preview.py
```

Mở [localhost:8767/storyboard.html](http://127.0.0.1:8767/storyboard.html). V1 có server tương tự mặc định port 8766. Hướng Gemini có clip A, screen demo, end card và prompt riêng trong thư mục; chưa có final nối với motion B mới.

Giữ bản nhập làm mốc; creative mới dùng ID mới và ghi quan hệ `based_on` trong brief. Những script render cũ cần Python/Pillow, FFmpeg/ffprobe và font macOS; đã nhập để bảo tồn quy trình, chưa chạy render lại trong lần sắp xếp này.
