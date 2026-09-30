# KV Apps — website và URL dùng chung cho App Store

Website tĩnh của Khanh Vu, dùng chung cho các ứng dụng liên kết tới những trang này. Cập nhật nội dung ngày **30/09/2026**. Không cần build, framework hoặc JavaScript phía client.

## Các URL ổn định

| Mục đích | URL |
|---|---|
| Trang chủ / Marketing URL | https://khanhvu-ops.github.io/ |
| Privacy Policy URL | https://khanhvu-ops.github.io/privacy.html |
| Terms link trong app/paywall/description | https://khanhvu-ops.github.io/terms.html |
| Support URL | https://khanhvu-ops.github.io/support.html |
| AdMob seller file | https://khanhvu-ops.github.io/app-ads.txt |

Các đường dẫn giữ nguyên để app đã phát hành không cần đổi link. Privacy/Terms viết bằng tiếng Anh; Support có phần hướng dẫn tiếng Anh và FAQ tiếng Việt.

## Phạm vi nội dung

- **privacy.html**: nội dung local và permission; Apple IAP; AdMob/ATT/consent; email hỗ trợ/hosting; retention, deletion và quyền người dùng. Những tính năng tuỳ chọn chỉ áp dụng cho app có tính năng đó. Có mục riêng `#color-meter` dựa trên implementation đã kiểm tra.
- **terms.html**: cho phép công việc cá nhân và thương mại, quyền với nội dung đầu ra, IAP/subscription/lifetime, restore/refund, quảng cáo, consumer rights. Apple Standard EULA là mặc định trừ khi app có custom EULA được cấu hình riêng.
- **support.html**: hướng dẫn liên hệ, restore/cancel/refund, local data/backup, permissions, PIN chỉ nếu app có, FAQ riêng Color Meter.
- **index.html**: giới thiệu studio, không khẳng định mọi app là vault, dùng SwiftUI, mã hoá riêng hoặc không có tracking. Không dùng badge tải app dẫn tới trang App Store chung khi chưa có listing cụ thể được xác nhận.
- **app-ads.txt**: thông tin seller hiện có; không đổi trong lần sửa nội dung này.

## Khi gắn URL này cho một app khác

Một URL dùng chung không có nghĩa mọi app có cùng cách xử lý dữ liệu. Trước khi phát hành app mới, kiểm tra:

1. Tên app/chủ thể phát hành khớp KV Apps; app liên kết tới đúng Privacy/Terms/Support.
2. Liệt kê dữ liệu thực xử lý, nơi lưu/gửi, mục đích, recipients, permissions và SDK thực có trong build. Không dùng câu “may use” để che một provider đã biết đang hoạt động.
3. Nếu app có account, cloud, AI/API upload, location, analytics hoặc mediation khác: bổ sung mục riêng trong Privacy nêu dữ liệu, dịch vụ, retention/deletion và control thật trước khi bật tính năng. Nội dung hiện không mặc định khai báo các dịch vụ chưa kiểm tra đó.
4. Kiểm tra backup, Keychain, app PIN và encryption thật. Chỉ ghi zero-knowledge/encrypted vault/recovery khi đã có bằng chứng implementation; không lan claim sang app khác.
5. Kiểm tra trial, plan, entitlement, Family Sharing, restore và refund theo sản phẩm thực. Gói mua ở app A không tự mở app B.
6. App Privacy trong App Store Connect và privacy manifests phải khớp build. Một policy URL không thay thế các khai báo này, UMP hay ATT consent flow.
7. Nếu app dành cho trẻ em hoặc xử lý dữ liệu nhạy cảm khác, bổ sung notice/safeguards phù hợp thay vì tái sử dụng policy general-audience mà không rà soát.
8. Thêm FAQ riêng khi có vấn đề đặc thù; giữ hướng dẫn chung không hứa tính năng chưa có. Cập nhật ngày sửa và thông báo thay đổi quan trọng theo yêu cầu áp dụng.

**License Agreement trong ASC:** link `terms.html` không tự trở thành custom EULA. Mặc định dùng Apple Standard EULA; nếu muốn custom, cần văn bản riêng đáp ứng yêu cầu Apple và cấu hình License Agreement trong ASC. Terms ở repo này được viết dưới dạng điều khoản bổ sung, không tự nhận là custom EULA đã được duyệt.

## Preview và phát hành

Preview local từ thư mục repo:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Mở `http://127.0.0.1:8765/`, đọc cả bốn trang ở mobile/desktop và thử liên kết nội bộ, anchor và email.

Remote đã cấu hình cho repo: `khanhVu-ops/khanhvu-ops.github.io`. Để phát hành thay đổi, review diff rồi commit/push lên branch dùng cho GitHub Pages theo cấu hình thực trong Settings → Pages. Không chạy lại `git init`, đổi remote hay tạo repository mới. Việc sửa file local **chưa** cập nhật website live.

Sau deploy, kiểm tra HTTPS và nội dung mới tại ba URL pháp lý/hỗ trợ. Với AdMob, Marketing URL phải trỏ về website sở hữu seller file; xác nhận app-ads.txt và app readiness trong AdMob. Chỉ có file app-ads.txt không bảo đảm quảng cáo được phục vụ đầy đủ.

## Nguồn tham chiếu khi sửa ngày 30/09/2026

- [Apple App Review privacy requirements](https://developer.apple.com/app-store/review/): giải thích collection, retention/deletion và lựa chọn người dùng.
- [Apple Standard EULA](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/) và [custom license agreement](https://developer.apple.com/help/app-store-connect/manage-app-information/provide-a-custom-license-agreement): phân biệt giấy phép app với Terms bổ sung.
- [Google ATT/IDFA](https://developers.google.com/admob/ios/privacy/idfa): từ chối ATT không gửi IDFA trong ad request, không có nghĩa dừng mọi data processing.
- [Google ad serving modes](https://developers.google.com/admob/ios/privacy/ad-serving-modes): consent cho quảng cáo là lớp riêng.
- [Google SDK data disclosure](https://developers.google.com/admob/ios/privacy/data-disclosure): dữ liệu SDK cần đối chiếu trên từng app.
- [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement): hosting website.

Các nội dung này không phải xác nhận Apple/Google đã duyệt ứng dụng. Khi tính năng hoặc SDK thay đổi, kiểm tra lại chính sách và khai báo tương ứng.
