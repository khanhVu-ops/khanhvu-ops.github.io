# Prompt cho Meta Muse: hook, caption và nghiên cứu đối thủ

Dùng Muse (gói token mời bạn) cho hai việc tốn token nhưng không cần model mạnh nhất: sinh nhiều biến thể hook/caption từ brief, và đọc review của app đối thủ. Kết quả của Muse là **nháp**: bạn chọn, sửa, rồi đưa vào repo theo mục [Đưa kết quả về repo](#đưa-kết-quả-về-repo). Không có gì từ Muse được đăng thẳng.

Prompt viết bằng tiếng Anh vì đầu ra (hook, caption, review) chủ yếu là tiếng Anh; với brief tiếng Việt, prompt đã dặn Muse viết tiếng Việt.

## Cách dùng

1. Mở **một cuộc chat mới cho mỗi việc** (mỗi brief, hoặc một lần nghiên cứu). Chat dài làm Muse lẫn bối cảnh giữa các creative.
2. Dán [Khối 0 · Bối cảnh Veilnest](#khối-0--bối-cảnh-veilnest) trước, rồi dán prompt của việc cần làm.
3. Với việc 1, dán **toàn bộ nội dung** `content/veilnest/videos/<creative>/BRIEF.md` vào chỗ `<<<BRIEF>>>`.
4. Không dán vào Muse: `.env`, `.secrets/`, file `.p8`, token, số liệu riêng trong `.dashboard/`. Repo IOS-Vault là private; chỉ dán phần copy ASO khi bạn chấp nhận gửi nó lên server Meta.

## Khối 0 · Bối cảnh Veilnest

Dán khối này mở đầu mọi cuộc chat. Cập nhật khi app đổi tính năng (nguồn: `Apps/IOS-Vault/Docs/ASO/locales/en-US/locale.json` và [hồ sơ Veilnest](../apps/veilnest.md)).

~~~text
You are helping a solo iOS developer market his app Veilnest on short-form video and the App Store.
Treat the facts below as the ONLY things the app does. Never claim anything outside them.

APP: Veilnest — private photo & video vault for iPhone. App Store: https://apps.apple.com/app/id6813747332
Developer: Van Khanh Vu (solo developer, studio name KV Apps).

WHAT IT DOES (free):
- Photos and videos live in an encrypted vault behind a 6-digit PIN you choose; optional Face ID / Touch ID.
- Auto-lock, blurred thumbnails, screen privacy cover.
- Import from Photos or Files (import makes a copy; originals stay in Photos until the user deletes them).
- Save from any app via the Share button (Photos, Safari, Files, chat apps) — works even while the vault is locked.
- Calculator cover: in Settings > Panic Protection choose Calculator and turn on face-down or shake. While the vault
  is open, flipping the phone face-down (supported devices) or shaking locks it and shows a WORKING calculator.
  The calculator only does math. It does NOT accept the PIN; you exit the cover and authenticate to reopen.
- Built-in camera: photos, video and document scans go straight into the vault, not the camera roll.
- Edit photos/videos, albums, private notes.
- Free tier: up to 100 items; free notes have a limit.

VEILNEST PRO (always label these "Pro" in any content that shows them):
- Storage beyond 100 items, a separate DECOY vault with its own PIN, private albums, more notes,
  Break-in Alerts (log of failed PIN attempts; intruder photo needs camera access), text search inside photos,
  advanced camera and editing tools. Yearly subscription or one-time Lifetime; never state prices or trial
  terms — say "check the in-app offer".

LIMITS (never contradict):
- Content stays on the iPhone. NO cloud sync, no automatic backup. Encrypted backup is a file the user exports.
- Losing/erasing the device, deleting the app or losing vault access can make content permanently inaccessible.
- The app name stays "Veilnest" even with an alternate icon. It does not disguise itself as a calculator app on
  the Home Screen.
- Never say "hack-proof", "100% secure", "military-grade", "undetectable", "no one can ever find it".
- Never imply spying on, hiding things from, or deceiving a partner, parent or child. Privacy framing only:
  "my photos, my space", lending the phone, showing a picture without exposing the whole camera roll.

CHANNELS:
- TikTok has no link in bio yet: CTA is "Search Veilnest on the App Store".
- YouTube Shorts description may contain the App Store link.
- Threads: solo-developer voice, telling the story of building the app; no hashtag stuffing.
- Videos are real screen recordings of the shipping build with a test vault and demo photos.
  Never write a hook that promises a scene the brief's footage does not show.
~~~

## Việc 1 · Hook và caption từ một brief

Mỗi brief có 3 biến thể A/B/C để so sánh trên cùng footage. Prompt này sinh 15–20 hook theo nhiều góc độ, chọn ra 3 hook khác góc để test có ý nghĩa, rồi viết caption cho từng kênh đúng giới hạn ký tự của dashboard.

~~~text
TASK: Write hook variants and captions for ONE short video. The brief is below between <<< >>>.

Read the brief first: the user situation ("Tình huống người dùng"), the single benefit ("Một lợi ích chính"),
the script table ("Kịch bản"), the target language ("Ngôn ngữ / thị trường thử") and whether a Pro feature is shown.
The footage is fixed. Only the on-screen hook text (first 2 seconds) and the captions change.

STEP 1 — 18 hook candidates, 3 per angle:
  1. POV / situation ("POV: ...")
  2. Relatable moment ("When they ...")
  3. Curiosity / reveal ("Flip my phone and ...")
  4. Problem → fix ("Stop ... / Your camera roll ...")
  5. Contrast ("Looks like X. Actually Y.")
  6. Direct demo statement (plain, what happens on screen)
Rules for every hook:
  - Must describe what the footage actually shows in the first seconds. No promises the video does not deliver.
  - Readable in 2 seconds: max 7 words and max 42 characters including spaces. No emoji. No hashtags.
  - Language: the brief's language. If it is VI, write natural spoken Vietnamese used on TikTok VN, not a
    translation of the English hooks.
  - If the brief shows a Pro feature, the hook or the end text must contain the word "Pro".
  - Follow every LIMIT in the app context above.

STEP 2 — pick A, B, C: three hooks from three DIFFERENT angles, so the test tells us which angle works.
For each, one sentence on why it should stop the scroll.

STEP 3 — for each of A, B, C write:
  - youtube_title: exactly the hook + " #Shorts" (max 100 characters total).
  - youtube_description: 2 short sentences explaining what happens and how the feature really works, then
    "Veilnest on the App Store: https://apps.apple.com/app/id6813747332", then
    "Filmed with a test vault and demo photos.", then 3 hashtags starting with #Shorts. Max 600 characters.
  - tiktok: 80–150 characters, hook rephrased + CTA "Search Veilnest on the App Store" + 3–5 hashtags.
  - instagram: first line (max 125 characters, it is the only part shown before "more") + 1–2 lines + CTA
    "Link in bio" is NOT available, so use "Search Veilnest on the App Store" + 3–5 hashtags. Max 2200 characters.
  - threads: max 500 characters, first person as the solo developer ("I built ..."), no hashtags or one at most.
Count characters and show the count after each field like (123/150).

STEP 4 — output, exactly in this format and nothing else after it:

### Hook candidates
| # | Angle | Hook | Chars |
|---|---|---|---|

### Chosen A/B/C
| Variant | Angle | Hook | Why |
|---|---|---|---|

### render.toml
```toml
[[variant]]
id = "a"
hook = "..."
meta = "youtube-a.toml"
(same for b, c)
```

### Captions
#### A
- youtube_title: ... (n/100)
- youtube_description: ... (n/600)
- tiktok: ... (n/150)
- instagram: ... (n/2200)
- threads: ... (n/500)
(same for B, C)

### Risks
List any hook or caption that is close to a forbidden claim, and why it is still OK or should be dropped.

BRIEF:
<<<BRIEF>>>
~~~

**Muốn thêm biến thể cho video đang thắng** (sau khi dashboard cho thấy một hook tốt): mở chat mới, dán Khối 0, dán brief, rồi thay STEP 1–2 bằng câu sau:

~~~text
Hook "<hook đang thắng>" won on <kênh> (<số liệu: view, % xem hết>). Write 12 new hooks that keep the same angle
and situation but change one thing each: wording, the first word, length, or the point of view. Then pick the
3 most different ones as A, B, C and continue with STEP 3 and STEP 4 unchanged.
~~~

## Việc 2 · Nghiên cứu review của app đối thủ

Mục tiêu: tìm điều người dùng app vault **đang ghét**, kèm trích dẫn thật, để làm hook và ý tưởng ASO. Muse cần đọc được web cho việc này. Nếu nó không mở được trang review, prompt bắt nó nói thẳng thay vì bịa.

~~~text
TASK: Competitor review research for a photo vault app (context above). Use web browsing.

STEP 1 — Find the competitors. Search the US App Store (apps.apple.com) for "photo vault", "hide photos",
"private photo album", "calculator vault", "secret calculator photo". List the 8–10 most prominent iPhone apps
with: app name, developer, App Store URL, rating and rating count if shown. Do not guess any number; write
"not shown" when you cannot see it.

STEP 2 — Read reviews. For each app, read its most recent critical reviews (1–3 stars) on the App Store page
and, where available, Reddit threads (r/privacy, r/iphone, r/ios, r/apple) and app review articles from the last
24 months. Aim for 15+ critical reviews per app.
Hard rules:
  - Quote reviews VERBATIM, max 25 words each, with the source URL. Never paraphrase inside quote marks.
  - If you cannot open a page or reviews are not visible, say so for that app. Never invent a review, a count,
    a date or a username.
  - Keep usernames out of the output.

STEP 3 — Cluster the complaints into themes (for example: lost photos after update or new phone, aggressive
paywall/subscription, ads, crashes, slow import, fake-looking calculator, PIN reset/recovery, no backup,
privacy/data worries, iCloud confusion, broken decoy). For each theme give:
  - how often it appears (count of quotes you collected, across how many apps),
  - 2–3 verbatim quotes with URLs,
  - what users wanted instead (in their words where possible).

STEP 4 — Map each theme to Veilnest using ONLY the app context above:
  - "Veilnest addresses this" (cite which listed feature), or
  - "Partly" (explain the gap), or
  - "Veilnest has the same weakness" (for example: no cloud backup — be honest), or
  - "Unknown".
Never claim Veilnest solves something the context does not list.

STEP 5 — Turn the themes Veilnest addresses into:
  - 10 video hook ideas (max 42 characters, same hook rules as a short video: real, no forbidden claims,
    no competitor names, no attacking other apps),
  - 10 App Store keyword ideas in English (single words or short phrases, lowercase). Exclude every competitor
    name and trademark — Apple rejects them in keywords,
  - 3 promotional text ideas (max 170 characters each) and 3 subtitle ideas (max 30 characters each).

OUTPUT, in this order:
1. Competitor table | App | Developer | URL | Rating | Rating count |
2. Theme table | Theme | Quotes collected | Apps | Veilnest | Note |
3. Per theme: quotes with URLs, what users wanted
4. Hook ideas, keyword ideas, promotional text, subtitle (with character counts)
5. Gaps: pages you could not read, and what a human should check manually
~~~

**Nghiên cứu tiếp theo ngôn ngữ**: chạy lại cùng prompt, đổi bước 1 sang App Store của nước khác (ví dụ `apps.apple.com/de/`, `/jp/`) và thêm "Collect reviews in the local language, quote them in the original language and add an English translation". Ý tưởng keyword cho locale nào thì đối chiếu với `locale.json` của locale đó trước khi sửa.

## Đưa kết quả về repo

**Hook và caption**

1. Chọn A/B/C (giữ hoặc sửa từ bản Muse đề xuất). Cập nhật cả ba chỗ cho khớp nhau, vì `check-content.py` báo lỗi khi lệch:
   - `[[variant]]` trong `render.toml`,
   - bảng **Biến thể hook** trong `BRIEF.md`,
   - `title` trong `youtube-a.toml`, `youtube-b.toml`, `youtube-c.toml` (đúng hook + ` #Shorts`); `description` lấy từ Muse.
2. Caption TikTok/Reels: cập nhật bảng **Caption** trong [VEILNEST_14_DAYS.md](VEILNEST_14_DAYS.md); trang **Đăng bài** của dashboard đọc từ bảng đó và đếm ký tự theo cùng giới hạn. Caption Threads dán tay khi đăng.
3. Chạy `python3 tools/check-content.py`, xem diff, rồi render: `tools/render/.venv/bin/python tools/render/render.py render <thư mục creative> --preview`.
4. Kiểm tra tay trước khi đăng: hook có đúng cảnh trong 2 giây đầu không, có claim nào ngoài Khối 0 không, tính năng Pro có ghi "Pro" chưa.
5. Đăng xong, ghi URL ở trang **Đăng bài**; sau 24h và 7 ngày nhập số ở trang **Số liệu**. Biểu đồ **So sánh hook A/B/C** cho biết góc nào thắng; dùng prompt "thêm biến thể cho video đang thắng" ở trên cho vòng sau.

**Nghiên cứu đối thủ**

1. Lưu kết quả vào `Apps/IOS-Vault/Docs/ASO/measurement/` (repo private) kèm ngày chạy. Không đưa trích dẫn review vào repo public này.
2. Mở vài URL trích dẫn để kiểm tra Muse không bịa. Bỏ mọi chủ đề không có trích dẫn kiểm chứng được.
3. Hook mới: viết thành brief mới trong `content/veilnest/videos/` (chỉ khi có footage thật cho tình huống đó), rồi chạy Việc 1.
4. Keyword và text ASO: sửa trong `locale.json`, chạy `python3 Docs/ASO/tools/aso.py` trong repo IOS-Vault, rồi so và đẩy qua trang **App Store** của dashboard (trạng thái *Local mới hơn*).
