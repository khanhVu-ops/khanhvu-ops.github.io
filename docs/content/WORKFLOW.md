# Quy trình nội dung

## Luồng trạng thái

`Idea → Brief → Producing → Review → Ready → Published → Measured → Archived`

Trạng thái mô tả bằng chứng hiện có. `Ready` cần có export cuối đã xem lại; `Published` cần URL public. Các pack nhập từ IOS-Vault hiện thuộc `Producing`, không chuyển sang Ready chỉ vì có file MP4.

## Một creative được quản lý như thế nào?

1. Chọn app và một tình huống. Tạo `content/<app>/videos/<yyyy-mm-dd>-<concept>-<lang>-v<version>/` cùng `BRIEF.md` từ [mẫu](../templates/VIDEO_BRIEF.md). Đây là ngày tạo creative, không tự coi là ngày đăng.
2. Trong brief ghi creative ID, app/build, ngôn ngữ, mục tiêu, hook, CTA, trạng thái, nguồn chứng minh tính năng và `based_on` nếu có.
3. Tổ chức file khi cần: `script.md`, `captions.srt`, `assets/`, `project/`, `exports/`. Không tạo thư mục rỗng cho đủ hình thức. Giữ master sạch, phiên bản có text và subtitle có tên rõ.
   Hook, text overlay, subtitle, end card, chuẩn hoá âm lượng và bản xuất cho Shorts/TikTok/Reels làm bằng [tool render](../../tools/render/README.md): một master sạch tại `exports/master.*` và `render.toml` cho ra mọi biến thể hook, kèm ảnh bìa, ảnh review vùng an toàn và manifest.
4. Review hình, tiếng, subtitle, vùng che bởi UI nền tảng, link đích và hành vi app. Đối chiếu lại build trước khi dùng footage cũ; đánh dấu mockup/AI khi cần để không gây hiểu nhầm.
5. Ghi slot tại [CALENDAR.md](CALENDAR.md), dẫn tới master. Đăng ở kênh đã có quyền sử dụng; nhật ký của kênh lưu URL và bản export thực đã dùng.
6. Cập nhật 24h/7d trong nhật ký hoặc báo cáo theo [mẫu](../templates/POST_REPORT.md), gồm khoảng đo và nguồn. Chỉ ghi chỉ số thật sự lấy được.
7. Tạo biến thể có ID/version riêng nếu đổi hook hoặc bản dịch. Ghi lại điều học được, không ghi view/lượt cài dự đoán thành kết quả.

## Kiểm tra trước khi đăng

Chạy từ gốc repo (chỉ cần Python 3.11+, không cài gì thêm):

```sh
python3 tools/check-content.py
```

Tool chỉ đọc file, không bao giờ sửa brief hay tự điền số liệu. Lỗi in ra stderr và làm lệnh thoát mã 1; chặn đăng cho tới khi sửa xong:

- `BRIEF.md` thiếu hoặc để trống trường của [mẫu brief](../templates/VIDEO_BRIEF.md) (danh sách trường đọc thẳng từ mẫu); Creative ID khác tên thư mục; trạng thái không bắt đầu bằng một trong `Idea/Brief/Producing/Review/Ready/Published/Measured/Archived` (ghi chú sau đó được phép, ví dụ `Brief (blocked)`). `Published`/`Measured` mà chưa có dòng nào trong `POSTS.md` của kênh cũng là lỗi.
- Brief có chữ `Pro` (cả từ, phân biệt hoa thường) ở bảng trường mà `youtube-*.toml` không ghi `Pro` trong title hoặc description, `render.toml` không có `Pro` ở hook/text/end card, hoặc caption trong [lịch 14 ngày](VEILNEST_14_DAYS.md) thiếu `Pro`.
- Link App Store của Veilnest (trong `content/veilnest/` và `docs/apps/veilnest.md`) khác `https://apps.apple.com/app/id6813747332`. Query campaign/CPP (`?ppid=…&ct=…`) được phép.
- `youtube-<x>.toml` thiếu `synthetic_media` hoặc `creative_id` khác `<thư mục>-hook<x>`; `render.toml` có `creative_id` khác tên thư mục, hoặc hook của biến thể khác tiêu đề YouTube (bỏ ` #Shorts`). Hook `A · …` trong lịch 14 ngày cũng phải khớp `render.toml`.
- Link Markdown nội bộ trong `docs/` và `content/` trỏ tới file hoặc tiêu đề (`#anchor`) không có, hoặc ra ngoài repo. Link trong code block và file gitignored được bỏ qua.

Cảnh báo không làm lệnh thất bại: bài trong `docs/social/channels/*/POSTS.md` đã quá 24 giờ mà cột "Kết quả" trống, hoặc quá 7 ngày mà chưa có số 7d. Quy ước để tool đọc được:

- Cột đầu là ngày giờ đăng: `2026-10-20 08:00 ICT`, `2026-10-20 08:00 +07:00`, `2026-10-20 01:00 UTC` hoặc `20/10/2026 08:00`. Không ghi múi giờ thì hiểu là giờ Việt Nam. Không đọc được ngày là lỗi.
- Cột kết quả: `24h: … / 7d: … · nguồn`. Có phần `7d`/`7 ngày`, có hai phần cách nhau bằng ` / `, hoặc có link tới file báo cáo `.md` thì coi là đã có 7d. `chưa có` là đã kiểm tra nhưng nền tảng chưa có dữ liệu; không điền số 0 cho im cảnh báo.

Sau phần lỗi, tool in ra stdout bảng tổng quan dạng Markdown: mỗi creative ở trạng thái nào, có tính năng Pro không, có hook nào, đã có master `exports/master.*` và bản export trong `exports/render-manifest.json` chưa, nằm ở slot/ngày nào trong lịch, đã đăng kênh nào và đã upload YouTube chưa (đọc từ [UPLOADS.md](../social/channels/youtube/UPLOADS.md)). `exports/` đã gitignore nên cột master/export chỉ đúng với máy đang chạy. Pack nhập không có `BRIEF.md` chỉ được liệt kê, không bị kiểm tra.

```sh
python3 tools/check-content.py --quiet                          # chỉ lỗi và cảnh báo
python3 tools/check-content.py --html media/local/pipeline.html # thêm trang HTML để mở trên máy
python3 tools/check-content.py --now 2026-10-25T09:00+07:00     # xem cảnh báo tại một thời điểm khác
python3 -m unittest tools/test_check_content.py                 # test offline
```

`--html` từ chối ghi vào chỗ trong repo mà Git không ignore, để trang tổng quan không lọt vào repo public. Dùng `media/local/` hoặc đường dẫn ngoài repo.

## Lưu trữ

Git hiện giữ script, asset demo, storyboard và preview của ba pack Veilnest được nhập. Các ZIP và handoff trùng lặp chỉ giữ local, xem [IMPORT.md](IMPORT.md). File GitHub Pages chỉ lấy từ `website/`; creative không xuất hiện trên site nhưng file đã commit vẫn công khai trong GitHub.

Thư mục `exports/` của mọi creative đã gitignore: bản export cuối không vào repo public, nên tự sao lưu ở nơi khác. Với dự án mới, giữ file render có ích cho review ở Git; media thô lớn để ngoài Git hoặc `media/local/` (đã ignore). Ghi nơi lưu trữ trong hệ thống riêng nếu có dữ liệu nhạy cảm. Trước khi thêm file lớn, chọn Git LFS hoặc kho media phù hợp và cập nhật tài liệu; không giả định thư mục ignored được backup khi push.

Các script render nhập từ repo iOS là công cụ sản xuất cũ, không nằm trong workflow phát hành website và chưa được kiểm tra lại khả năng render trong lần chuyển này.
