# Bộ hồ sơ social KV Apps

Lập ngày 18/10/2026. Mọi kênh dùng **một nhận diện**: tên `KV Apps`, handle `khanhvuapps`, link `https://khanhvu-ops.github.io/`, email `khanhvu.dev@gmail.com`. Trạng thái thật của từng kênh nằm trong [sổ tài khoản](../../../docs/social/ACCOUNTS.md); file này chỉ là nội dung để dán vào.

Đăng ký, mật khẩu, ngày sinh, OTP và xác minh do chủ tài khoản tự làm. Không lưu các thông tin đó trong repo.

## Ảnh

| File | Dùng cho | Kích thước | Ghi chú |
|---|---|---|---|
| [`../logo/avatar-light-1024.png`](../logo/avatar-light-1024.png) | Avatar mọi kênh (logo mới 18/10) | 1024 × 1024 | Nền trắng; bản nền tối: `avatar-dark-1024.png`. Xem [logo](../logo/README.md) |
| [`youtube-banner-2560x1440.jpg`](youtube-banner-2560x1440.jpg) | Banner YouTube | 2560 × 1440, 248 KB | Logo và icon nằm trong vùng giữa ~1500 × 400, phần còn lại có thể bị cắt trên mobile |
| [`facebook-cover-1640x683.jpg`](facebook-cover-1640x683.jpg) | Ảnh bìa Facebook Page | 1640 × 683 (2.4:1), 96 KB | Nội dung ở giữa, chừa góc dưới trái cho avatar |

Nguồn của banner và cover là [`banner.html`](banner.html). Muốn sửa thì chỉnh file đó rồi chụp lại bằng Chrome headless:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=2560,1440 --screenshot=banner.png "file://$PWD/content/shared/social-kit/banner.html"
```

Mặc định file HTML không đặt kích thước vùng an toàn; thêm `style="--w:1500px;--h:400px"` (YouTube) hoặc `style="--w:1080px;--h:300px"` (Facebook) vào thẻ `<div class="safe">`.

Kích thước tham chiếu: [YouTube channel branding](https://support.google.com/youtube/answer/10456525) (2560 × 1440 khuyến nghị, tối thiểu 2048 × 1152, ≤ 6 MB) và [Facebook Page dimensions](https://www.facebook.com/help/125379114252045) (bìa 2.4:1 trên mobile, 16:9 trên desktop).

## Nội dung từng kênh

### YouTube — [@khanhvuapps](https://www.youtube.com/@khanhvuapps)

Đã có tên, handle, mô tả, link. **Còn thiếu banner; avatar cần thay bằng logo mới.**

YouTube Studio → **Customization → Branding → Banner image → Upload** → chọn `youtube-banner-2560x1440.jpg` → kiểm tra khung TV/desktop/mobile → **Publish**.

### TikTok — [@khanhvuapps](https://www.tiktok.com/@khanhvuapps)

Đã có tên `KV Apps`, avatar và bio (kiểm tra 18/10/2026). Bio đang dùng (≤ 80 ký tự):

```text
iOS apps & offline games by Khanh Vu. Small apps. Everyday joy.
```

Ô Website trên TikTok chỉ hiện khi tài khoản đủ điều kiện; chưa có thì CTA trong video là "Search Veilnest on the App Store".

### Instagram — [@khanhvuapps](https://www.instagram.com/khanhvuapps/)

Đã có tên, avatar, bio và link (kiểm tra 18/10/2026). Bio đang dùng (≤ 150 ký tự):

```text
Practical iOS apps, creative tools and offline games by Khanh Vu.
Small apps. Everyday joy.
```

Còn lại: chọn loại tài khoản chuyên nghiệp (**Settings → Account type and tools → Switch to professional account → Creator** hoặc **Business**, category *App Page* hoặc *Software*), rồi bật hiển thị email liên hệ `khanhvu.dev@gmail.com`.

### Threads — @khanhvuapps (chưa tạo)

Threads dùng chung tài khoản Instagram, nên handle sẽ là `@khanhvuapps`.

1. Cài app **Threads** trên iPhone, chọn **Log in with Instagram** và chọn `khanhvuapps`.
2. Chọn **Import from Instagram** để lấy tên, avatar và bio.
3. Profile để **Public**.
4. Vào **Edit profile → Link**, dán `https://khanhvu-ops.github.io/`. Link phải ở ô Link, không phải trong bio.
5. Kiểm tra lại trên [threads.com/@khanhvuapps](https://www.threads.com/@khanhvuapps), rồi cập nhật sổ tài khoản.

Bio Threads (≤ 150 ký tự), nếu muốn khác Instagram:

```text
Solo dev building iOS apps & offline games. Notes on shipping, privacy and app marketing. Small apps. Everyday joy.
```

Threads hợp với bài chữ ngắn hơn video: chuyện làm app, ảnh chụp màn hình, câu hỏi cho người dùng. Xem [kênh Threads](../../../docs/social/channels/threads/README.md).

### Facebook Page — KV Apps (chưa tạo)

Cần **Facebook cá nhân thật** của chủ studio trước; Page được tạo và quản trị từ tài khoản đó.

1. Facebook → **Pages → Create new Page**.
2. Page name: `KV Apps`. Category: `App Page` (thêm `Software` nếu được chọn nhiều).
3. Bio:

```text
Apps & Games by Khanh Vu. Small apps. Everyday joy.
```

4. Contact: email `khanhvu.dev@gmail.com`, website `https://khanhvu-ops.github.io/`.
5. Avatar `../logo/avatar-light-1024.png`, cover `facebook-cover-1640x683.jpg`.
6. **Settings → Username**: thử `khanhvuapps` (hiện `facebook.com/khanhvuapps` chưa có trang nào công khai). Nếu đã có người dùng thì thử `kvappsstudio`.
7. Nút hành động: **Send email** tới `khanhvu.dev@gmail.com`.
8. Kiểm tra trang ở chế độ xem public, cập nhật sổ tài khoản.

Mô tả dài (phần About / Details):

```text
KV Apps is a small studio by Khanh Vu making practical iOS apps, creative tools and offline games.

Veilnest: a private photo and video vault with its own PIN.
Color Meter: find and keep colors from camera and photos.
Paper Drift: a calm paper-boat puzzle game (in development).

Support: khanhvu.dev@gmail.com
```

## Sau khi xong

Kiểm tra từng profile ở chế độ chưa đăng nhập, ghi ngày và URL vào [ACCOUNTS.md](../../../docs/social/ACCOUNTS.md). Chỉ thêm link kênh lên website sau khi URL public đã kiểm tra.
