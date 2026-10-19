# KV Studio dashboard (chạy local)

Web dashboard để theo dõi toàn bộ việc marketing: pipeline content, lịch 14 ngày, bộ đăng bài từng kênh, số liệu từng bài, listing App Store (localize, screenshot, gói giá), campaign link App Store, và trạng thái tài khoản.

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
| Danh sách app | `docs/apps/registry.json`: tên, bundle id, App Store ID, repo trong `~/personal`, nơi repo giữ listing | **Có**, khi bạn bấm Liên kết/Thêm hoặc Nhập listing |
| Listing App Store: copy theo locale, screenshot | Repo của từng app (Veilnest: `Apps/IOS-Vault/Docs/ASO/locales/*/locale.json` và `screenshots/<locale>/`; app nhập từ ASC: `AppStore/locales/`) | Chỉ khi bạn bấm **Nhập về repo** (tạo file mới, không ghi đè). Ghi **lên App Store Connect** khi bạn xác nhận |
| Mốc đồng bộ listing (field nào đã khớp/đã đẩy/giữ bản ASC) | `.dashboard/dashboard.db`, bảng `asc_sync` | **Có**, tự động |
| Số liệu chi tiết từng lần đo | `.dashboard/dashboard.db` (SQLite) | **Có**. Thư mục này nằm trong gitignore và **không vào repo public** |

Repo vẫn là nguồn sự thật. Mỗi lần mở trang hoặc bấm làm mới (phím <kbd>R</kbd>), dashboard đọc lại toàn bộ file. Các thay đổi do dashboard ghi là thay đổi Git bình thường: xem diff rồi tự commit.

Muốn sao lưu số liệu riêng thì chép `.dashboard/dashboard.db` ra nơi an toàn. Không commit file này.

## Các trang

- **Tổng quan**: gợi ý việc tiếp theo, suy ra từ lịch, master, render và nhật ký (ví dụ quay master, render hook, đăng ngày N, nhập số 24h còn thiếu). Kèm KPI, pipeline theo trạng thái brief, dải 14 ngày, tình trạng kênh và kết quả `check-content`.
- **Content**: lưới creative có bộ lọc. Bấm một creative để xem brief, từng biến thể (video render xem được ngay, ảnh review vùng an toàn), lệnh render khi chưa có master, và các bài đã đăng.
- **Lịch 14 ngày**: từng ngày cùng hook, kênh, cộng đồng và trạng thái thật (có master / đã render / đã đăng).
- **Đăng bài**: chọn creative, hook và kênh để lấy bộ đăng cho từng kênh: caption có đếm ký tự theo giới hạn nền tảng, tiêu đề và mô tả YouTube (tự thay link App Store bằng campaign link nếu có), file video và nút mở trang đăng. Đăng xong, bấm **Đã đăng xong** rồi dán URL public để ghi vào POSTS.md.
- **Số liệu**: nhập số từ TikTok Studio, Instagram Insights, YouTube Studio hay App Store Connect, hoặc **Đồng bộ YouTube** qua API. Có biểu đồ view theo bài, so sánh hook A/B/C theo view hoặc tỷ lệ xem hết, và lịch sử đo. Ô để trống nghĩa là chưa có số, không được tính là 0.
- **App Store**: chọn app ở thanh trên cùng (mỗi app một thẻ: đã liên kết ASC chưa, có listing trong repo chưa, tìm thấy repo không). Xem độ dài từng field (tên, subtitle, keywords, promotional text, mô tả, What's New) so với giới hạn của Apple và ảnh theo locale. Có API key thì **Tải từ App Store Connect** để biết trạng thái từng field, **Chọn locale cần đẩy**, **Xem trước** danh sách lệnh rồi mới đẩy. Mỗi locale có **Thay screenshot**. **App trên ASC** liệt kê mọi app của team để liên kết vào registry. App đã localize tay trên ASC mà repo chưa có gì thì **Nhập về repo**. Tab **Gói giá** chỉ đọc subscription và IAP kèm giá ở storefront Mỹ.
- **Campaign link**: lưu provider token (`pt`), tạo link theo kênh × ngôn ngữ × creative × hook (`ct` được gợi ý như `yt_shorts_en_decoy-pin_a`, tối đa 40 ký tự), gắn Custom Product Page (`ppid`) khi CPP được duyệt.
- **Kênh & tài khoản**: đọc từ ACCOUNTS.md, kèm trạng thái kết nối YouTube API.

## YouTube

- **Upload private**: dashboard gọi `tools/youtube/upload.py`, nên dùng chung metadata, kiểm tra kênh và sổ UPLOADS.md. Luôn có nút **Kiểm tra (dry-run)** để chạy thử trước. Dashboard **không bao giờ** đặt public hoặc hẹn giờ; việc đó làm trong YouTube Studio hoặc bằng `upload.py --publish-at` (có bước xác nhận riêng).
- **Đồng bộ số liệu**: `youtube_sync.py` chạy bằng `tools/youtube/.venv`, chỉ đọc. Nó lấy view, like và comment, và nếu token có quyền thì lấy thêm thời gian xem, thời lượng xem trung bình và tỷ lệ xem hết từ YouTube Analytics. Mỗi lần đồng bộ được gắn nhãn khoảng đo trung thực: `24h` khi đo trong khoảng 24–36 giờ sau khi đăng, `7d` khi đo trong khoảng 7–7,5 ngày, còn lại là `lifetime`. Video private được bỏ qua.
- Cần làm theo [tools/youtube/README.md](../youtube/README.md): bật thêm **YouTube Analytics API** trong Google Cloud, rồi chạy `upload.py auth` (token cũ phải đăng nhập lại để có quyền `yt-analytics.readonly`).
- Máy studio đã kết nối ngày **19/10/2026**: project `kvapps-studio`, client Desktop, token đủ ba quyền; `upload.py channel` trả đúng KV Apps `UC7kW-0SrYs4FGm1LFT9zJRw`, trang Kênh hiện **Đã kết nối**. Nút upload chỉ bật khi biến thể đang chọn có bản render và metadata; hiện repo chưa có bản render thật. Chưa thử upload hoặc đồng bộ số liệu thật.

## App Store Connect

Trang App Store đọc copy và ảnh từ repo app, không chép vào repo public này. Phần so sánh và đẩy lên App Store Connect gọi API trực tiếp, vẫn bằng thư viện chuẩn (JWT ký bằng `openssl` có sẵn trên macOS), nên không cần venv.

**Cấp key (một lần, Account Holder):** App Store Connect → Users and Access → Integrations → App Store Connect API → **Team Keys** → Generate, quyền **App Manager**. Tải `AuthKey_<KEY_ID>.p8` (chỉ tải được một lần) vào `.secrets/appstore/`, rồi thêm vào `.env`:

```sh
ASC_KEY_ID=…
ASC_ISSUER_ID=…   # ở đầu trang Team Keys
```

Bấm <kbd>R</kbd>; ô kết nối trên trang App Store chuyển xanh.

Server không tự nạp lại code. Sau khi `git pull` hoặc sửa `tools/dashboard/*.py`, trang hiện thanh nhắc khởi động lại: dừng bằng Ctrl+C rồi chạy lại lệnh ở đầu file.

**Trạng thái từng field (và bộ screenshot):**

| Trạng thái | Nghĩa | Đẩy |
|---|---|---|
| Đã khớp | Giống ASC sau khi chuẩn hoá (xuống dòng, khoảng trắng cuối dòng, Unicode, dấu cách trong keyword). Kể cả nội dung bạn dán tay vào ASC | Không gửi gì |
| ASC trống | ASC chưa có nội dung này | Tự chọn |
| Local mới hơn | ASC vẫn đúng như lần khớp trước, chỉ local đổi | Tự chọn |
| ASC sửa tay | ASC đổi sau lần khớp trước (sửa trong App Store Connect) | Chỉ khi tick **Ghi đè** |
| Khác, chưa có mốc | Khác nhau và chưa từng khớp, không rõ bên nào mới hơn (thường là bản upload tay trước khi có dashboard) | Chỉ khi tick **Ghi đè**, hoặc bấm **Giữ bản ASC** |
| Giữ bản ASC | Bạn chọn giữ nội dung trên ASC | Bỏ qua, tới khi local đổi tiếp thì thành Local mới hơn |

Mốc lưu trong `.dashboard/dashboard.db`, ghi tự động mỗi lần đọc thấy hai bên khớp, sau mỗi lệnh đẩy thành công (kể cả khi lệnh sau đó lỗi) và khi bấm Giữ bản ASC. Nhờ vậy đẩy hai lần không gửi trùng, và nội dung bạn sửa tay trên ASC không bị đè âm thầm. Screenshot so khớp bằng MD5 (ASC giữ MD5 của file gốc): cùng file thì khớp dù upload tay; ảnh export lại thì tính là khác. Xoá `.dashboard/` thì mất mốc: field khác nhau quay về *Khác, chưa có mốc*, không có gì bị đẩy tự động.

**Thêm app:** bấm **App trên ASC** → **Liên kết** (app đã có trong registry, khớp theo bundle id) hoặc **Thêm** (app mới; repo được đoán theo bundle id trong `~/personal/Apps`). Dashboard ghi `docs/apps/registry.json`; xem diff rồi commit. Nếu app đã localize tay trên ASC, bấm **Nhập về repo**: dashboard tạo `AppStore/locales/<locale>/locale.json` trong repo app cho từng ngôn ngữ chưa có (không ghi đè file nào) và khai `store` trong registry; mọi field nhập vào ở trạng thái Đã khớp. Đặt `KV_WORKSPACE` trong `.env` nếu các repo không nằm trong thư mục cha của repo này.

**Quy tắc:**

- Mọi lệnh ghi đều hai bước: dashboard đọc lại ASC, lập danh sách lệnh (tạo/sửa ngôn ngữ nào, field nào), bạn xem rồi mới bấm đẩy. Không bao giờ submit review, đổi giá hay phát hành.
- Dashboard luôn so với **version tạo gần nhất**, dù nó đang ở trạng thái nào, và hiện cả version đang bán. Ví dụ 1.4 đang *Waiting for Review*: trang hiện 1.4 (khoá, kèm hướng dẫn Remove from Review nếu cần sửa), không lùi về 1.3 đang bán.
- Mô tả, keywords, What's New và screenshot chỉ sửa được trên version ở *Prepare for Submission* (hoặc bị từ chối, đã rút khỏi review); tên và subtitle cần App Information ở trạng thái chuẩn bị. Khi chỉ có version đang bán, chỉ promotional text sửa được; field bị khoá hiện viền nét đứt kèm lý do.
- Ngôn ngữ mới được tạo ở App Information trước, rồi ở version; privacy URL, support URL và marketing URL chép từ primary locale.
- Field vượt giới hạn bị chặn; sửa trong `locale.json` của repo app rồi chạy `aso.py` như thường lệ.
- Screenshot: kích thước quyết định display type (1206×2622 → `APP_IPHONE_61`, 1320×2868 → `APP_IPHONE_67`…). Thay một locale là xoá bộ cũ cùng display type rồi upload bộ mới, vì mỗi bộ tối đa 10 ảnh. So khớp bằng MD5, nên bấm lại khi ảnh không đổi thì không làm gì.

Cấu trúc listing trong repo app: `locales/<locale>/locale.json` với `metadata.name`, `subtitle`, `keywords`, `promotional_text`, `description`, `whats_new`; ảnh ở `screenshots/<locale>/` theo thứ tự tên file. Khai đường dẫn hai thư mục này trong `store` của registry.

## Bảo mật

- Server chỉ lắng nghe trên `127.0.0.1`. Nó từ chối request có `Host` hoặc `Origin` lạ, nên trang web khác không gọi được API qua trình duyệt của bạn. Lệnh ghi bắt buộc gửi JSON.
- `/media` chỉ phục vụ file nằm trong `content/`; `/asc-shot` chỉ phục vụ ảnh nằm trong thư mục screenshot đã khai của app.
- Không có đăng nhập vì chỉ chạy trên máy bạn. **Không** mở server ra mạng (không đổi host, không port-forward).

## Test

```sh
python3 -m unittest discover -s tools/dashboard
```

Test ghi vào bản sao tạm của POSTS.md và campaign-links.json. `test_appstore.py` chạy mọi lệnh App Store Connect với một server ASC giả trong bộ nhớ (version đang bán + version chuẩn bị, phân trang, upload ảnh nhiều phần, các trạng thái đồng bộ, liên kết app và nhập listing trong một `~/personal` tạm với registry và SQLite riêng) và kiểm chữ ký JWT bằng `openssl`; không gọi tới Apple, không đụng registry hay `.dashboard/` thật. Test server chạy trên một cổng ngẫu nhiên và kiểm tra cả các lớp chặn Host, Origin và đường dẫn.

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
| Trang App Store: đọc copy và ảnh local, kiểm giới hạn | Chạy trên dữ liệu thật của IOS-Vault: 34 locale, 272 ảnh 1206×2622, không field nào vượt giới hạn |
| Registry app, tìm repo khi thư mục đã chuyển nhóm | `docs/apps/registry.json` với 4 app; Veilnest vẫn tìm ra `IOS-Vault` dù chưa chuyển vào `Apps/` |
| Báo lỗi thân thiện khi cổng đã bị dùng | Thử cả hai trường hợp: dashboard đang chạy sẵn và chương trình khác chiếm cổng |

### Chưa chạy được: chờ thiết lập bên ngoài

| Tính năng | Thiếu | Việc cần làm (ai) | Sau khi xong, kiểm tra |
|---|---|---|---|
| **Upload YouTube private** | Bản render thật được duyệt; OAuth đã xong | [Render video](../render/README.md), kiểm tra [metadata YouTube](../youtube/README.md). Chỉ thử upload khi chủ kênh yêu cầu một video cụ thể | Video private hiện trên YouTube Studio, đúng kênh KV Apps; có dòng mới trong UPLOADS.md. Chưa kiểm tra upload thật |
| **Đồng bộ số liệu YouTube** | Video public thật. Token đã có đủ quyền; code `youtube_sync.py` **chưa từng gọi API thật** | Khi có video public, bấm “Đồng bộ YouTube” | Số view khớp YouTube Studio; nhãn `24h`/`7d`/`lifetime` đúng thời điểm đo; thời gian xem và tỷ lệ xem hết có mặt (Analytics có thể trễ 1–2 ngày). Sửa code nếu tên trường API khác |
| **App Store Connect: so sánh, trạng thái đồng bộ, đẩy metadata, thay screenshot, liên kết app, nhập listing, xem gói giá** | API key Team Keys (App Manager). Code **chưa từng gọi API thật**: mới chạy với server ASC giả (`test_appstore.py`, và thử cả luồng trên giao diện, gồm bản dán tay, CRLF, ghi đè, giữ bản ASC, đẩy lần hai không gửi gì) | Chủ tài khoản tạo key, đặt `.p8` + `.env` | Bấm Tải từ ASC: version, trạng thái và copy en-US khớp App Store Connect. Lần đẩy đầu nên chọn một locale ít quan trọng; screenshot lần đầu kiểm display type `APP_IPHONE_61` có đúng ô 6.3" không. Sửa code nếu tên trường API khác |
| **Campaign link được Apple ghi nhận** | Provider token `pt` | Chủ app lấy `pt` trong App Store Connect → Apps → Veilnest → Analytics → Acquisition → Campaigns, nhập ở trang Campaign link, tạo link cho từng kênh × ngôn ngữ | Sau 1–2 ngày có lượt truy cập, campaign xuất hiện trong Analytics → Sources (Apple ẩn số dưới ngưỡng) |
| **Custom Product Page** | CPP chưa được duyệt | Tạo CPP (ví dụ `decoy`, `calculator`) trong App Store Connect; khi duyệt, thêm `ppid` vào link | Link mở đúng trang CPP |
| **Facebook Page** | Page chưa tạo được (xem [ACCOUNTS.md](../../docs/social/ACCOUNTS.md)) | Chủ studio thử tạo lại; cập nhật ACCOUNTS.md | Kênh tự mở khoá trong trang Đăng bài khi trạng thái không còn “Chưa tạo” |

### Chưa làm: giai đoạn sau

| Hạng mục | Điều kiện | Ghi chú triển khai |
|---|---|---|
| Thiết lập Meta app (bắt đầu 19/10) | Chờ Meta cho phép truy cập cổng Developers; chủ studio đã thực hiện bước truy cập | Chưa tạo app/token. [Checklist hiện tại](../../docs/social/META_SETUP.md); chưa tích hợp API Instagram/Threads vào dashboard |
| Instagram Reels + Threads: đăng bài và đọc Insights | Meta app theo từng use case được hỗ trợ, chủ tài khoản là admin/tester; cần kiểm tra Meta có yêu cầu app riêng cho Threads hay không | Thêm `meta_sync.py` theo khuôn `youtube_sync.py`: chỉ đọc trước, token trong `.secrets/`, ghi snapshot nguồn `Instagram API`/`Threads API`. Đăng bài: luôn qua nút xác nhận, mặc định không tự đăng |
| TikTok: đăng bài và đọc số | App TikTok for Developers được duyệt (Content Posting API, `video.list`) | App chưa duyệt chỉ đăng được private. Trong lúc chờ: đăng tay, nhập số tay |
| Tạo gói subscription và đặt giá theo nước | API key như trên | Hiện tab Gói giá chỉ đọc. Tạo subscription cần thêm localization, ảnh review và price point theo từng territory (có equalization); làm sau khi phần listing đã chạy thật |
| Lượt tải theo campaign tự động | App Store Connect API key (Analytics Reports) | Chỉ làm nếu báo cáo tách được theo campaign; cần xác minh trước. Key lưu `.secrets/`, không commit |
| Tự đồng bộ theo lịch | Server phải đang chạy hoặc dùng launchd/cron | Ví dụ chạy sync mỗi sáng; không tự đăng bài |
| Lịch cho Color Meter, Paper Drift | Có brief và lịch như `VEILNEST_14_DAYS.md` | Parser `read_plan` hiện chỉ đọc file Veilnest; tổng quát hoá khi có lịch thứ hai |
| Sao lưu số liệu | — | Hiện chép tay `.dashboard/dashboard.db`; có thể thêm nút export CSV (vào thư mục gitignored) |

### Còn phải kiểm tra trên giao diện

- Nút “Mở thư mục” / “Hiện file trong Finder” (`open -R`), các nút Copy (clipboard) và hộp xác nhận khi xoá: phía API đã có test, nhưng chưa bấm thử trên trình duyệt thật.
- Trên mobile, thanh menu trên cùng hơi tràn và phải kéo ngang. Chấp nhận được vì dashboard dùng chủ yếu trên Mac; nếu cần thì gom bớt icon.
- Sau khi có bài thật: kiểm tra biểu đồ khi có hơn 10 bài, khi một concept có đủ cả A/B/C trên cùng kênh, và khi tên creative dài.
