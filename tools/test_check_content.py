"""Offline tests for check-content.py: each test builds a small fake repo in a temp folder."""

import datetime as dt
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

spec = importlib.util.spec_from_file_location("check_content", Path(__file__).with_name("check-content.py"))
cc = importlib.util.module_from_spec(spec)
sys.modules["check_content"] = cc
spec.loader.exec_module(cc)

NOW = dt.datetime(2026, 10, 30, 12, 0, tzinfo=cc.ICT)
CID = "2026-10-18-decoy-pin-en-v1"
TEMPLATE = """# Video brief

| Trường | Giá trị |
|---|---|
| Creative ID | |
| Trạng thái | Idea / Brief |
| Tình huống người dùng | |
| CTA / URL đích đã xác minh | |
"""
BRIEF = """# Video brief — {cid}

| Trường | Giá trị |
|---|---|
| Creative ID | `{cid}` |
| Trạng thái | {status} |
| Tình huống người dùng | {situation} |
| CTA / URL đích đã xác minh | https://apps.apple.com/app/id6813747332 |

```sh
see [example](not/a/real/file.md)
```
"""
META = """creative_id = "{cid}-hook{v}"

[youtube]
title = "{title} #Shorts"
description = "{desc}\\n\\nVeilnest on the App Store: {link}"
{synthetic}
"""
RENDER = """creative_id = "{cid}"

[[variant]]
id = "a"
hook = "Two PINs. Two different vaults."
meta = "youtube-a.toml"

[[text]]
text = "{label}"
start = 10.0
end = 13.0
"""
PLAN = """# Plan

| Ngày | Video | Hook | Kênh | Cộng đồng | Trạng thái |
|---|---|---|---|---|---|
| 4 | decoy-pin EN | A · {hook} | Shorts | — | Chưa quay |

| Video | Caption TikTok / Reels |
|---|---|
| decoy-pin | `{caption}` |
"""
POSTS = """# Nhật ký TikTok

| Ngày giờ + múi giờ | App | Creative ID / phiên bản | URL bài đăng | Kết quả 24h / 7d · nguồn |
|---|---|---|---|---|
{rows}
"""


class Repo:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp())
        self.dir = self.root / "content/veilnest/videos" / CID
        self.write("docs/templates/VIDEO_BRIEF.md", TEMPLATE)
        self.brief()
        self.meta()
        self.write(f"content/veilnest/videos/{CID}/render.toml",
                   RENDER.format(cid=CID, label="Decoy vault · Veilnest Pro"))
        self.plan()
        self.write("docs/content/CALENDAR.md", "# Lịch\n")
        self.write("docs/social/channels/tiktok/POSTS.md", POSTS.format(rows=""))

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def brief(self, status="Brief", situation="Decoy PIN (Pro)", cid=CID):
        self.write(f"content/veilnest/videos/{CID}/BRIEF.md", BRIEF.format(cid=cid, status=status, situation=situation))

    def meta(self, v="a", cid=None, title="Two PINs. Two different vaults.", desc="With Veilnest Pro you get a decoy.",
             link="https://apps.apple.com/app/id6813747332", synthetic="synthetic_media = false"):
        self.write(f"content/veilnest/videos/{CID}/youtube-{v}.toml",
                   META.format(cid=cid or CID, v=v, title=title, desc=desc, link=link, synthetic=synthetic))

    def plan(self, hook="Two PINs. Two different vaults.", caption="Decoy vault is a Veilnest Pro feature."):
        self.write("docs/content/VEILNEST_14_DAYS.md", PLAN.format(hook=hook, caption=caption))

    def posts(self, *rows):
        self.write("docs/social/channels/tiktok/POSTS.md", POSTS.format(rows="\n".join(rows)))

    def check(self):
        return cc.Checker(self.root, NOW).run()

    def messages(self, level="error"):
        return [i.message for i in self.check().issues if i.level == level]


class BriefTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def test_clean_fixture_has_no_issues(self):
        self.assertEqual(self.repo.check().issues, [])

    def test_missing_and_empty_fields(self):
        self.repo.write(f"content/veilnest/videos/{CID}/BRIEF.md",
                        "| Trường | Giá trị |\n|---|---|\n| Creative ID | |\n| Trạng thái | Brief |\n")
        errors = self.repo.messages()
        self.assertIn("trường «Creative ID» đang trống", errors)
        self.assertTrue(any("thiếu trường bắt buộc «Tình huống người dùng»" in e for e in errors))

    def test_unknown_status_and_annotated_status(self):
        self.repo.brief(status="Done")
        self.assertTrue(any("trạng thái «Done»" in e for e in self.repo.messages()))
        self.repo.brief(status="Brief (blocked)")
        self.assertEqual(self.repo.messages(), [])

    def test_creative_id_must_match_folder(self):
        self.repo.brief(cid="something-else")
        self.assertTrue(any("khác tên thư mục" in e for e in self.repo.messages()))

    def test_published_needs_a_post(self):
        self.repo.brief(status="Published")
        self.assertTrue(any("chưa có dòng nào" in e for e in self.repo.messages()))
        self.repo.posts(f"| 2026-10-29 20:00 ICT | Veilnest | {CID}-hooka | https://tiktok.com/x | |")
        self.assertEqual(self.repo.messages(), [])


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def test_pro_feature_needs_pro_in_metadata(self):
        self.repo.meta(desc="A decoy vault with its own PIN.")
        self.assertTrue(any("không ghi «Pro»" in e for e in self.repo.messages()))

    def test_pro_word_must_be_whole(self):
        self.repo.meta(desc="Protect your photos.")
        self.assertTrue(any("không ghi «Pro»" in e for e in self.repo.messages()))

    def test_non_pro_brief_needs_nothing(self):
        self.repo.brief(situation="Private camera")
        self.repo.meta(desc="A camera that saves to the vault.")
        self.repo.write(f"content/veilnest/videos/{CID}/render.toml", RENDER.format(cid=CID, label="Camera"))
        self.assertEqual(self.repo.messages(), [])

    def test_pro_feature_needs_pro_on_video(self):
        self.repo.write(f"content/veilnest/videos/{CID}/render.toml", RENDER.format(cid=CID, label="Decoy vault"))
        self.assertTrue(any("hook/text/end card" in e for e in self.repo.messages()))

    def test_wrong_app_store_link(self):
        self.repo.meta(link="https://apps.apple.com/us/app/veilnest/id6000000000")
        self.assertTrue(any("khác link veilnest" in e for e in self.repo.messages()))

    def test_campaign_query_is_allowed(self):
        self.repo.meta(link="https://apps.apple.com/app/id6813747332?ppid=abc&ct=yt")
        self.assertEqual(self.repo.messages(), [])

    def test_missing_synthetic_media(self):
        self.repo.meta(synthetic="")
        self.assertTrue(any("synthetic_media" in e for e in self.repo.messages()))

    def test_creative_id_must_include_hook(self):
        self.repo.meta(cid=CID + "-hookb")
        self.assertTrue(any("phải là «2026-10-18-decoy-pin-en-v1-hooka»" in e for e in self.repo.messages()))

    def test_hook_must_match_title(self):
        self.repo.meta(title="Two PINs, two vaults")
        self.assertTrue(any("khác tiêu đề YouTube" in e for e in self.repo.messages()))

    def test_meta_without_variant_is_a_warning(self):
        self.repo.meta(v="b", title="Other hook")
        self.assertEqual(self.repo.messages(), [])
        self.assertTrue(any("youtube-b.toml" in w for w in self.repo.messages("warning")))


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def test_plan_hook_must_match_render(self):
        self.repo.plan(hook="Two PINs")
        self.assertTrue(any("khác render.toml" in e for e in self.repo.messages()))

    def test_caption_for_pro_feature(self):
        self.repo.plan(caption="Two PINs. Two vaults.")
        self.assertTrue(any("caption decoy-pin" in e for e in self.repo.messages()))


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def test_broken_link_and_anchor(self):
        self.repo.write("docs/a.md", "[x](missing.md) [y](b.md#khong-co) [ok](b.md#nhóm-thủ-thuật) "
                        "`[code](nope.md)` [web](https://example.com) [self](#tiêu-đề)\n\n# Tiêu đề\n")
        self.repo.write("docs/b.md", "## Nhóm Thủ thuật\n")
        errors = self.repo.messages()
        self.assertIn("link hỏng: missing.md", errors)
        self.assertIn("không có tiêu đề #khong-co: b.md#khong-co", errors)
        self.assertEqual(len(errors), 2)

    def test_link_leaving_repo(self):
        self.repo.write("docs/a.md", "[x](../../../../etc/hosts)\n")
        self.assertTrue(any("ra ngoài repo" in e for e in self.repo.messages()))


class PostTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def test_result_reminders(self):
        self.repo.posts(
            "| 2026-10-29 08:00 ICT | Veilnest | a | u | |",                       # 28 h, empty
            "| 2026-10-29 20:00 ICT | Veilnest | b | u | |",                       # 16 h, not due
            "| 2026-10-20 08:00 +07:00 | Veilnest | c | u | 24h: 300 view · TikTok |",  # 10 d, no 7d
            "| 20/10/2026 08:00 | Veilnest | d | u | 24h: 300 / 7d: 900 · TikTok |",
            "| 2026-10-20 01:00 UTC | Veilnest | e | u | chưa có / chưa có |",
            "| 2026-10-20 | Veilnest | f | u | [báo cáo](../../../templates/POST_REPORT.md) |",
        )
        warnings = self.repo.messages("warning")
        self.assertEqual(len(warnings), 2, warnings)
        self.assertIn("đã đăng 28 giờ, cột kết quả 24h còn trống", warnings)
        self.assertIn("đã đăng 10 ngày, cột kết quả chưa có số 7d", warnings)

    def test_unreadable_date_is_an_error(self):
        self.repo.posts("| hôm qua | Veilnest | a | u | |")
        self.assertTrue(any("không đọc được ngày giờ" in e for e in self.repo.messages()))

    def test_never_writes_logs(self):
        path = self.repo.root / "docs/social/channels/tiktok/POSTS.md"
        self.repo.posts("| 2026-10-01 08:00 ICT | Veilnest | a | u | |")
        before = path.read_text(encoding="utf-8")
        self.repo.check()
        self.assertEqual(path.read_text(encoding="utf-8"), before)


class OverviewTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def test_overview_reads_manifest_posts_and_plan(self):
        exports = self.repo.dir / "exports"
        exports.mkdir()
        (exports / "master.mov").write_bytes(b"")
        (exports / "render-manifest.json").write_text(json.dumps({
            f"{CID}-hooka.mp4": {"variant": "a", "draft": False}}), encoding="utf-8")
        self.repo.posts(f"| 2026-10-30 08:00 ICT | Veilnest | {CID}-hooka | u | |")
        self.repo.write("content/veilnest/videos/old-pack/README.md", "# Old\n")
        checker = self.repo.check()
        text = cc.markdown_overview(checker)
        self.assertIn(f"| veilnest | {CID} | Brief · Pro | a | exports/master.mov | a | ngày 4 | tiktok |", text)
        self.assertIn("| old-pack | pack nhập (không có BRIEF.md) |", text)
        self.assertIn("<td>Brief · Pro</td>", cc.html_overview(checker))

    def test_html_must_not_land_in_tracked_repo_path(self):
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            code = cc.main(["--root", str(self.repo.root), "--html", str(self.repo.root / "pipeline.html")])
        self.assertEqual(code, 2)
        self.assertFalse((self.repo.root / "pipeline.html").exists())
        out = Path(tempfile.mkdtemp()) / "pipeline.html"
        with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
            code = cc.main(["--root", str(self.repo.root), "--html", str(out), "--now", NOW.isoformat()])
        self.assertEqual(code, 0)
        self.assertIn("<table>", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
