# Việc cần làm — studio

Snapshot **18/10/2026**. Đánh dấu xong sau khi kiểm tra kết quả; trạng thái tài khoản chi tiết cập nhật tại [sổ tài khoản](social/ACCOUNTS.md).

## Thiết lập kênh

- [x] Tạo và kiểm tra YouTube KV Apps bằng Google studio.
- [x] Tạo và kiểm tra handle TikTok `@khanhvuapps` bằng Google studio.
- [ ] Thiết kế/upload avatar và banner YouTube; kiểm tra crop trên mobile.
- [ ] Hoàn tất bio/avatar TikTok; đổi display name KV Apps khi UI cho phép từ 25/10/2026.
- [ ] Chủ tài khoản hoàn tất đăng ký/xác minh Instagram; sau đó kiểm tra profile và quyền quản trị.
- [ ] Chủ tài khoản hoàn tất Facebook cá nhân thật; sau đó tạo Facebook Page KV Apps.
- [ ] Chỉ thêm Instagram/Facebook lên website khi đã có URL xác nhận.

## Nội dung và tăng trưởng

- [x] Đưa ba bộ Veilnest vào kho nội dung studio và ghi nguồn nhập.
- [ ] Chọn một hướng để hoàn thiện: POV v2 hoặc Gemini continuation; không dựng cả hai như cùng một video.
- [ ] Thay UI tham chiếu bằng capture build thực, hoàn tất motion/voice/subtitle, kiểm tra claim và audio.
- [ ] Xác minh listing/download URL Color Meter trước khi dùng CTA tải.
- [ ] Tạo brief đầu tiên cho Color Meter và Paper Drift.
- [ ] Chốt 5 slot thử nghiệm đầu; hiện chưa có ngày đăng được cam kết.
- [ ] Đăng video đầu tiên khi bản cuối đã duyệt; ghi URL thật vào nhật ký kênh.
- [ ] Bổ sung số liệu sau 24 giờ/7 ngày và chọn creative tiếp theo theo dữ liệu.

## Veilnest — 14 ngày (thêm 18/10/2026)

- [x] Viết trang SEO [how-to-hide-photos-iphone.html](../website/how-to-hide-photos-iphone.html), thêm `sitemap.xml`/`robots.txt`. Chưa commit/deploy.
- [x] Lập [lịch 14 ngày](content/VEILNEST_14_DAYS.md), 7 brief và metadata YouTube cho từng hook.
- [x] Viết nháp bài [Reddit](social/channels/reddit/README.md) và [nhóm Facebook VN](social/channels/facebook-groups/README.md).
- [x] Tool [upload YouTube qua API](../tools/youtube/README.md), mặc định private.
- [ ] Chủ kênh tạo OAuth client trong Google Cloud, điền `.env`, chạy `upload.py auth`.
- [ ] Quay 4 master trên build thật bằng vault thử; xuất bản EN và VI.
- [ ] Sau khi deploy trang SEO: gửi `sitemap.xml` trong Google Search Console.
- [ ] Chốt ngày bắt đầu; ghi ngày thật vào lịch 14 ngày.

Các mục trên là backlog. Tool YouTube chỉ upload khi chủ kênh chạy lệnh; không có tác vụ tự đăng.
