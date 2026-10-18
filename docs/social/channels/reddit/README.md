# Reddit — cộng đồng

Tài khoản: chưa kiểm tra (xem [sổ tài khoản](../../ACCOUNTS.md)). Nhật ký: [POSTS.md](POSTS.md).

Reddit không phải kênh đăng hằng ngày. Dùng tài khoản cá nhân thật của developer, nói rõ "I made this", trả lời comment, và không đăng cùng một bài vào nhiều subreddit trong cùng ngày. Tài khoản mới hoặc ít karma có thể bị bộ lọc tự động ẩn bài; tham gia thảo luận thật trước vài ngày.

## Trước mỗi bài

1. Đọc rules và sidebar **hôm đăng** (quy tắc thay đổi): có cho self-promotion không, có cần flair, có ngày riêng cho app không, có giới hạn link không.
2. Một bài một app. Nêu rõ giá: miễn phí kèm Pro trả phí.
3. Chỉ nêu tính năng có trong bản đang phát hành.
4. Sau khi đăng, ghi URL vào [POSTS.md](POSTS.md); không xoá rồi đăng lại để lấy vị trí.

## r/iosapps

Ngày 3 trong [lịch 14 ngày](../../../content/VEILNEST_14_DAYS.md).

```text
Title: I made Veilnest, a photo vault with its own PIN and a calculator cover [Free, Pro optional]

Hi r/iosapps, I'm the solo developer.

Veilnest keeps photos and videos in a vault on your iPhone, behind a six-digit PIN that's separate from your phone passcode (Face ID optional). No account.

- In-app camera that saves straight to the vault, not your camera roll
- Optional calculator cover: enable it in Settings, flip the phone face-down and the vault locks behind a working calculator (it only does math, it isn't a PIN pad)
- Pro: more storage, a decoy vault with its own PIN, albums, Break-in Alerts

Honest limits: everything stays on the device, there's no cloud sync, and I can't recover a lost PIN. If the built-in Hidden album is enough for you, that's fine, I wrote a short comparison here: https://khanhvu-ops.github.io/how-to-hide-photos-iphone.html

App Store: https://apps.apple.com/app/id6813747332

I'd really like feedback on onboarding and the cover setup. Happy to answer anything.
```

## r/SideProject

Ngày 8. Kể chuyện làm sản phẩm, không phải quảng cáo tính năng.

```text
Title: I built an iPhone photo vault as a solo dev — what I learned about privacy claims

I've been building Veilnest, an iOS photo vault, on my own. A few things surprised me:

1. The hardest part wasn't encryption, it was not overpromising. The calculator cover is a real calculator, and I had to rewrite the store text several times so nobody thinks typing a PIN into it opens the vault.
2. "No cloud" is a feature and a risk. I now tell people up front that a lost PIN means lost photos.
3. Apple's Hidden album is genuinely good enough for many people, so I wrote a comparison that says so: https://khanhvu-ops.github.io/how-to-hide-photos-iphone.html

Stack: SwiftUI, Swift 6, local storage only. Free with an optional Pro.
App Store: https://apps.apple.com/app/id6813747332

What would you want to know before trusting an app like this with private photos?
```

## Trả lời các thread "how to hide photos on iPhone"

Trả lời câu hỏi trước bằng cách dùng Hidden album (các bước trong [trang hướng dẫn](https://khanhvu-ops.github.io/how-to-hide-photos-iphone.html)). Chỉ nhắc Veilnest khi người hỏi cần PIN riêng hoặc không muốn dùng passcode máy, và ghi "I'm the developer". Không trả lời hàng loạt bằng cùng một đoạn văn.
