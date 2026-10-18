# Logo KV Apps

Chọn ngày 18/10/2026: mẫu "mảnh ghép" (phương án 3 trong bốn ảnh AI). Các file ở đây được **vẽ lại bằng SVG** theo đúng hình ảnh đó, không dùng ảnh raster gốc.

| File | Dùng cho |
|---|---|
| `kv-mark.svg` | Hình KV trên nền sáng |
| `kv-mark-on-dark.svg` | Hình KV trên nền tối: mảng navy được làm sáng để không chìm vào nền |
| `avatar-light.svg` · `avatar-light-1024.png` | **Avatar mặc định** cho mọi kênh: nền trắng, đọc rõ cả trên app nền tối |
| `avatar-dark.svg` · `avatar-dark-1024.png` | Khi muốn avatar nền tối |
| `favicon.svg` | Favicon website (`website/assets/kv-apps.svg`), tự đổi màu theo chế độ sáng/tối của trình duyệt. Header website dùng `website/assets/kv-mark.svg` (bản on-dark) và `kv-mark-on-light.svg` cho trang Paper Drift; avatar `kv-apps-avatar.png` dùng ở hero và apple-touch icon; ảnh chia sẻ `kv-apps-social-cover.jpg` lấy từ social-kit |

Avatar chỉ dùng hình KV, không kèm chữ "KV Apps" vì ở cỡ avatar chữ không đọc được và tên kênh đã nằm cạnh avatar. Hình nằm giữa, rộng 640/1024 px nên không bị mất khi cắt tròn. Banner và cover ở [social-kit](../social-kit/README.md) dùng `kv-mark-on-dark.svg`.

Sửa hình: chỉnh các `path` trong SVG (giống nhau ở mọi file), rồi xuất PNG:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1024,1024 --screenshot=content/shared/logo/avatar-light-1024.png "file://$PWD/content/shared/logo/avatar-light.svg"
```

Trước khi dùng rộng rãi, chủ studio nên tìm ảnh ngược (Google Images/Lens) để chắc logo do AI tạo không trùng thương hiệu khác.
