# Kết nối Meta cho dashboard studio

Cập nhật **19/10/2026**. Chưa có Meta app hoặc token được tạo trong phiên thiết lập. Chủ studio đã thực hiện bước truy cập; kiểm tra lại [Meta for Developers](https://developers.facebook.com/apps/) vẫn chưa vào được danh sách ứng dụng. Chờ thông báo từ Meta trước khi tiếp tục. Trạng thái trong [ACCOUNTS.md](ACCOUNTS.md) là nguồn sự thật; Business Suite đã đăng nhập không đồng nghĩa với app Developer đã được tạo. Không lưu ảnh hoặc dữ liệu xác minh cá nhân trong repo.

## Cấu hình dự kiến

- Tên app dự kiến: **KV Apps Studio Tools**; email liên hệ **khanhvu.dev@gmail.com**.
- Tài khoản cần kết nối: Instagram Business **@khanhvuapps** và Threads **@khanhvuapps**.
- Ưu tiên kết nối đọc hồ sơ, nội dung và Insights cho tài khoản của studio trước. Chọn quyền chính xác theo màn hình Meta hiện hành; chỉ cấp token sau khi chủ studio xác nhận quyền thực tế.
- Kiểm tra use case Instagram và Threads trong form tạo app; nếu Meta yêu cầu app riêng thì ghi từng App ID và vai trò rõ ràng. Chưa xác nhận cả hai use case có thể dùng cùng một app.
- Secret/token chỉ lưu trong `.secrets/` local, file quyền `0600`, thư mục quyền `0700`. Không đưa secret vào website, tài liệu public, ảnh chụp hoặc log Git.

## Các bước còn lại

- [x] Chủ tài khoản thực hiện bước truy cập trực tiếp trên trang ngày 19/10.
- [ ] Meta cho phép truy cập cổng Developers; chỉ kiểm tra lại khi có thông báo hoặc trạng thái thay đổi.
- [ ] Kiểm tra hoặc hoàn tất đăng ký Developer; xác nhận điều khoản tại màn hình chấp nhận nếu Meta yêu cầu.
- [ ] Tạo app theo use case được hỗ trợ; ghi lại tên, App ID, tài khoản quản trị và trạng thái Development thực tế.
- [ ] Cấu hình Instagram Login và Threads tương ứng, thêm tài khoản studio vào vai trò thử nghiệm nếu cần.
- [ ] Chủ studio duyệt quyền OAuth; lưu token local và gọi API đọc để đối chiếu đúng @khanhvuapps.
- [ ] Thêm công cụ đọc Insights và trạng thái kết nối vào dashboard. Hiện dashboard chỉ có API YouTube; Instagram/Threads vẫn nhập số thủ công.
- [ ] Khi có bài thật, đối chiếu số với Insights của nền tảng rồi mới đánh dấu đồng bộ đã kiểm tra.

Việc đăng bài qua API cần luồng riêng và yêu cầu cụ thể của chủ studio; tạo app hoặc cấp quyền không đồng nghĩa với đã đăng nội dung.

## Tài liệu gốc

- [Instagram API do Meta duy trì trên Postman](https://www.postman.com/meta/instagram/folder/6raa77c/instagram-api-with-instagram-login): Instagram Login hỗ trợ tài khoản Professional mà không yêu cầu nối Facebook Page.
- [Threads API do Meta duy trì trên Postman](https://www.postman.com/meta/threads/documentation/dht3nzz/threads-api): hướng dẫn use case Threads, OAuth và các API nội dung. Kiểm tra lại dashboard và tài liệu tại thời điểm cấu hình quyền.
