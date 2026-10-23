"""Offline tests for the dashboard backend. Writes go to temporary copies; the real repo is only read."""

import datetime as dt
import http.client
import json
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import repo  # noqa: E402
import server  # noqa: E402
import store  # noqa: E402

ICT = dt.timezone(dt.timedelta(hours=7))
STANDARD = """# Nhật ký TikTok

| Ngày giờ + múi giờ | App | Creative ID / phiên bản | Ngôn ngữ | URL bài đăng | Link đích | Kết quả 24h / 7d · nguồn |
|---|---|---|---|---|---|---|

Ghi chú sau bảng.
"""
REDDIT = """# Reddit

| Ngày giờ + múi giờ | Subreddit | App | Loại (bài / trả lời) | URL | Rule đã đọc ngày | Kết quả 24h / 7d · nguồn |
|---|---|---|---|---|---|---|
"""


class TempChannels(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for name, text in (("tiktok", STANDARD), ("reddit", REDDIT)):
            (self.tmp / name).mkdir()
            (self.tmp / name / "POSTS.md").write_text(text, encoding="utf-8")
        patches = [mock.patch.object(repo, "CHANNELS_DIR", self.tmp),
                   mock.patch.object(repo, "CAMPAIGNS", self.tmp / "campaign-links.json")]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(shutil.rmtree, self.tmp)

    def text(self, channel):
        return (self.tmp / channel / "POSTS.md").read_text(encoding="utf-8")


class PostLogTests(TempChannels):
    def test_appends_row_by_header_and_keeps_text_after_table(self):
        repo.append_post("tiktok", {"url": "https://www.tiktok.com/@khanhvuapps/video/1", "when": "2026-10-17T08:00+07:00",
                                    "creative": "2026-10-18-decoy-pin-en-v1-hooka", "lang": "en", "app": "veilnest"})
        text = self.text("tiktok")
        self.assertIn("| 2026-10-17 08:00 ICT | Veilnest | `2026-10-18-decoy-pin-en-v1-hooka` | EN | "
                      "https://www.tiktok.com/@khanhvuapps/video/1 | — |  |", text)
        self.assertTrue(text.rstrip().endswith("Ghi chú sau bảng."))
        posts = repo.read_posts(dt.datetime(2026, 10, 18, 9, tzinfo=ICT))
        self.assertEqual(posts[0]["creative_id"], "2026-10-18-decoy-pin-en-v1")
        self.assertEqual(posts[0]["variant"], "a")
        self.assertEqual(posts[0]["age_hours"], 25.0)

    def test_reddit_columns(self):
        repo.append_post("reddit", {"url": "https://www.reddit.com/r/iosapps/comments/x", "when": "2026-10-17 08:00",
                                    "place": "r/iosapps", "app": "veilnest", "rules_read": "2026-10-16"})
        self.assertIn("| r/iosapps | Veilnest | bài | https://www.reddit.com/r/iosapps/comments/x | 2026-10-16 |", self.text("reddit"))

    def test_refuses_bad_input(self):
        ok = {"url": "https://x.example/1", "when": "2026-10-17 08:00"}
        for bad, message in ((dict(ok, url="http://x"), "https://"), (dict(ok, when="hôm qua"), "không hợp lệ"),
                             (dict(ok, when="2099-01-01 08:00"), "tương lai")):
            with self.assertRaises(repo.RepoError) as ctx:
                repo.append_post("tiktok", bad)
            self.assertIn(message, str(ctx.exception))
        repo.append_post("tiktok", ok)
        with self.assertRaisesRegex(repo.RepoError, "đã có"):
            repo.append_post("tiktok", ok)
        with self.assertRaises(repo.RepoError):
            repo.append_post("myspace", ok)

    def test_write_result_replaces_only_that_cell(self):
        repo.append_post("tiktok", {"url": "https://x.example/1", "when": "2026-10-17 08:00"})
        repo.write_result("tiktok", "https://x.example/1", "24h 1.2k view · TikTok Studio 2026-10-18")
        self.assertIn("| https://x.example/1 | — | 24h 1.2k view · TikTok Studio 2026-10-18 |", self.text("tiktok"))


class CampaignTests(TempChannels):
    def test_add_list_delete(self):
        repo.set_provider_token("123456")
        link = repo.add_campaign({"app": "veilnest", "ct": "yt_shorts_en", "channel": "youtube", "lang": "en"})
        data = repo.read_campaigns()
        self.assertEqual(data["links"][0]["url"],
                         "https://apps.apple.com/app/apple-store/id6813747332?pt=123456&ct=yt_shorts_en&mt=8")
        self.assertNotIn("url", json.loads((self.tmp / "campaign-links.json").read_text())["links"][0])
        with self.assertRaisesRegex(repo.RepoError, "đã tồn tại"):
            repo.add_campaign({"app": "veilnest", "ct": "yt_shorts_en"})
        repo.delete_campaign(link["id"])
        self.assertEqual(repo.read_campaigns()["links"], [])

    def test_validation_and_cpp(self):
        for bad in ({"app": "veilnest", "ct": "has space"}, {"app": "veilnest", "ct": "x" * 41},
                    {"app": "color-meter", "ct": "ok"}, {"app": "veilnest", "ct": "ok", "ppid": "not a uuid!"}):
            with self.assertRaises(repo.RepoError):
                repo.add_campaign(bad)
        with self.assertRaises(repo.RepoError):
            repo.set_provider_token("abc")
        repo.add_campaign({"app": "veilnest", "ct": "tiktok_en", "ppid": "4a1f5b3c-1111-2222-3333-444455556666"})
        self.assertIn("&ppid=4a1f5b3c-1111-2222-3333-444455556666&mt=8", repo.read_campaigns()["links"][0]["url"])

    def test_suggestion(self):
        self.assertEqual(repo.suggest_ct("instagram", "VI", "2026-10-18-hidden-album-vi-v1", "a"), "ig_reels_vi_hidden-album_a")
        self.assertLessEqual(len(repo.suggest_ct("facebook-groups", "en", "2026-10-18-" + "x" * 60 + "-en-v1")), 40)


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.db = Path(tempfile.mkdtemp()) / "d.db"
        self.conn = store.connect(self.db)
        self.addCleanup(self.conn.close)

    def add(self, **kw):
        return store.add_snapshot(self.conn, {"channel": "tiktok", "url": "https://x.example/1", "source": "TikTok Studio", **kw})

    def test_validation(self):
        for kw in ({}, {"views": -1}, {"completion_pct": 120}, {"views": "abc"}, {"views": 5, "window": "1y"}):
            with self.assertRaises(store.StoreError):
                self.add(**kw)
        with self.assertRaises(store.StoreError):
            store.add_snapshot(self.conn, {"channel": "tiktok", "url": "https://x.example/1", "views": 3})  # no source

    def test_blank_stays_missing_not_zero(self):
        self.add(views=1200, likes="")
        row = store.snapshots(self.conn)[0]
        self.assertEqual(row["views"], 1200)
        self.assertNotIn("likes", row)
        self.assertTrue((self.db.parent / ".gitignore").is_file())

    def test_result_text_is_read_by_check_content(self):
        self.add(window="24h", views=1234, completion_pct=42.4, captured_at="2026-10-18T09:00+07:00")
        text = store.result_text(self.conn, "https://x.example/1")
        self.assertEqual(text, "24h 1.2k view, 42% xem hết · TikTok Studio 2026-10-18")
        self.assertEqual(repo.check_content.result_state(text), (True, False))
        self.add(window="7d", views=5600, installs=3, captured_at="2026-10-24T09:00+07:00")
        text = store.result_text(self.conn, "https://x.example/1")
        self.assertTrue(text.startswith("24h 1.2k view, 42% xem hết / 7d 5.6k view, 3 tải · "))
        self.assertEqual(repo.check_content.result_state(text), (True, True))


class RepoStateTests(unittest.TestCase):
    def test_reads_real_repo(self):
        state = repo.load_state()
        self.assertEqual(len(state["plan"]), 14)
        self.assertTrue(all(day["creative"] for day in state["plan"]))
        decoy = next(c for c in state["creatives"] if c["concept"] == "decoy-pin")
        self.assertTrue(decoy["pro"])
        self.assertEqual([v["id"] for v in decoy["variants"]], ["a", "b", "c"])
        self.assertTrue(decoy["caption"].startswith("Two PINs."))
        self.assertEqual(next(a for a in state["accounts"] if a["channel"] == "youtube")["url"],
                         "https://www.youtube.com/@khanhvuapps")


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def request(self, method, path, headers=None, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request(method, path, body=body, headers={"Host": f"127.0.0.1:{self.port}", **(headers or {})})
        res = conn.getresponse()
        return res.status, res.read()

    def test_state_and_static(self):
        with mock.patch.object(store, "DB_PATH", Path(tempfile.mkdtemp()) / "d.db"):
            status, body = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertIn("creatives", json.loads(body))
        self.assertEqual(self.request("GET", "/")[0], 200)

    def test_rejects_foreign_host_origin_and_traversal(self):
        self.assertEqual(self.request("GET", "/api/state", {"Host": "evil.example"})[0], 403)
        status, _ = self.request("POST", "/api/campaigns", {"Origin": "http://evil.example", "Content-Type": "application/json"}, "{}")
        self.assertEqual(status, 403)
        self.assertEqual(self.request("POST", "/api/campaigns", {"Content-Type": "text/plain"}, "{}")[0], 415)
        self.assertEqual(self.request("GET", "/media?path=../.env.example")[0], 404)
        self.assertEqual(self.request("GET", "/media?path=docs/README.md")[0], 404)
        self.assertEqual(self.request("GET", "/../server.py")[0], 404)


if __name__ == "__main__":
    unittest.main()
