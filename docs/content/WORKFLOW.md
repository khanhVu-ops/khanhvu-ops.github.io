# Quy trình nội dung

## Luồng trạng thái

`Idea → Brief → Producing → Review → Ready → Published → Measured → Archived`

Trạng thái mô tả bằng chứng hiện có. `Ready` cần có export cuối đã xem lại; `Published` cần URL public. Các pack nhập từ IOS-Vault hiện thuộc `Producing`, không chuyển sang Ready chỉ vì có file MP4.

## Một creative được quản lý như thế nào?

1. Chọn app và một tình huống. Tạo `content/<app>/videos/<yyyy-mm-dd>-<concept>-<lang>-v<version>/` cùng `BRIEF.md` từ [mẫu](../templates/VIDEO_BRIEF.md). Đây là ngày tạo creative, không tự coi là ngày đăng.
2. Trong brief ghi creative ID, app/build, ngôn ngữ, mục tiêu, hook, CTA, trạng thái, nguồn chứng minh tính năng và `based_on` nếu có.
3. Tổ chức file khi cần: `script.md`, `captions.srt`, `assets/`, `project/`, `exports/`. Không tạo thư mục rỗng cho đủ hình thức. Giữ master sạch, phiên bản có text và subtitle có tên rõ.
4. Review hình, tiếng, subtitle, vùng che bởi UI nền tảng, link đích và hành vi app. Đối chiếu lại build trước khi dùng footage cũ; đánh dấu mockup/AI khi cần để không gây hiểu nhầm.
5. Ghi slot tại [CALENDAR.md](CALENDAR.md), dẫn tới master. Đăng ở kênh đã có quyền sử dụng; nhật ký của kênh lưu URL và bản export thực đã dùng.
6. Cập nhật 24h/7d trong nhật ký hoặc báo cáo theo [mẫu](../templates/POST_REPORT.md), gồm khoảng đo và nguồn. Chỉ ghi chỉ số thật sự lấy được.
7. Tạo biến thể có ID/version riêng nếu đổi hook hoặc bản dịch. Ghi lại điều học được, không ghi view/lượt cài dự đoán thành kết quả.

## Lưu trữ

Git hiện giữ script, asset demo, storyboard và preview của ba pack Veilnest được nhập. Các ZIP và handoff trùng lặp chỉ giữ local, xem [IMPORT.md](IMPORT.md). File GitHub Pages chỉ lấy từ `website/`; creative không xuất hiện trên site nhưng file đã commit vẫn công khai trong GitHub.

Với dự án mới, giữ file render có ích cho review ở Git; media thô lớn để ngoài Git hoặc `media/local/` (đã ignore). Ghi nơi lưu trữ trong hệ thống riêng nếu có dữ liệu nhạy cảm. Trước khi thêm file lớn, chọn Git LFS hoặc kho media phù hợp và cập nhật tài liệu; không giả định thư mục ignored được backup khi push.

Các script render nhập từ repo iOS là công cụ sản xuất cũ, không nằm trong workflow phát hành website và chưa được kiểm tra lại khả năng render trong lần chuyển này.
