# Sổ tài khoản studio

Cập nhật **19/10/2026**. Google chủ sở hữu studio: **`khanhvu.dev@gmail.com`**. Mọi trạng thái dưới đây là trạng thái đã quan sát hoặc được chủ tài khoản xác nhận, không phải kế hoạch đã hoàn thành.

| Nền tảng | Hồ sơ / định danh | Trạng thái | Chủ sở hữu / quản trị | Việc còn lại |
|---|---|---|---|---|
| YouTube | [KV Apps · @khanhvuapps](https://www.youtube.com/@khanhvuapps), ID `UC7kW-0SrYs4FGm1LFT9zJRw` | Đã tạo; avatar logo mảnh ghép mới và banner đã hiện trên trang kênh (18/10) | Google studio đã đối chiếu | Video đầu tiên |
| TikTok | [KV Apps · @khanhvuapps](https://www.tiktok.com/@khanhvuapps) | Tên KV Apps, bio và avatar logo mảnh ghép mới nền trắng đã lưu; kiểm tra profile sau reload (18/10) | Google studio; đã thấy TikTok trong Google Linked apps | Video đầu tiên; loại tài khoản chưa xác minh |
| Instagram | [KV Apps · @khanhvuapps](https://www.instagram.com/khanhvuapps/) | Đã chuyển Business, category Software; logo mới và bio đã lưu | Email studio đã đối chiếu trong Accounts Center | Website trong trường Links đã lưu qua Meta Business Suite và xác nhận trên profile sau reload; nút contact cần kiểm tra trong app mobile |
| Threads | [KV Apps · @khanhvuapps](https://www.threads.com/@khanhvuapps) | Đã tạo profile public; bio, logo mới kế thừa từ Instagram và link website riêng đã kiểm tra sau reload (18/10) | Instagram `khanhvuapps` | Bài đầu tiên |
| Meta Business Suite | [Business Suite](https://business.facebook.com/) | Đã đăng nhập bằng Instagram studio và thấy dashboard @khanhvuapps | Instagram `khanhvuapps` | Chưa có Facebook Page được kết nối; luồng Connect Facebook Page chưa hoàn tất |
| Meta for Developers | [Cổng ứng dụng](https://developers.facebook.com/apps/) cho Instagram/Threads | Tạm dừng: chưa tạo app; Facebook cá nhân dùng để vào cổng đã bị khoá (19/10) | Chưa có tài khoản quản trị khả dụng; email liên hệ dự kiến `khanhvu.dev@gmail.com` | Chờ kết quả kháng nghị Facebook. Không tạo Facebook mới để lách khoá. Xem [checklist](META_SETUP.md) |
| Facebook cá nhân | Tài khoản thật của chủ studio | Đăng ký 18/10; chủ studio báo tài khoản đã bị khoá vĩnh viễn (19/10). Chưa ghi nhận lý do Facebook nêu hay kết quả kháng nghị | Chủ studio | Kháng nghị nếu Facebook còn cho phép; kiểm tra Instagram/Threads vẫn hoạt động. Không công khai thông tin xác minh cá nhân |
| Facebook Page | Tên dự kiến KV Apps; `facebook.com/khanhvuapps` chưa có trang public (18/10) | Tạm dừng, chưa tạo | Không còn tài khoản quản trị khả dụng | Các lần tạo 18/10 không thành công; Facebook cá nhân sau đó bị khoá vĩnh viễn (19/10). Chỉ quay lại khi khôi phục được tài khoản quản trị hợp lệ |
| Reddit | Tài khoản cá nhân của chủ studio (chưa ghi username) | Chủ studio báo đã đăng ký (19/10); profile chưa thiết lập, chưa kiểm tra public | Chủ studio | Điền profile theo [social kit](../../content/shared/social-kit/README.md#reddit--tài-khoản-cá-nhân-của-developer), ghi username; tham gia thảo luận vài ngày trước bài đầu; xem [hướng dẫn](channels/reddit/README.md) |
| Google Cloud (YouTube API) | Project `kvapps-studio`; app `KV Apps Studio Tools`; client `KV Apps Studio Desktop` | Đã bật cả hai API, app External/Testing với test user studio; OAuth hoàn tất, `upload.py channel` trả đúng KV Apps `UC7kW-0SrYs4FGm1LFT9zJRw`; dashboard hiện Đã kết nối (19/10) | `khanhvu.dev@gmail.com` | Client, token và `.env` chỉ lưu local; chưa thử upload thật hoặc đồng bộ Analytics. Cần bản render được duyệt cho lần upload private đầu. [Thiết lập tool](../../tools/youtube/README.md) |
| Apple Developer | Email studio | Người dùng xác nhận đang dùng email này; chưa audit quyền | `khanhvu.dev@gmail.com` | Kiểm tra lại trong Apple khi thay đổi quyền |
| AdMob | Email studio | Người dùng xác nhận đang dùng email này; chưa audit quyền | `khanhvu.dev@gmail.com` | Giữ seller file hiện có; kiểm tra quyền trực tiếp khi cần |

Không có bài đăng social nào được xác nhận trong phiên thiết lập. Các số view, follower, click và lượt cài còn để trống cho tới khi có dữ liệu thật. Không ghi email Google cá nhân khác vào sổ studio.

## YouTube — đã lưu

- Tên KV Apps, handle `@khanhvuapps`, website “Explore KV Apps” và business contact `khanhvu.dev@gmail.com` đã kiểm tra trên profile.
- Description:

```text
Apps & Games by Khanh Vu.
Small apps. Everyday joy.

Discover practical iOS apps, creative tools and offline games. Watch app demos, quick tutorials, gameplay and updates from KV Apps.

Explore our apps: https://khanhvu-ops.github.io/
Support: khanhvu.dev@gmail.com
```

- Đã thay avatar bằng [logo mới](../../content/shared/logo/avatar-light-1024.png), upload [banner](../../content/shared/social-kit/youtube-banner-2560x1440.jpg), Publish và kiểm tra trang kênh. [Hướng dẫn vận hành](channels/youtube/README.md).
- Ngày 19/10: chủ kênh đã xác nhận ba quyền `youtube.upload`, `youtube.readonly`, `yt-analytics.readonly`. `upload.py auth` thành công và lệnh `channel` gọi API thật trả đúng ID kênh ở trên. Token có refresh token; file client/token và `.env` quyền `0600`, thư mục `.secrets/` quyền `0700`, đều bị Git bỏ qua. Chưa upload video hoặc chạy đồng bộ số liệu thật.

## TikTok — profile

Tên `KV Apps` và bio “iOS apps & offline games by Khanh Vu. Small apps. Everyday joy.” đã hiển thị sau reload. Avatar đã đổi thành [logo mảnh ghép mới nền trắng](../../content/shared/logo/avatar-light-1024.png): chọn PNG trong Edit profile, Apply phần cắt, đợi quay lại form rồi Save qua giao diện trình duyệt trực tiếp. Form đóng, avatar mới xuất hiện trên profile và vẫn còn sau reload; đã kiểm tra trực quan cả avatar chính và avatar ở thanh bên. Không đổi nickname đang có giới hạn tới 25/10. Chưa xác nhận Business account. [Hướng dẫn vận hành](channels/tiktok/README.md).

## Instagram — Business

Đã hoàn tất chuyển loại tài khoản; UI xác nhận “Your Instagram business account is ready”. Trang Professional account lưu category **Software**, email business `khanhvu.dev@gmail.com` và **Display contact info = bật**. Instagram ghi rõ nút liên hệ chỉ hiện trong app mobile. Category label đang ẩn; không thêm số điện thoại hay địa chỉ cá nhân.

Bio đã làm gọn sau khi thêm website vào Links:

```text
Practical iOS apps, creative tools and offline games by Khanh Vu.
Small apps. Everyday joy.
```

Đã thêm `https://khanhvu-ops.github.io/` với title “Explore KV Apps” qua Meta Business Suite → Edit Instagram profile → Edit Links → Add external link → Save. Profile Instagram sau reload có link bấm riêng; không cần thao tác mobile cho mục này. Meta Business Suite có thể còn hiển thị “No links” ngay sau lưu, nên lấy kết quả profile Instagram đã reload làm bằng chứng.

## Threads — đã tạo

Chủ studio đã xác nhận điều khoản ở nút Join Threads. Tạo bằng Instagram `khanhvuapps`, giữ profile **Public**. Đã kiểm tra URL profile, bio, logo mới và website ở trường Links với tiêu đề “Explore KV Apps”; xác nhận link còn hiển thị sau reload. Bio được lưu trước, link được thêm riêng sau đó. Chưa có bài đăng; không tự follow hoặc đăng bài để hoàn thành gợi ý onboarding.

```text
Solo dev building iOS apps & offline games. Notes on shipping, privacy and app marketing. Small apps. Everyday joy.
```

Đã kiểm tra trực quan avatar mảnh ghép mới, kế thừa từ Instagram, cùng bio và link website sau reload.

## Facebook cá nhân — bị khoá (19/10)

Chủ studio báo ngày 19/10/2026 tài khoản Facebook cá nhân đã bị khoá vĩnh viễn. Chưa ghi lý do hay hạn kháng nghị vì chưa thấy thông báo gốc. Hệ quả: Facebook Page, nhóm Facebook VN và Meta for Developers tạm dừng. Instagram, Threads và Meta Business Suite đăng nhập bằng Instagram; cần kiểm tra lại xem việc khoá có ảnh hưởng tới chúng không. Không tạo tài khoản Facebook mới để thay thế: điều khoản Meta cấm việc này sau khi tài khoản bị vô hiệu hoá, và có thể kéo theo các tài khoản liên kết.

## Facebook Page — chưa tạo thành công

Chủ studio đã đồng ý tạo **KV Apps**, category **Software**, bio “Apps & Games by Khanh Vu. Small apps. Everyday joy.” và chấp nhận Pages, Groups and Events Policies tại bước Create Page ngày 18/10/2026.

Đã thử form tạo Page ban đầu, luồng **Pages → Create Page → Public Page → Get started** và nút Create Page qua giao diện trực tiếp. Form xác nhận tên/category hợp lệ; nút có xử lý Loading rồi quay lại form. Chưa quan sát được Page mới hoặc thông báo nêu lý do. Danh sách Pages chưa hiển thị Page quản lý; trình chuyển hồ sơ cũng chưa tải xong. Không suy đoán tài khoản bị hạn chế, thời gian phải chờ hoặc lỗi điều khoản khi UI chưa xác nhận.

Chủ studio đã phản hồi sau khi kiểm tra trực tiếp rằng có thể do tài khoản Facebook mới nên chưa tạo được Page. Đây là nhận định của chủ studio; lần kiểm tra UI tiếp theo vẫn chỉ thấy form, không có thông báo xác nhận nguyên nhân hoặc thời gian chờ. Giữ mục này ở trạng thái chờ kiểm tra lại khi có thay đổi; không đặt mốc mở quyền tạo Page chưa được Facebook xác nhận. Avatar, cover, email, website và username Page chưa được lưu vì chưa có Page để cấu hình. Chưa thêm Facebook lên website; không dùng URL dự kiến như URL đã xác nhận.

## Nội dung và ảnh để hoàn thiện profile

Logo đổi ngày 18/10/2026. [Avatar mới](../../content/shared/logo/avatar-light-1024.png) đã hiện trên YouTube, Instagram, Threads và TikTok; đã kiểm tra logo TikTok vẫn hiển thị sau reload. Không đánh dấu hoàn tất chỉ dựa vào preview trong form upload.

Tên, bio, link, avatar, banner YouTube và cover Facebook cho mọi kênh, kể cả Threads: [content/shared/social-kit/](../../content/shared/social-kit/README.md).

## Quy tắc cập nhật

Sau mỗi thay đổi, kiểm tra profile public rồi cập nhật ngày, URL thực, trạng thái và việc còn lại ở đây. Chỉ thêm link lên website sau khi tài khoản có thật và URL đã kiểm tra. Lưu quyền truy cập, 2FA và thông tin khôi phục trong trình quản lý mật khẩu riêng; tài liệu này không chứa bí mật đăng nhập.
