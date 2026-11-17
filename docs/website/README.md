# Website studio — URL và triển khai

Website tĩnh của Khanh Vu, dùng chung cho các ứng dụng liên kết tới những trang này. Ngày **18/10/2026**, trang chủ được cập nhật theo nhận diện **KV Apps — Apps & Games by Khanh Vu**, thêm Veilnest và Color Meter, hỗ trợ/privacy riêng cho Veilnest và đồng bộ thông tin Paper Drift. Không cần build, framework hoặc JavaScript phía client. Từ 18/10/2026, toàn bộ mã trang và assets nằm trong `website/`; thư mục này là gốc của artifact GitHub Pages, không thêm `/website/` vào URL public.

## Nhận diện và danh mục

- Thương hiệu: **KV Apps**; slogan **Small apps. Everyday joy.**; liên hệ công khai `khanhvu.dev@gmail.com`.
- **Paper Lagoon là sản phẩm chủ đạo từ 17/11/2026:** hero trang chủ dùng icon, gameplay thật và CTA App Store của game. Card game đứng đầu danh sách; link game đứng trước Veilnest ở footer toàn site. Title, mô tả SEO và ảnh chia sẻ trang chủ cũng ưu tiên Paper Lagoon.
- **Veilnest:** App Store US lookup xác nhận version 1.3, seller Van Khanh Vu và ID `6813747332` ngày 18/10/2026. Trang chủ dùng link tải chính xác; support và privacy có anchor `#veilnest`. Copy về vault/PIN/calculator dựa trên listing này; thông tin Firebase dựa trên bootstrap, analytics service và package configuration của repo IOS-Vault.
- **Color Meter:** chưa phát hành; đã gỡ khỏi website công khai theo yêu cầu chủ app ngày 17/11/2026, gồm card, icon giới thiệu, navigation, footer, FAQ và mục privacy riêng. Hai anchor rỗng `support.html#color-meter` / `privacy.html#color-meter` giữ tương thích link cũ. Hồ sơ nội bộ và asset cũ vẫn còn trong repo.
- **Paper Lagoon:** đã có trên App Store cho iPhone/iPad, ID `6820811705`. Apple US Lookup ngày 17/11/2026 xác nhận bản **1.3, 600 màn và 20 đảo**. Trang chủ và trang game có CTA tải trực tiếp; marketing, support, terms và privacy đã bỏ trạng thái đang phát triển cùng nội dung kinh tế/ảnh v5 cũ. [Hồ sơ app](../apps/paper-drift.md).
- Icon sản phẩm được sao chép từ asset catalog của app. `assets/kv-apps.svg` là favicon studio trên cả 6 trang, cùng apple-touch icon `assets/kv-apps-avatar.png`. Logo studio xuất hiện ở header/back-link. Trang chủ và trang game dùng icon Paper Lagoon làm ảnh chia sẻ; các trang hỗ trợ/pháp lý/how-to dùng studio avatar. Cover cũ có Color Meter không còn được tham chiếu trong HTML.

Thông tin tài khoản/chủ sở hữu và các bước social còn lại được quản lý tại [sổ tài khoản](../social/ACCOUNTS.md), không cập nhật song song trong hướng dẫn website.

## Các URL ổn định

| Mục đích | URL |
|---|---|
| Trang chủ / Marketing URL | https://khanhvu-ops.github.io/ |
| Privacy Policy URL | https://khanhvu-ops.github.io/privacy.html |
| Terms link trong app/paywall/description | https://khanhvu-ops.github.io/terms.html |
| Support URL | https://khanhvu-ops.github.io/support.html |
| AdMob seller file | https://khanhvu-ops.github.io/app-ads.txt |
| Hướng dẫn SEO Veilnest | https://khanhvu-ops.github.io/how-to-hide-photos-iphone.html |
| Sitemap / robots | https://khanhvu-ops.github.io/sitemap.xml · /robots.txt |

Các đường dẫn giữ nguyên để app đã phát hành không cần đổi link. Các trang public viết bằng tiếng Anh; hỗ trợ qua email nhận tiếng Anh hoặc tiếng Việt.

### URL dùng cho Paper Lagoon

Từ bản 1.1, game đổi tên thành **Paper Lagoon** (tên App Store `Paper Lagoon: Logic Puzzle`, app ID `6820811705`). Bản 1.3 đã phát hành ngày 17/11/2026. URL, anchor `#paper-drift`, thư mục `assets/paper-drift/` và `app-ads.txt` giữ nguyên để các app đã cài tiếp tục dùng được link cũ.

| Mục đích | URL |
|---|---|
| Marketing URL | https://khanhvu-ops.github.io/paper-drift.html |
| Privacy Policy URL | https://khanhvu-ops.github.io/privacy.html#paper-drift |
| Support URL | https://khanhvu-ops.github.io/support.html#paper-drift |
| Terms | https://khanhvu-ops.github.io/terms.html#paper-drift |

Paper Lagoon 1.3: save local, không account/cloud sync; AdMob/UMP, StoreKit, Firebase Analytics và Firebase Remote Config. Bản Debug dùng test ads, bản Release dùng cấu hình quảng cáo phát hành và Remote Config. Privacy mô tả dữ liệu lưu trên máy, lựa chọn quảng cáo/ATT, analytics, cấu hình từ xa và giới hạn khôi phục. Không có analytics opt-out trong app hiện tại; mua No Ads hoặc từ chối ATT không tự tắt usage analytics. Gameplay không cần mạng; video thưởng và IAP cần mạng. Việc cập nhật website không thay đổi App Store Connect hoặc cấu hình provider. Không thay seller ID trong `app-ads.txt`.

**Ảnh cập nhật 17/11/2026:** `assets/paper-drift/icon-1.3.png`, `gameplay-1.3.webp` và `journey-1.3.webp` lấy từ icon/capture tiếng Anh của repo PaperLagoon (`store-assets/screenshots/source/art/v6/` và `raw-v6/`). Các asset cũ vẫn được giữ để URL đã chia sẻ tiếp tục tồn tại. Không thêm trang public hoặc thay cách deploy.

**Thiết kế (18/10/2026):** các trang studio (index, support, privacy, terms, how-to) dùng chung `assets/site.css`: màu lấy từ logo KV, tự đổi sáng/tối theo hệ thống, header/footer chung, chuyển trang bằng CSS View Transitions, hiện dần khi cuộn bằng scroll-driven animations. Tất cả là CSS, không có JavaScript, font web hay CDN; trình duyệt không hỗ trợ chỉ bỏ qua hiệu ứng, và `prefers-reduced-motion` tắt mọi chuyển động. Paper Drift giữ CSS riêng theo nhận diện game, chỉ thêm cùng kiểu chuyển trang và hiệu ứng nhẹ. Khi thêm trang studio mới: dùng header/footer giống các trang hiện có, nội dung đặt trong `<main class="doc"><div class="container">`.

`index.html` giới thiệu Paper Lagoon trước, sau đó Veilnest; `paper-drift.html` là trang marketing riêng với icon và ảnh native từ project game. Asset được giữ local trong `assets/`; site không thêm script analytics, font/CDN hay embed bên thứ ba.

## Phạm vi nội dung

- **how-to-hide-photos-iphone.html** (18/10/2026): hướng dẫn Hidden album theo [Apple](https://support.apple.com/en-us/104987), giới hạn của nó, rồi Veilnest. Claim Veilnest chỉ lấy từ listing **1.3 đang live** (không nhắc Share extension hay backup cho tới khi bản đó phát hành). Ảnh là screenshot store en-US thu nhỏ trong `assets/veilnest/`. Có JSON-LD `Article` (dữ liệu, không phải script chạy). Thêm trang mới thì thêm vào `sitemap.xml`; `check-site.py` báo lỗi nếu thiếu.

- **privacy.html**: nội dung local và permission; Apple IAP; AdMob/ATT/consent; email hỗ trợ/hosting; retention, deletion và quyền người dùng. Những tính năng tuỳ chọn chỉ áp dụng cho app có tính năng đó. Có notice riêng Paper Lagoon và Veilnest.
- **terms.html**: cho phép công việc cá nhân và thương mại, quyền với nội dung đầu ra, IAP/subscription/lifetime, restore/refund, quảng cáo, consumer rights. Apple Standard EULA là mặc định trừ khi app có custom EULA được cấu hình riêng.
- **support.html**: FAQ Paper Lagoon đứng trước Veilnest, cùng hướng dẫn liên hệ, restore/cancel/refund, local data/backup, permissions và PIN nếu app có.
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
python3 tools/check-site.py
./tools/preview.sh
```

Mở `http://127.0.0.1:8765/`, đọc cả sáu trang ở mobile/desktop và thử liên kết nội bộ, anchor và email.

Remote đã cấu hình cho repo: `khanhVu-ops/khanhvu-ops.github.io`. GitHub Pages dùng **GitHub Actions**, workflow [pages.yml](../../.github/workflows/pages.yml) chỉ upload `website/`, không upload `docs/` hay `content/`. Các file trong GitHub vẫn public theo visibility của repository.

Sau khi chạy kiểm tra và review diff, commit/push lên `main`. Workflow `Deploy studio website` tự chạy khi thay đổi `website/**`, checker hoặc cấu hình workflow; thay đổi docs/video đơn thuần không deploy website. Có thể dùng `workflow_dispatch` để phát hành lại thủ công. Chờ workflow thành công trước khi coi website live đã cập nhật.

Nếu cấu hình lại hosting, Settings → Pages → Source phải là **GitHub Actions**. Chế độ Deploy from branch ở `/` hoặc `/docs` không phục vụ được cấu trúc `website/` này. Không đổi Marketing URL hoặc đưa `/website/` vào App Store/AdMob. Tham khảo [GitHub custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

Preview luôn phục vụ riêng `website/`; không chạy HTTP server ở gốc repo nếu muốn kiểm tra đúng nội dung được deploy.

Sau deploy, kiểm tra HTTPS và nội dung mới tại ba URL pháp lý/hỗ trợ. Với AdMob, Marketing URL phải trỏ về website sở hữu seller file; xác nhận app-ads.txt và app readiness trong AdMob. Chỉ có file app-ads.txt không bảo đảm quảng cáo được phục vụ đầy đủ.

## Nguồn tham chiếu khi sửa ngày 30/09/2026

- [Apple App Review privacy requirements](https://developer.apple.com/app-store/review/): giải thích collection, retention/deletion và lựa chọn người dùng.
- [Apple Standard EULA](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/) và [custom license agreement](https://developer.apple.com/help/app-store-connect/manage-app-information/provide-a-custom-license-agreement): phân biệt giấy phép app với Terms bổ sung.
- [Google ATT/IDFA](https://developers.google.com/admob/ios/privacy/idfa): từ chối ATT không gửi IDFA trong ad request, không có nghĩa dừng mọi data processing.
- [Google ad serving modes](https://developers.google.com/admob/ios/privacy/ad-serving-modes): consent cho quảng cáo là lớp riêng.
- [Google SDK data disclosure](https://developers.google.com/admob/ios/privacy/data-disclosure): dữ liệu SDK cần đối chiếu trên từng app.
- [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement): hosting website.

Các nội dung này không phải xác nhận Apple/Google đã duyệt ứng dụng. Khi tính năng hoặc SDK thay đổi, kiểm tra lại chính sách và khai báo tương ứng.

Color Meter chưa phát hành và đã được gỡ khỏi website ngày 17/11/2026. Khi app được giới thiệu lại, phải đối chiếu notice với bản phát hành thực, gồm Firebase Analytics, Crashlytics, Remote Config và các lựa chọn analytics/diagnostics nếu có.

## Website language

All public pages are English-only static HTML. There is no language switch, translation resource, JavaScript or language preference storage. Existing `?lang=en` or `?lang=vi` links still serve the same English page; section anchors are unchanged. The native Paper Drift app has its own 19-language first-launch picker and saved setting.

## Privacy Paper Drift — nguồn đối chiếu ngày 09/10/2026

- Native source: `AnalyticsBootstrap.swift`, `FBEvent.swift`, `DriftAds.swift`, `DriftStore.swift`, `ProgressStore.swift`, `DriftNotifications.swift`, `GameInfoView.swift`, hai `KVAdsConfig` và `PrivacyInfo.xcprivacy`.
- [Google Mobile Ads data disclosure](https://developers.google.com/admob/ios/privacy/data-disclosure), [UMP choices](https://developers.google.com/admob/ios/privacy), [Firebase Analytics data disclosure](https://support.google.com/analytics/answer/10285841), [Apple App Privacy](https://developer.apple.com/app-store/app-privacy-details/).
- Giữ Color Meter và seller ID. Privacy đã đồng bộ tiếp sau khi native project thêm cấu hình Firebase/ATT; chưa đổi ad unit IDs hoặc App Store Connect.
