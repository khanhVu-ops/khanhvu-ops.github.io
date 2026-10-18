# Việc cần làm — studio

Snapshot **19/10/2026**. Đánh dấu xong sau khi kiểm tra kết quả; trạng thái tài khoản chi tiết cập nhật tại [sổ tài khoản](social/ACCOUNTS.md).

## Thiết lập kênh

- [x] Tạo và kiểm tra YouTube KV Apps bằng Google studio.
- [x] Tạo và kiểm tra handle TikTok `@khanhvuapps` bằng Google studio.
- [x] Profile YouTube, TikTok, Instagram đã tạo; tên và bio đã kiểm tra.
- [x] Avatar YouTube và Instagram đã đổi sang logo mảnh ghép mới.
- [x] Đổi avatar TikTok sang logo mảnh ghép mới nền trắng; kiểm tra profile và avatar thanh bên sau reload.
- [x] Upload [banner YouTube](../content/shared/social-kit/youtube-banner-2560x1440.jpg), Publish và kiểm tra trên trang kênh.
- [x] Instagram Business, category Software; lưu email business và bật Display contact info.
- [x] Thêm website vào Links Instagram qua Meta Business Suite; kiểm tra link bấm và bio sau reload.
- [x] Tạo Threads public `@khanhvuapps` từ Instagram; thêm bio và link website riêng.
- [x] Kiểm tra trực quan logo Threads và xác nhận bio/link còn hiển thị sau reload.
- [x] Đăng nhập Meta Business Suite bằng Instagram studio; kiểm tra dashboard @khanhvuapps.
- [ ] Tạo Meta app cho Instagram/Threads: đã mở cổng Developers ngày 19/10; đang chờ chủ tài khoản hoàn tất xác minh trực tiếp. App, token và tích hợp API với dashboard chưa tạo. [Checklist](social/META_SETUP.md).
- [x] Chủ tài khoản hoàn tất Facebook cá nhân thật; đã kiểm tra phiên đăng nhập.
- [ ] Tạo Facebook Page KV Apps; chủ studio đã xác nhận chính sách và đã thử tạo qua các luồng Facebook nhưng vẫn quay lại form. Chủ studio đã kiểm tra trực tiếp, nghi do tài khoản mới; chưa có thông báo Facebook xác nhận lý do/thời gian chờ. Chưa có Page để thêm logo/cover.
- [x] Thêm link Instagram và Threads đã xác nhận lên website.
- [ ] Thêm Facebook lên website sau khi Page có URL xác nhận.

## Nội dung và tăng trưởng

- [x] Chốt [quy trình chăm sóc account có điều kiện](social/ACCOUNT_ROUTINE.md) cho toàn bộ kênh; không đặt lịch lướt/like/follow mặc định hoặc coi đó là điều kiện tăng reach.
- [x] Đưa ba bộ Veilnest vào kho nội dung studio và ghi nguồn nhập.
- [ ] Chọn một hướng để hoàn thiện: POV v2 hoặc Gemini continuation; không dựng cả hai như cùng một video.
- [ ] Thay UI tham chiếu bằng capture build thực, hoàn tất motion/voice/subtitle, kiểm tra claim và audio.
- [ ] Xác minh listing/download URL Color Meter trước khi dùng CTA tải.
- [ ] Tạo brief đầu tiên cho Color Meter và Paper Drift.
- [ ] Chốt 5 slot thử nghiệm đầu; hiện chưa có ngày đăng được cam kết.
- [ ] Đăng video đầu tiên khi bản cuối đã duyệt; ghi URL thật vào nhật ký kênh.
- [ ] Bổ sung số liệu sau 24 giờ/7 ngày và chọn creative tiếp theo theo dữ liệu.

## Veilnest — 14 ngày (thêm 18/10/2026)

- [x] Viết trang SEO [how-to-hide-photos-iphone.html](../website/how-to-hide-photos-iphone.html), thêm `sitemap.xml`/`robots.txt`; đã deploy cùng website.
- [x] Lập [lịch 14 ngày](content/VEILNEST_14_DAYS.md), 7 brief và metadata YouTube cho từng hook.
- [x] Viết nháp bài [Reddit](social/channels/reddit/README.md) và [nhóm Facebook VN](social/channels/facebook-groups/README.md).
- [x] Tool [upload YouTube qua API](../tools/youtube/README.md), mặc định private.
- [x] Tool [render biến thể hook](../tools/render/README.md); mỗi brief 18/10 đã có `render.toml` (thời gian theo kịch bản, chỉnh lại sau khi quay).
- [x] [Dashboard local](../tools/dashboard/README.md): pipeline, lịch, bộ đăng bài, nhật ký bài đăng, số liệu (SQLite gitignored), campaign link.
- [ ] Lấy provider token (`pt`) trong App Store Connect, nhập ở trang Campaign link và tạo link cho từng kênh × ngôn ngữ.
- [ ] Khi có một video public: bấm “Đồng bộ YouTube” và đối chiếu số với YouTube Studio (`youtube_sync.py` chưa từng gọi API thật; token đã có đủ quyền).
- [ ] Dashboard giai đoạn sau: Meta app cho Instagram/Threads, app TikTok được duyệt, tự đồng bộ theo lịch. Chi tiết và điều kiện ở [trạng thái dashboard](../tools/dashboard/README.md#trạng-thái-và-việc-còn-lại).
- [x] Tool [kiểm tra content](content/WORKFLOW.md#kiểm-tra-trước-khi-đăng) (`tools/check-content.py`): chặn thiếu Pro, sai link App Store, lệch hook/creative_id, link hỏng; in tổng quan pipeline.
- [x] Tạo project `kvapps-studio`, bật YouTube Data API v3 và YouTube Analytics API; app External/Testing với test user studio; tạo Desktop client, lưu JSON và `.env` local (19/10/2026).
- [x] Hoàn tất `upload.py auth` bằng Google studio với ba quyền upload/xem tài khoản/đọc Analytics. `upload.py channel` gọi API thật trả đúng KV Apps `UC7kW-0SrYs4FGm1LFT9zJRw`; dashboard hiện Đã kết nối (19/10). Token chỉ lưu local; chưa upload video.
- [ ] Khi có bản render + metadata được duyệt và chủ kênh yêu cầu video cụ thể: thử upload private qua dashboard, kiểm tra YouTube Studio và dòng mới trong UPLOADS.md.
- [ ] Quay 4 master trên build thật bằng vault thử; xuất bản EN và VI.
- [ ] Sau khi deploy trang SEO: gửi `sitemap.xml` trong Google Search Console.
- [ ] Chốt ngày bắt đầu; ghi ngày thật vào lịch 14 ngày.

Các mục trên là backlog. Tool YouTube chỉ upload khi chủ kênh chạy lệnh; không có tác vụ tự đăng.
