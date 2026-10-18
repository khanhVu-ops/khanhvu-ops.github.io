# KV Studio dashboard (chạy local)

Web dashboard để theo dõi toàn bộ việc marketing: pipeline content, lịch 14 ngày, bộ đăng bài từng kênh, số liệu từng bài, campaign link App Store, và trạng thái tài khoản.

```sh
python3 tools/dashboard/server.py
```

Lệnh này mở [http://127.0.0.1:8790](http://127.0.0.1:8790) và chỉ cần Python 3.11 trở lên, không phải cài gì thêm. `--port 8800` để đổi cổng, `--no-open` để không tự mở trình duyệt. Dừng bằng Ctrl+C.

## Dữ liệu nằm ở đâu

| Dữ liệu | Nguồn | Dashboard có ghi không |
|---|---|---|
| Creative, hook, metadata YouTube, bản render | `content/<app>/videos/*/` (BRIEF.md, render.toml, youtube-*.toml, `exports/render-manifest.json`) | Không |
| Lỗi/cảnh báo nội dung | `tools/check-content.py`, chạy mỗi lần tải trang | Không |
| Lịch 14 ngày, caption | `docs/content/VEILNEST_14_DAYS.md` | Không |
| Tài khoản | `docs/social/ACCOUNTS.md` | Không. Sửa trực tiếp file này |
| Bài đã đăng | `docs/social/channels/<kênh>/POSTS.md` | **Có**: thêm dòng khi bấm “Đã đăng xong”; ghi cột kết quả 24h/7d khi bấm “POSTS.md” |
| Upload YouTube | `docs/social/channels/youtube/UPLOADS.md` | Qua `upload.py` |
| Campaign link | `docs/social/campaign-links.json` | **Có** |
| Số liệu chi tiết từng lần đo | `.dashboard/dashboard.db` (SQLite) | **Có**. Thư mục này nằm trong gitignore và **không vào repo public** |

Repo vẫn là nguồn sự thật. Mỗi lần mở trang hoặc bấm làm mới (phím <kbd>R</kbd>), dashboard đọc lại toàn bộ file. Các thay đổi do dashboard ghi là thay đổi Git bình thường: xem diff rồi tự commit.

Muốn sao lưu số liệu riêng thì chép `.dashboard/dashboard.db` ra nơi an toàn. Không commit file này.

## Các trang

- **Tổng quan**: gợi ý việc tiếp theo, suy ra từ lịch, master, render và nhật ký (ví dụ quay master, render hook, đăng ngày N, nhập số 24h còn thiếu). Kèm KPI, pipeline theo trạng thái brief, dải 14 ngày, tình trạng kênh và kết quả `check-content`.
- **Content**: lưới creative có bộ lọc. Bấm một creative để xem brief, từng biến thể (video render xem được ngay, ảnh review vùng an toàn), lệnh render khi chưa có master, và các bài đã đăng.
- **Lịch 14 ngày**: từng ngày cùng hook, kênh, cộng đồng và trạng thái thật (có master / đã render / đã đăng).
- **Đăng bài**: chọn creative, hook và kênh để lấy bộ đăng cho từng kênh: caption có đếm ký tự theo giới hạn nền tảng, tiêu đề và mô tả YouTube (tự thay link App Store bằng campaign link nếu có), file video và nút mở trang đăng. Đăng xong, bấm **Đã đăng xong** rồi dán URL public để ghi vào POSTS.md.
- **Số liệu**: nhập số từ TikTok Studio, Instagram Insights, YouTube Studio hay App Store Connect, hoặc **Đồng bộ YouTube** qua API. Có biểu đồ view theo bài, so sánh hook A/B/C theo view hoặc tỷ lệ xem hết, và lịch sử đo. Ô để trống nghĩa là chưa có số, không được tính là 0.
- **Campaign link**: lưu provider token (`pt`), tạo link theo kênh × ngôn ngữ × creative × hook (`ct` được gợi ý như `yt_shorts_en_decoy-pin_a`, tối đa 40 ký tự), gắn Custom Product Page (`ppid`) khi CPP được duyệt.
- **Kênh & tài khoản**: đọc từ ACCOUNTS.md, kèm trạng thái kết nối YouTube API.

## YouTube

- **Upload private**: dashboard gọi `tools/youtube/upload.py`, nên dùng chung metadata, kiểm tra kênh và sổ UPLOADS.md. Luôn có nút **Kiểm tra (dry-run)** để chạy thử trước. Dashboard **không bao giờ** đặt public hoặc hẹn giờ; việc đó làm trong YouTube Studio hoặc bằng `upload.py --publish-at` (có bước xác nhận riêng).
- **Đồng bộ số liệu**: `youtube_sync.py` chạy bằng `tools/youtube/.venv`, chỉ đọc. Nó lấy view, like và comment, và nếu token có quyền thì lấy thêm thời gian xem, thời lượng xem trung bình và tỷ lệ xem hết từ YouTube Analytics. Mỗi lần đồng bộ được gắn nhãn khoảng đo trung thực: `24h` khi đo trong khoảng 24–36 giờ sau khi đăng, `7d` khi đo trong khoảng 7–7,5 ngày, còn lại là `lifetime`. Video private được bỏ qua.
- Cần làm theo [tools/youtube/README.md](../youtube/README.md): bật thêm **YouTube Analytics API** trong Google Cloud, rồi chạy `upload.py auth` (token cũ phải đăng nhập lại để có quyền `yt-analytics.readonly`).

## Bảo mật

- Server chỉ lắng nghe trên `127.0.0.1`. Nó từ chối request có `Host` hoặc `Origin` lạ, nên trang web khác không gọi được API qua trình duyệt của bạn. Lệnh ghi bắt buộc gửi JSON.
- `/media` chỉ phục vụ file nằm trong `content/`.
- Không có đăng nhập vì chỉ chạy trên máy bạn. **Không** mở server ra mạng (không đổi host, không port-forward).

## Test

```sh
python3 -m unittest discover -s tools/dashboard
```

Test ghi vào bản sao tạm của POSTS.md và campaign-links.json. Test server chạy trên một cổng ngẫu nhiên và kiểm tra cả các lớp chặn Host, Origin và đường dẫn.

## Giai đoạn sau

Instagram và Threads (đăng bài + Insights) cần một Meta app. TikTok cần app được TikTok duyệt. Facebook Page chờ tạo được Page. Trong lúc chờ, đăng tay theo bộ đăng bài và nhập số ở trang Số liệu.
