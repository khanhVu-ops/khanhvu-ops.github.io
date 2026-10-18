# Upload YouTube Shorts qua API chính thức

`upload.py` upload **một bản export đã duyệt** lên kênh KV Apps bằng YouTube Data API v3 (`videos.insert`), kèm metadata từ file `youtube-*.toml` trong thư mục creative.

- Mặc định **private**. Video chỉ public khi bạn tự thêm `--privacy public` hoặc `--publish-at …` **và** gõ `publish` ở câu hỏi xác nhận. Không có cờ nào bỏ qua câu hỏi này.
- Tool từ chối upload nếu tài khoản đăng nhập không phải kênh trong `YOUTUBE_EXPECTED_CHANNEL_ID`.
- Mỗi lần upload thành công thêm một dòng vào [UPLOADS.md](../../docs/social/channels/youtube/UPLOADS.md).
- Không tạo tài khoản, không đọc mật khẩu. Đăng nhập diễn ra trên trang Google trong trình duyệt của bạn.

## Thiết lập một lần

Chủ kênh tự làm các bước trong Google Cloud Console bằng tài khoản studio `khanhvu.dev@gmail.com`.

1. Tạo project mới (ví dụ `kvapps-studio`) tại [console.cloud.google.com](https://console.cloud.google.com/).
2. **APIs & Services → Library**: bật **YouTube Data API v3**.
3. **Google Auth Platform → Branding/Audience**: loại **External**, giữ trạng thái **Testing**, thêm `khanhvu.dev@gmail.com` vào **Test users**.
4. **Clients → Create client → Desktop app**. Tải JSON về và lưu thành `.secrets/youtube-client.json` ở gốc repo (thư mục này đã gitignore).
5. Tạo môi trường Python và cấu hình:

```sh
uv venv tools/youtube/.venv
VIRTUAL_ENV=tools/youtube/.venv uv pip install -r tools/youtube/requirements.txt
cp .env.example .env
```

Không có `uv` thì dùng `python3 -m venv tools/youtube/.venv && tools/youtube/.venv/bin/pip install -r tools/youtube/requirements.txt`. Cần Python 3.11 trở lên.

6. Đăng nhập. Trình duyệt mở trang Google; chọn tài khoản studio và kênh **KV Apps**. Google sẽ cảnh báo app chưa được xác minh vì đây là app riêng của bạn ở chế độ Testing: chọn *Advanced → Go to … (unsafe)* để tiếp tục.

```sh
tools/youtube/.venv/bin/python tools/youtube/upload.py auth
```

Kết quả phải là `Signed in. Uploads go to KV Apps (UC7kW-0SrYs4FGm1LFT9zJRw).` Token nằm ở `.secrets/youtube-token.json` (quyền 600).

Ở chế độ Testing, Google cho refresh token hết hạn sau khoảng **7 ngày**. Khi tool báo không refresh được token, chạy lại `auth`.

## Dùng hằng ngày

Đặt bản export vào `content/<app>/videos/<creative-id>/exports/` (đã gitignore; tự sao lưu master ở nơi khác).

```sh
PY=tools/youtube/.venv/bin/python
DIR=content/veilnest/videos/2026-10-18-calculator-pov-en-v1

# 1. Kiểm tra file và metadata, không gửi gì
$PY tools/youtube/upload.py upload $DIR/exports/final.mp4 --meta $DIR/youtube-a.toml --dry-run

# 2. Upload private để xem lại trong YouTube Studio
$PY tools/youtube/upload.py upload $DIR/exports/final.mp4 --meta $DIR/youtube-a.toml

# 3. Hoặc hẹn giờ public (upload private, YouTube tự public đúng giờ; tool hỏi xác nhận)
$PY tools/youtube/upload.py upload $DIR/exports/final.mp4 --meta $DIR/youtube-a.toml --publish-at 2026-10-21T08:00:00+07:00

# Xem trạng thái, lịch và xử lý của một video
$PY tools/youtube/upload.py status <video-id>
```

`--dry-run` chạy được cả với `python3` của hệ thống vì không cần thư viện Google.

Tool kiểm tra trước khi gửi: tiêu đề 1–100 ký tự, không có `<` `>`, mô tả ≤ 5000 byte, tổng tag ≤ 500 ký tự, video dọc hoặc vuông, dài ≤ 180 giây (cần `ffprobe`), thời điểm hẹn có múi giờ và cách hiện tại ít nhất 15 phút.

Sau khi video public thật, ghi URL vào [POSTS.md](../../docs/social/channels/youtube/POSTS.md). Thumbnail, playlist và bình luận đầu tiên làm trong YouTube Studio.

## File metadata

```toml
creative_id = "2026-10-18-calculator-pov-en-v1-hooka"

[youtube]
title = "POV: your friend grabs your phone #Shorts"
description = "…"
tags = ["iphone tips", "photo vault"]
category_id = "28"          # Science & Technology
language = "en"
made_for_kids = false
synthetic_media = false     # bắt buộc khai báo; true nếu có cảnh thật được tạo/sửa bằng AI
privacy = "private"
```

`synthetic_media` là trường `status.containsSyntheticMedia` của YouTube. Các pack Veilnest cũ có ảnh AI; nếu video dùng cảnh người/không gian thật do AI tạo, đặt `true`.

## Giới hạn

- Quota: theo [tài liệu `videos.insert`](https://developers.google.com/youtube/v3/docs/videos/insert) hiện hành, upload tính vào hạn mức upload riêng của project. Xem số thật ở **APIs & Services → YouTube Data API v3 → Quotas**.
- Lên lịch dùng `status.publishAt`, chỉ đặt được khi video là private; thời điểm trong quá khứ sẽ public ngay, nên tool chặn.
- YouTube tự xếp video vào Shorts theo tỷ lệ khung và thời lượng; `#Shorts` trong tiêu đề không bắt buộc.
- Tool chỉ phục vụ YouTube. TikTok và Instagram vẫn đăng tay hoặc hẹn giờ trong app của nền tảng; API đăng của hai nền tảng này yêu cầu duyệt app riêng.

## Test

```sh
tools/youtube/.venv/bin/python -m unittest discover -s tools/youtube
```

Test chạy offline: không cần credential, mọi phản hồi YouTube đều là mock.
