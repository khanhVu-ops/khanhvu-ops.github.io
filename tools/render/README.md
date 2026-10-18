# Render biến thể hook cho video ngắn

`render.py` lấy **một master sạch** (bản dựng chưa có chữ) cùng `render.toml` trong thư mục creative. Với mỗi biến thể hook, tool xuất ra:

- `exports/<creative-id>-hook<x>.mp4`: 1080×1920, H.264 High yuv420p, AAC 48 kHz stereo 192 kbps, `+faststart`. Bản này đăng được ngay lên Shorts, TikTok và Reels.
- `exports/<creative-id>-hook<x>-cover.jpg`: khung hình bìa, mặc định lấy giữa đoạn hook.
- `exports/review/<…>-sheet.jpg`: ảnh tổng hợp các khung chính trên bản đã render, có vẽ vùng UI của TikTok, Reels và Shorts. Khung xanh là chữ nằm trong vùng an toàn, khung đỏ là chữ bị UI che.
- `exports/review/<…>-safezones.mp4` (khi chạy với `--preview`): bản 540×960 có vẽ vùng an toàn, để xem trên điện thoại.
- `exports/render-manifest.json`: thông số thật của từng file (sha256, thời lượng, fps, LUFS, true peak, vị trí từng lớp chữ, master gốc), cùng các cảnh báo.

Chữ được vẽ bằng Pillow thành PNG rồi ghép bằng ffmpeg. Vì vậy vị trí chữ được kiểm tra với vùng an toàn **trước khi** render. Nếu chữ bị UI nền tảng che, tool dừng lại và báo lấn bao nhiêu pixel, ở nền tảng nào.

Toàn bộ `exports/` đã nằm trong gitignore: master và bản render không vào repo public, nên tự sao lưu ở nơi khác.

## Cài một lần

Cần `ffmpeg`/`ffprobe` (`brew install ffmpeg`) và Python 3.11 trở lên.

```sh
uv venv tools/render/.venv
VIRTUAL_ENV=tools/render/.venv uv pip install -r tools/render/requirements.txt
```

Không có `uv` thì dùng `python3 -m venv tools/render/.venv && tools/render/.venv/bin/pip install -r tools/render/requirements.txt`.

## Dùng hằng ngày

```sh
PY=tools/render/.venv/bin/python
DIR=content/veilnest/videos/2026-10-18-decoy-pin-en-v1

# 0. (một lần cho mỗi creative) tạo render.toml từ bảng "Biến thể hook" trong BRIEF.md
$PY tools/render/render.py init $DIR

# 1. Đặt bản dựng sạch vào $DIR/exports/master.mov, rồi kiểm tra bố cục
$PY tools/render/render.py check $DIR

# 2. Bản nháp nhanh để xem nhịp chữ
$PY tools/render/render.py render $DIR --draft

# 3. Bản cuối của mọi biến thể, kèm video có vẽ vùng an toàn để xem trên điện thoại
$PY tools/render/render.py render $DIR --preview

# Chỉ render một biến thể, hoặc nhiều creative một lúc
$PY tools/render/render.py render $DIR --variant b
$PY tools/render/render.py check content/veilnest/videos/2026-10-18-*
```

`check` chạy được cả khi **chưa quay**: nếu chưa có master, tool dựng bố cục trên nền giả, nên có thể duyệt độ dài hook và vị trí chữ trước. Ảnh bố cục ghi vào `exports/review/<creative-id>-layout.jpg`.

Lần render sau sẽ bỏ qua biến thể nào có cấu hình, master, subtitle và ảnh không đổi. Muốn render lại thì thêm `--force`. Cuối mỗi lần chạy, tool in sẵn lệnh `upload.py … --dry-run` để kiểm tra metadata YouTube; tool render không upload gì.

## Master

- Bản dựng **sạch**: đã cắt nhịp, có âm thanh, nhưng chưa có hook hay text overlay. Mọi chữ do tool thêm, nên một master cho ra cả A, B, C và bản dịch.
- Mặc định tool tìm `exports/master.*`. Có nhiều file thì ghi rõ `master = "exports/…"`.
- `fit = "auto"`: master 9:16 được scale thẳng. Tỷ lệ khác, như quay màn hình iPhone 1179×2556, thì đặt giữa khung trên nền chính video làm mờ. Có thể chọn `crop` (cắt cho đầy khung), `pad` (viền đen) hoặc `blur`.
- fps lấy theo master, làm tròn về 24/25/30/50/60. Quay màn hình là variable frame rate, tool chuyển sang khung hình đều.
- Âm thanh được chuẩn hoá hai lượt về **-14 LUFS, true peak -1.5 dBTP**. Đặt `loudness = false` nếu muốn giữ nguyên. Master không có tiếng sẽ được thêm track im lặng, vì một số nền tảng xử lý video không có audio kém.
- **Metadata của master bị xoá** khỏi file xuất, gồm vị trí GPS, model máy và ngày quay mà iPhone ghi vào video.

### HDR

iPhone quay camera ở HDR (HLG) theo mặc định. Đem master HDR xuất ra SDR thì màu sẽ bạc, nên tool từ chối render. Có hai cách xử lý:

1. Tắt *Cài đặt → Camera → Quay video → Video HDR* trước khi quay.
2. Hoặc xuất master SDR từ app dựng: CapCut tắt HDR khi export, iMovie/Photos chọn *Most Compatible*.

`--allow-hdr` bỏ qua bước chặn này, nhưng màu sẽ sai. Quay màn hình là SDR nên không bị ảnh hưởng.

## render.toml

```toml
creative_id = "2026-10-18-decoy-pin-en-v1"   # phải trùng tên thư mục
# master = "exports/master.mov"
# trim = [0.4, 15.4]                          # cắt master, giây
fit = "auto"
loudness = -14.0
platforms = ["tiktok", "reels", "shorts"]     # vùng an toàn phải thoả cả ba

[hook]
duration = 2.0          # hook hiện từ khung đầu tiên, nên ảnh preview của nền tảng cũng có hook
position = "upper"      # top | upper | center | lower | bottom | số 0–1 (tâm theo chiều cao)
style = "hook"

[captions]              # tuỳ chọn: burn subtitle từ SRT
file = "captions.srt"
style = "caption"
position = "lower"

[[variant]]
id = "a"
hook = "Two PINs. Two different vaults."
meta = "youtube-a.toml"  # tool đối chiếu creative_id và tiêu đề với hook
# cover_at = 1.0

[[text]]                # chữ chung cho mọi biến thể
text = "Decoy vault · Veilnest Pro"
start = 10.0
end = 13.0
style = "label"
position = "upper"

[[image]]               # ảnh PNG chồng lên video (sticker, icon…)
file = "assets/badge.png"
start = 3.0
end = 5.0
width = 280
position = "center"

[end_card]              # thẻ kết thúc full-frame: icon, tên app, một dòng phụ, nút CTA
start = 13.0            # end mặc định là hết video
title = "Veilnest"
subtitle = "Private photo vault"
cta = "Search “Veilnest” on the App Store"
icon = "../veilnest-us-pov-v2-2026-10-04/assets/veilnest-icon.png"
# background = "#0b0b10"

[styles.hook]           # tuỳ chỉnh style có sẵn hoặc tạo style mới
size = 80
```

### Style có sẵn

| Style | Trông thế nào | Dùng cho |
|---|---|---|
| `hook` | Chữ đậm màu tối trên các viên trắng bo góc theo từng dòng, giống chữ dựng trong app | Hook 0–2 giây |
| `caption` | Chữ trắng viền đen dày, có bóng | Subtitle, câu thoại |
| `label` | Chữ trắng trên viên đen mờ | Ghi chú sự thật như "Pro", "Demo vault" |
| `outline` | Chữ rất to viền đen, không nền | Câu tuyên bố |
| `cta` | Viên xanh, một dòng | Kêu gọi hành động |

Các khoá chỉnh được: `size`, `weight` (tên biến thể font như `Bold`, `Heavy`), `font`, `font_index`, `color`, `background` (`#rrggbbaa`), `padding_x`, `padding_y`, `radius`, `stroke_width`, `stroke_color`, `shadow`, `line_spacing`, `max_lines`, `max_width`, `fade` (giây; 0 là cắt cứng).

Ngắt dòng: tool ưu tiên ngắt ở dấu câu nếu không làm tăng số dòng ("Two PINs. / Two different vaults."), nếu không thì chia các dòng dài đều nhau. Chữ quá dài so với `max_lines` sẽ được thu nhỏ, tối đa 40%; dài hơn nữa thì tool báo lỗi để bạn rút gọn. Dùng `\n` trong chuỗi để tự xuống dòng. Emoji không burn được vào video; để emoji trong caption bài đăng.

**Font:** mặc định là SF Pro của macOS, hỗ trợ đủ dấu tiếng Việt. Giấy phép SF Pro của Apple chủ yếu dành cho mockup giao diện Apple. Nếu muốn chắc chắn về quyền dùng trong video quảng bá, tải một font OFL (ví dụ Be Vietnam Pro, Inter) vào `content/shared/fonts/` rồi đặt `font = "../../../shared/fonts/<file>.ttf"` trong `[styles.<tên>]`.

## Vùng an toàn

Số đo nằm trong [`safezones.toml`](safezones.toml). Đây là ước lượng thận trọng về vùng UI che: thanh tab trên cùng, cột nút bên phải, tên tài khoản, caption và âm thanh ở dưới. Nền tảng đổi giao diện thường xuyên, nên **xem bản export trên điện thoại thật** và sửa số trong file này nếu khác. Đổi số thì mọi `check`/`render` sau đó dùng số mới.

Overlay PNG để dựng trong CapCut hay app khác nằm ở [content/shared/social-kit/safezones/](../../content/shared/social-kit/safezones/). Tạo lại sau khi sửa số:

```sh
tools/render/.venv/bin/python tools/render/render.py safezones
```

## Test

```sh
tools/render/.venv/bin/python -m unittest discover -s tools/render
```

Test đơn vị chạy offline. Test đầu-cuối cần `ffmpeg`: tool render một master giả 3 giây, kiểm tra kích thước, fps và LUFS, rồi chạy lại để xác nhận bước bỏ qua khi không có gì đổi.
