# KV Apps — Studio Hub

Repo chung để vận hành studio **KV Apps — Apps & Games by Khanh Vu**: website, các kênh social và nội dung cho từng app/game. Liên hệ công khai: `khanhvu.dev@gmail.com`.

## Bắt đầu ở đâu?

| Công việc | Nơi quản lý |
|---|---|
| Xem tài khoản, chủ sở hữu và trạng thái thiết lập | [Sổ tài khoản social](docs/social/ACCOUNTS.md) |
| Xem việc cần làm tiếp | [Bảng công việc studio](docs/OPERATIONS.md) |
| Cách kéo user organic, thị trường và nội dung | [Chiến lược social](docs/social/STRATEGY.md) |
| Quản lý YouTube, TikTok, Instagram, Facebook | [Các kênh social](docs/social/channels/README.md) |
| Lên lịch và ghi kết quả đăng bài | [Lịch nội dung](docs/content/CALENDAR.md) |
| Tìm kịch bản, storyboard, video theo app | [Kho nội dung](content/README.md) |
| Sửa trang chủ, privacy, support, terms | [Website](docs/website/README.md) · mã nguồn trong [website/](website/) |
| Đọc hướng dẫn và biểu mẫu | [Chỉ mục tài liệu](docs/README.md) |

## Cấu trúc

```text
website/                  Toàn bộ nội dung được phát hành lên GitHub Pages
docs/
  studio/                 Nhận diện thương hiệu
  social/                 Sổ tài khoản, chiến lược, hướng dẫn và nhật ký từng kênh
  apps/                   Hồ sơ marketing của từng app/game
  content/                Quy trình, lịch nội dung và nguồn tài liệu nhập vào
  templates/              Mẫu brief video và báo cáo bài đăng
  website/                Hướng dẫn bảo trì website và các URL ổn định
content/
  veilnest/videos/        Ba bộ creative đã nhập từ IOS-Vault/Docs/Marketing
  color-meter/videos/    Nội dung Color Meter
  paper-drift/videos/    Nội dung Paper Drift
  shared/                 Tài nguyên dùng chung giữa các app
tools/                    Kiểm tra website và chạy preview
.github/workflows/        Phát hành riêng website/ lên GitHub Pages
```

## Website

Chạy từ gốc repo:

```sh
python3 tools/check-site.py
./tools/preview.sh
```

Preview tại [localhost:8765](http://127.0.0.1:8765/). Có thể truyền port khác: `./tools/preview.sh 8770`.

Website live: [khanhvu-ops.github.io](https://khanhvu-ops.github.io/). Workflow `Deploy studio website` phát hành **chỉ `website/`** khi thư mục này hoặc cấu hình triển khai thay đổi trên `main`; sửa docs/video không cần phát hành lại trang chủ. Có thể chạy thủ công từ Actions. Các URL `/privacy.html`, `/terms.html`, `/support.html`, `/paper-drift.html`, `/app-ads.txt` và `/assets/…` giữ nguyên.

## Quy ước vận hành

- Repo này là nguồn quản lý studio từ **18/10/2026**. Source app vẫn ở repo riêng; ASO gắn với từng bản phát hành vẫn quản lý cùng app, hồ sơ marketing ở đây liên kết tới nguồn đó.
- Tài khoản dùng một nhận diện **KV Apps / @khanhvuapps**; trạng thái thật chỉ cập nhật trong [ACCOUNTS.md](docs/social/ACCOUNTS.md). Chưa tạo tài khoản không đồng nghĩa đã giữ được handle.
- Một creative có một thư mục gốc theo app, dùng lại trên nhiều kênh; nhật ký kênh liên kết đến creative đó. Không sao chép video sang bốn thư mục social.
- Repo **public**: chỉ lưu thông tin vận hành công khai; mật khẩu, OTP, backup code, ngày sinh và thông tin khôi phục giữ trong trình quản lý mật khẩu riêng.
- Các video Veilnest hiện là animatic hoặc bộ nguyên liệu dựng tiếp, chưa có bằng chứng đã đăng. Xem [trạng thái từng bộ](content/veilnest/README.md) trước khi dùng.
