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
- Máy studio đã kết nối ngày **19/10/2026**: project `kvapps-studio`, client Desktop, token đủ ba quyền; `upload.py channel` trả đúng KV Apps `UC7kW-0SrYs4FGm1LFT9zJRw`, trang Kênh hiện **Đã kết nối**. Nút upload chỉ bật khi biến thể đang chọn có bản render và metadata; hiện repo chưa có bản render thật. Chưa thử upload hoặc đồng bộ số liệu thật.

## Bảo mật

- Server chỉ lắng nghe trên `127.0.0.1`. Nó từ chối request có `Host` hoặc `Origin` lạ, nên trang web khác không gọi được API qua trình duyệt của bạn. Lệnh ghi bắt buộc gửi JSON.
- `/media` chỉ phục vụ file nằm trong `content/`.
- Không có đăng nhập vì chỉ chạy trên máy bạn. **Không** mở server ra mạng (không đổi host, không port-forward).

## Test

```sh
python3 -m unittest discover -s tools/dashboard
```

Test ghi vào bản sao tạm của POSTS.md và campaign-links.json. Test server chạy trên một cổng ngẫu nhiên và kiểm tra cả các lớp chặn Host, Origin và đường dẫn.

## Trạng thái và việc còn lại

Cập nhật 19/10/2026. Bảng dưới phân biệt rõ phần **đã chạy thật**, phần **chỉ mới test bằng dữ liệu giả** và phần **chưa làm**. Khi một mục xong, chuyển dòng đó sang “Đã chạy”, ghi ngày và cách đã kiểm tra.

### Đã chạy và đã kiểm tra

| Tính năng | Cách đã kiểm tra (19/10/2026) |
|---|---|
| Đọc repo: creative, hook, lịch 14 ngày, ACCOUNTS.md, check-content | Chạy trên repo thật; test `RepoStateTests` |
| Ghi bài đã đăng vào POSTS.md, ghi cột kết quả 24h/7d | Test trên bản sao tạm; thử qua API với dữ liệu giả rồi `git checkout` lại; `check-content.py` đọc đúng định dạng kết quả |
| Nhập, xem, xoá số liệu (SQLite `.dashboard/`) | Test `StoreTests`; thử 4 bài giả trên giao diện rồi xoá DB |
| Biểu đồ view theo bài, so sánh hook A/B/C, lịch sử đo | Xem trên trình duyệt với dữ liệu giả; hiện đang trống vì chưa có bài thật |
| Tạo/xoá campaign link, gợi ý `ct`, URL có `pt`/`ppid` | Test `CampaignTests`; tạo thử một link trên giao diện rồi xoá file |
| Xem video, ảnh bìa, ảnh review vùng an toàn trong Content | Render thử bằng master giả trong `exports/` rồi xoá |
| YouTube **dry-run** (kiểm tra metadata + file, không gửi gì) | Gọi thật qua dashboard, `upload.py` trả “Dry run: … nothing was sent” |
| Kết nối OAuth YouTube | `upload.py auth` lưu token local đủ ba scope và refresh token; `upload.py channel` gọi API thật trả đúng ID KV Apps; trang Kênh hiện Đã kết nối, cả ba điều kiện môi trường/client/token đạt |
| Chặn Host/Origin lạ, chặn đọc file ngoài `content/`, Range cho video | Test `ServerTests` + `curl` |
| Báo lỗi thân thiện khi cổng đã bị dùng | Thử cả hai trường hợp: dashboard đang chạy sẵn và chương trình khác chiếm cổng |

### Chưa chạy được: chờ thiết lập bên ngoài

| Tính năng | Thiếu | Việc cần làm (ai) | Sau khi xong, kiểm tra |
|---|---|---|---|
| **Upload YouTube private** | Bản render thật được duyệt; OAuth đã xong | [Render video](../render/README.md), kiểm tra [metadata YouTube](../youtube/README.md). Chỉ thử upload khi chủ kênh yêu cầu một video cụ thể | Video private hiện trên YouTube Studio, đúng kênh KV Apps; có dòng mới trong UPLOADS.md. Chưa kiểm tra upload thật |
| **Đồng bộ số liệu YouTube** | Video public thật. Token đã có đủ quyền; code `youtube_sync.py` **chưa từng gọi API thật** | Khi có video public, bấm “Đồng bộ YouTube” | Số view khớp YouTube Studio; nhãn `24h`/`7d`/`lifetime` đúng thời điểm đo; thời gian xem và tỷ lệ xem hết có mặt (Analytics có thể trễ 1–2 ngày). Sửa code nếu tên trường API khác |
| **Campaign link được Apple ghi nhận** | Provider token `pt` | Chủ app lấy `pt` trong App Store Connect → Apps → Veilnest → Analytics → Acquisition → Campaigns, nhập ở trang Campaign link, tạo link cho từng kênh × ngôn ngữ | Sau 1–2 ngày có lượt truy cập, campaign xuất hiện trong Analytics → Sources (Apple ẩn số dưới ngưỡng) |
| **Custom Product Page** | CPP chưa được duyệt | Tạo CPP (ví dụ `decoy`, `calculator`) trong App Store Connect; khi duyệt, thêm `ppid` vào link | Link mở đúng trang CPP |
| **Facebook Page** | Page chưa tạo được (xem [ACCOUNTS.md](../../docs/social/ACCOUNTS.md)) | Chủ studio thử tạo lại; cập nhật ACCOUNTS.md | Kênh tự mở khoá trong trang Đăng bài khi trạng thái không còn “Chưa tạo” |

### Chưa làm: giai đoạn sau

| Hạng mục | Điều kiện | Ghi chú triển khai |
|---|---|---|
| Instagram Reels + Threads: đăng bài và đọc Insights | Một Meta app (chế độ dev, chủ tài khoản là admin/tester) với Instagram API (Instagram Login) và Threads API | Thêm `meta_sync.py` theo khuôn `youtube_sync.py`: chỉ đọc trước, token trong `.secrets/`, ghi snapshot nguồn `Instagram API`/`Threads API`. Đăng bài: luôn qua nút xác nhận, mặc định không tự đăng |
| TikTok: đăng bài và đọc số | App TikTok for Developers được duyệt (Content Posting API, `video.list`) | App chưa duyệt chỉ đăng được private. Trong lúc chờ: đăng tay, nhập số tay |
| Lượt tải theo campaign tự động | App Store Connect API key (Analytics Reports) | Chỉ làm nếu báo cáo tách được theo campaign; cần xác minh trước. Key lưu `.secrets/`, không commit |
| Tự đồng bộ theo lịch | Server phải đang chạy hoặc dùng launchd/cron | Ví dụ chạy sync mỗi sáng; không tự đăng bài |
| Lịch cho Color Meter, Paper Drift | Có brief và lịch như `VEILNEST_14_DAYS.md` | Parser `read_plan` hiện chỉ đọc file Veilnest; tổng quát hoá khi có lịch thứ hai |
| Sao lưu số liệu | — | Hiện chép tay `.dashboard/dashboard.db`; có thể thêm nút export CSV (vào thư mục gitignored) |

### Còn phải kiểm tra trên giao diện

- Nút “Mở thư mục” / “Hiện file trong Finder” (`open -R`), các nút Copy (clipboard) và hộp xác nhận khi xoá: phía API đã có test, nhưng chưa bấm thử trên trình duyệt thật.
- Trên mobile, thanh menu trên cùng hơi tràn và phải kéo ngang. Chấp nhận được vì dashboard dùng chủ yếu trên Mac; nếu cần thì gom bớt icon.
- Sau khi có bài thật: kiểm tra biểu đồ khi có hơn 10 bài, khi một concept có đủ cả A/B/C trên cùng kênh, và khi tên creative dài.
