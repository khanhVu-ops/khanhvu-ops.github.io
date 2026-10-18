# Video brief — 2026-10-18-hidden-album-en-v1

| Trường | Giá trị |
|---|---|
| Creative ID | `2026-10-18-hidden-album-en-v1` |
| App / build kiểm tra | Veilnest 1.3 (App Store US, kiểm tra 18/10/2026) — quay trên build đang phát hành |
| Ngày tạo / người phụ trách | 18/10/2026 · Khanh Vu |
| Trạng thái | Brief |
| Based on | — |
| Ngôn ngữ / thị trường thử | EN |
| Tình huống người dùng | Hidden album vs. vault |
| Một lợi ích chính | Hidden album mở bằng passcode máy; vault có PIN riêng |
| Hook 0–2s | Xem bảng biến thể bên dưới |
| CTA / URL đích đã xác minh | Text: tìm "Veilnest" trên App Store. Link mô tả YouTube: https://apps.apple.com/app/id6813747332 · CPP `mặc định` thay link khi CPP được duyệt |
| Kênh dự kiến | YouTube Shorts, TikTok; Reels khi có tài khoản |
| Thời lượng / tỷ lệ khung | 12–15s · 9:16 · 1080×1920 |
| Footage thật / AI / mockup | Quay màn hình build thật + tay cầm máy; vault thử, ảnh mẫu không có người thật. `synthetic_media = false` chỉ đúng khi không dùng cảnh AI |
| Nguồn kiểm chứng tính năng / ngày kiểm tra | Hidden album: Collections → Utilities → Hidden, mở bằng Face ID/Touch ID/passcode (iOS 16+). Veilnest: PIN 6 số riêng. |
| Nhạc/font/media và quyền sử dụng | Âm thanh gốc hoặc thư viện âm thanh có quyền của từng nền tảng; font hệ thống |

## Biến thể hook

Chỉ đổi text 0–2 giây và tiêu đề; giữ nguyên footage để so sánh hook.

| Biến thể | Hook | Metadata YouTube |
|---|---|---|
| A | Your Hidden album opens with your phone passcode | `youtube-a.toml` |
| B | Hidden album vs. a vault with its own PIN | `youtube-b.toml` |
| C | Who else knows your iPhone passcode? | `youtube-c.toml` |

## Kịch bản

| Thời gian | Hình / hành động | Voice / text | Asset |
|---|---|---|---|
| 0–2s | Photos → Hidden album, text hook | Hook | |
| 2–5s | Nhập passcode máy → Hidden album mở | "Anyone with your passcode gets in." | |
| 5–10s | Mở Veilnest → PIN riêng → vault | "A vault with its own PIN." | |
| 10–13s | Text: Hidden album = free & built in; vault = separate PIN | Công bằng, không chê Apple | |
| 13–15s | End card + "Full guide: link in description" | — | |

## Review

- [ ] Hành vi và claim khớp build; ghi rõ giả lập/mockup nếu dùng.
- [ ] Hình/tiếng/subtitle và vùng UI che phủ đã xem trên điện thoại.
- [ ] CTA khớp app, ngôn ngữ và link đích thật.
- [ ] Bản export cuối ở `exports/` có tên/version; trạng thái không vượt bằng chứng.

## Upload YouTube (private)

```sh
tools/youtube/.venv/bin/python tools/youtube/upload.py upload content/veilnest/videos/2026-10-18-hidden-album-en-v1/exports/<file>.mp4 --meta content/veilnest/videos/2026-10-18-hidden-album-en-v1/youtube-a.toml --dry-run
```

Bỏ `--dry-run` để upload private. Xem [tools/youtube/README.md](../../../../tools/youtube/README.md).

## Sau khi đăng

Ghi URL vào nhật ký kênh và [lịch 14 ngày](../../../../docs/content/VEILNEST_14_DAYS.md).
