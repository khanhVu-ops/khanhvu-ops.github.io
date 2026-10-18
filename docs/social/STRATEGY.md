# Kế hoạch organic cho KV Apps

Đây là kế hoạch thử nghiệm, chưa phải kết quả chiến dịch. Mục tiêu ban đầu: tìm tình huống sử dụng và cách mở đầu khiến người xem muốn dùng app; đo tiếp lượt cài và hành vi dùng thật khi có dữ liệu.

## Kênh và thị trường

Giữ một hệ thống KV Apps cho cả tier 1, 2 và 3. Dùng YouTube Shorts, TikTok và Instagram Reels để thử demo ngắn; Facebook Page làm điểm nhận diện, cập nhật và hỗ trợ khi thiết lập xong. Trạng thái tài khoản nằm trong [ACCOUNTS.md](ACCOUNTS.md). Chưa mở thêm nhiều tài khoản theo app hoặc quốc gia.

Sản xuất bản tiếng Anh trước. Khi có creative tốt, thử tiếng Tây Ban Nha, Bồ Đào Nha Brazil, Việt hoặc Indonesia theo dữ liệu territory/ngôn ngữ thực của app. Mỗi bản dịch có caption, text và CTA tương ứng. ASO đa ngôn ngữ tiếp tục ở repo từng app; điều chỉnh social theo listing đã phát hành, không hứa app hỗ trợ ngôn ngữ chưa có.

Ưu tiên thử Veilnest vì đã xác nhận listing; Color Meter cần xác minh link tải; Paper Drift dùng nội dung phát triển/gameplay và chỉ dùng CTA tải khi phát hành. Không mặc định kênh có nhiều view sẽ có nhiều lượt cài.

## Nhịp thử nghiệm 30 ngày

Mức làm việc dự kiến: 60–90 phút/ngày, khoảng **5 creative gốc/tuần**, video dọc 15–25 giây. Điều chỉnh theo sức sản xuất; đây là mục tiêu công việc, không phải cam kết tăng trưởng.

1. Tuần 1: hoàn tất profile, dựng demo thật, thử các tình huống/hook khác nhau cho Veilnest.
2. Tuần 2: giữ phần demo, đổi một yếu tố mỗi biến thể — hook, nhịp dựng hoặc CTA.
3. Tuần 3: làm thêm biến thể của video có tín hiệu tốt; dịch một creative thắng sang ngôn ngữ có cơ sở dữ liệu.
4. Tuần 4: so sánh retention xem video, click và lượt cài; tiếp tục chủ đề có người dùng thật, bỏ chủ đề chỉ tạo view rỗng.

Tái sử dụng cùng creative trên các kênh bằng bản export sạch. Viết caption phù hợp từng nơi, kiểm tra nhạc và quy tắc hiện hành trước khi đăng. Một master video ở `content/<app>/videos/`; nhật ký từng kênh ghi post URL và phiên bản đã dùng.

## Góc nội dung để thử

| App | Tình huống / hook | Bằng chứng cần có trước khi đăng |
|---|---|---|
| Veilnest | Đưa điện thoại cho người khác; không muốn lộ ảnh riêng | Luồng cover → giữ tiêu đề → PIN riêng → vault trong build thực |
| Veilnest | Chụp nội dung trực tiếp vào không gian riêng | Quay lại đúng flow đang phát hành, không khẳng định hành vi chưa kiểm tra |
| Veilnest | Hành động khóa nhanh | Kiểm tra setting và trigger thật trong build dùng quay |
| Color Meter | Một tình huống chọn/đọc màu và kết quả rõ ràng | Chức năng trong build, listing và link tải đúng |
| Paper Drift | Một pha gameplay ngắn, fail/win hoặc mẹo điều khiển | Gameplay thật; phân biệt offline gameplay với dịch vụ cần mạng |

Với Veilnest, calculator dùng để tính toán; số nhập trên calculator **không phải PIN để mở vault**. Không biến một mockup marketing thành bằng chứng app thực hiện được hành vi đó. Các pack hiện tại dùng ảnh AI/UI dựng lại và chưa sẵn sàng đăng như footage app thật.

## Đo và ghi lại

Mỗi post ghi creative ID, app, ngôn ngữ, kênh, thời điểm, URL, CTA và link đích. Sau 24 giờ và 7 ngày ghi số thật từ nền tảng: view, thời gian xem/tỷ lệ xem hết nếu có, profile visit/click nếu có. Ghi nguồn và khoảng thời gian đo; trường không có dữ liệu để “chưa có”, không điền 0.

Dùng campaign link của App Store Connect khi triển khai tracking, phân biệt kênh/ngôn ngữ như `shorts_en`; chỉ đưa link đã tạo thực vào bài. Dữ liệu nền tảng và App Store có cửa sổ đo/điều kiện hiển thị khác nhau, không gán mỗi click thành lượt cài. Các chỉ số mở vault/import/retention cần xác nhận instrumentation trước khi đưa vào báo cáo.

Tham gia cộng đồng bằng câu trả lời hữu ích và nói rõ mình là developer khi nhắc app; kiểm tra quy tắc từng cộng đồng trước khi đặt link. Không dùng fake review hoặc spam comment. Theo dõi ở [lịch nội dung](../content/CALENDAR.md) và [mẫu báo cáo](../templates/POST_REPORT.md).
