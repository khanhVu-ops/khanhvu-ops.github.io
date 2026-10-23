# Bộ hồ sơ social KV Apps

Lập ngày 18/10/2026. Mọi kênh dùng **một nhận diện**: tên `KV Apps`, handle `khanhvuapps`, link `https://khanhvu-ops.github.io/`, email `khanhvu.dev@gmail.com`. Trạng thái thật của từng kênh nằm trong [sổ tài khoản](../../../docs/social/ACCOUNTS.md); file này chỉ là nội dung để dán vào.

Đăng ký, mật khẩu, ngày sinh, OTP và xác minh do chủ tài khoản tự làm. Không lưu các thông tin đó trong repo.

## Ảnh

| File | Dùng cho | Kích thước | Ghi chú |
|---|---|---|---|
| [`../logo/avatar-light-1024.png`](../logo/avatar-light-1024.png) | Avatar mọi kênh (logo mới 18/10) | 1024 × 1024 | Nền trắng; bản nền tối: `avatar-dark-1024.png`. Xem [logo](../logo/README.md) |
| [`youtube-banner-2560x1440.jpg`](youtube-banner-2560x1440.jpg) | Banner YouTube | 2560 × 1440, 248 KB | Logo và icon nằm trong vùng giữa ~1500 × 400, phần còn lại có thể bị cắt trên mobile |
| [`facebook-cover-1640x683.jpg`](facebook-cover-1640x683.jpg) | Ảnh bìa Facebook Page | 1640 × 683 (2.4:1), 96 KB | Nội dung ở giữa, chừa góc dưới trái cho avatar |

Overlay vùng an toàn cho video dọc 1080 × 1920 nằm ở [`safezones/`](safezones/): `safezones-all` gộp TikTok, Reels và Shorts, các file còn lại là từng nền tảng. Đặt overlay làm lớp trên cùng trong app dựng khi canh chữ, rồi tắt lớp này trước khi xuất. Số đo và lệnh tạo lại xem [tool render](../../../tools/render/README.md#vùng-an-toàn).

Nguồn của banner và cover là [`banner.html`](banner.html). Muốn sửa thì chỉnh file đó rồi chụp lại bằng Chrome headless:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=2560,1440 --screenshot=banner.png "file://$PWD/content/shared/social-kit/banner.html"
```

Mặc định file HTML không đặt kích thước vùng an toàn; thêm `style="--w:1500px;--h:400px"` (YouTube) hoặc `style="--w:1080px;--h:300px"` (Facebook) vào thẻ `<div class="safe">`.

Kích thước tham chiếu: [YouTube channel branding](https://support.google.com/youtube/answer/10456525) (2560 × 1440 khuyến nghị, tối thiểu 2048 × 1152, ≤ 6 MB) và [Facebook Page dimensions](https://www.facebook.com/help/125379114252045) (bìa 2.4:1 trên mobile, 16:9 trên desktop).

## Nội dung từng kênh

### YouTube — [@khanhvuapps](https://www.youtube.com/@khanhvuapps)

Avatar mới và banner đã xuất bản. Trạng thái gần nhất xem [sổ tài khoản](../../../docs/social/ACCOUNTS.md); hướng dẫn dưới đây dùng cho lần thay tiếp theo.

YouTube Studio → **Customization → Branding → Banner image → Upload** → chọn `youtube-banner-2560x1440.jpg` → kiểm tra khung TV/desktop/mobile → **Publish**.

### TikTok — [@khanhvuapps](https://www.tiktok.com/@khanhvuapps)

Tên, bio và avatar logo mảnh ghép mới nền trắng đã lưu; logo vẫn hiển thị sau reload profile ngày 18/10/2026. Trạng thái gần nhất xem sổ tài khoản. Bio đang dùng (≤ 80 ký tự):

```text
iOS apps & offline games by Khanh Vu. Small apps. Everyday joy.
```

Ô Website trên TikTok chỉ hiện khi tài khoản đủ điều kiện; chưa có thì CTA trong video là "Search Veilnest on the App Store".

### Instagram — [@khanhvuapps](https://www.instagram.com/khanhvuapps/)

Đã có tên, logo mới và bio; đã chuyển Business/category Software, lưu email business và bật hiển thị contact. Website đã có link bấm riêng, thêm qua Meta Business Suite và kiểm tra trên profile sau reload. Bio hiện tại (≤ 150 ký tự):

```text
Practical iOS apps, creative tools and offline games by Khanh Vu.
Small apps. Everyday joy.
```

Nút email liên hệ chỉ hiển thị trên Instagram mobile. Không cần chuyển loại tài khoản lại; website đã hoàn tất; kiểm tra nút Email trong app.

### Threads — [@khanhvuapps](https://www.threads.com/@khanhvuapps)

Đã tạo bằng Instagram `khanhvuapps` qua web ngày 18/10/2026, profile Public; bio và link riêng đã lưu. Logo mới kế thừa từ Instagram đã được kiểm tra; trạng thái gần nhất được ghi tại sổ tài khoản.

Quản lý tiếp trên web hoặc app Threads: **Edit profile → Bio**; **Links → Add link**, URL `https://khanhvu-ops.github.io/`, tiêu đề “Explore KV Apps”; lưu bio bằng **Done** trong Edit profile, sau đó thêm link riêng bằng **Done** trong Add link và quay lại profile. Luôn reload để xác nhận link còn hiển thị; lần nhập đồng thời bio/link đã có trường hợp link mất sau reload. Không cần tạo thêm tài khoản hoặc nhập lại mật khẩu.

Bio Threads (≤ 150 ký tự), nếu muốn khác Instagram:

```text
Solo dev building iOS apps & offline games. Notes on shipping, privacy and app marketing. Small apps. Everyday joy.
```

Threads hợp với bài chữ ngắn hơn video: chuyện làm app, ảnh chụp màn hình, câu hỏi cho người dùng. Xem [kênh Threads](../../../docs/social/channels/threads/README.md).

### Facebook Page — KV Apps (chưa tạo)

**Facebook cá nhân thật** của chủ studio đã đăng ký xong. Chủ studio đã xác nhận chính sách và đã bấm Create Page, nhưng Facebook vẫn quay lại form, chưa có Page được xác nhận; chủ studio đã kiểm tra trực tiếp và nghi do tài khoản mới. Chưa có thông báo Facebook xác nhận nguyên nhân hoặc thời gian chờ; trạng thái chi tiết nằm trong sổ tài khoản. Page được quản trị từ tài khoản cá nhân đó.

1. Facebook → **Pages → Create new Page**.
2. Page name: `KV Apps`. Category: `Software` (lựa chọn đã thấy và điền trong UI).
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

### Reddit — tài khoản cá nhân của developer

Reddit dùng tài khoản cá nhân, không làm profile thương hiệu (xem [kênh Reddit](../../../docs/social/channels/reddit/README.md)). Username Reddit không đổi được sau khi tạo; ghi username thật vào sổ tài khoản.

Vào **Settings → Profile** (hoặc **Edit profile** trên trang hồ sơ):

1. Display name (≤ 30 ký tự): `Khanh Vu`.
2. About (≤ 200 ký tự):

```text
Solo dev behind KV Apps: practical iOS apps & offline games (Veilnest, Color Meter). Here for SwiftUI, indie dev and app marketing talk. I always say when I made something.
```

3. Avatar: `../logo/avatar-light-1024.png`, hoặc ảnh cá nhân nếu muốn trông như người thật hơn. Banner để trống.
4. Social links: Website `https://khanhvu-ops.github.io/` (tiêu đề “KV Apps”), YouTube `https://www.youtube.com/@khanhvuapps`. Không thêm App Store vào profile.
5. NSFW: tắt. Giữ hiển thị bài và comment trên profile để mod và người đọc kiểm tra được lịch sử.

Lưu xong thì mở profile ở cửa sổ ẩn danh để kiểm tra, rồi ghi username và ngày vào sổ tài khoản.

## Sau khi xong

Kiểm tra từng profile ở chế độ chưa đăng nhập, ghi ngày và URL vào [ACCOUNTS.md](../../../docs/social/ACCOUNTS.md). Chỉ thêm link kênh lên website sau khi URL public đã kiểm tra.
