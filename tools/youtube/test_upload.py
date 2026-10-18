"""Offline tests for upload.py: no credentials, no network, YouTube answers are mocked."""

import datetime as dt
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import upload  # noqa: E402

CHANNEL = {"items": [{"id": "UC7kW-0SrYs4FGm1LFT9zJRw", "snippet": {"title": "KV Apps"}}]}
META = """
creative_id = "2026-10-18-calculator-pov-en-v1"

[youtube]
title = "POV: your friend grabs your phone #Shorts"
description = "Veilnest on the App Store: https://apps.apple.com/app/id6813747332"
tags = ["iphone tips", "privacy"]
synthetic_media = false
"""


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def meta(self, text=META):
        path = self.dir / "youtube.toml"
        path.write_text(text, encoding="utf-8")
        return upload.Meta.load(path)

    def test_defaults_to_private_and_builds_body(self):
        meta = self.meta()
        self.assertEqual(meta.privacy, "private")
        body = upload.request_body(meta)
        self.assertEqual(body["status"]["privacyStatus"], "private")
        self.assertFalse(body["status"]["containsSyntheticMedia"])
        self.assertNotIn("publishAt", body["status"])
        self.assertEqual(body["snippet"]["categoryId"], "28")
        self.assertEqual(upload.validate(meta), [])

    def test_synthetic_media_must_be_declared(self):
        with self.assertRaisesRegex(upload.UsageError, "synthetic_media"):
            self.meta(META.replace("synthetic_media = false\n", ""))

    def test_rejects_long_title_and_angle_brackets(self):
        meta = self.meta()
        meta.title = "x" * 101
        meta.description = "<b>"
        problems = " ".join(upload.validate(meta))
        self.assertIn("1–100", problems)
        self.assertIn("< or >", problems)

    def test_schedule_requires_private(self):
        meta = self.meta()
        meta.publish_at, meta.privacy = "2030-01-01T00:00:00Z", "public"
        self.assertIn("must upload as private", " ".join(upload.validate(meta)))

    def test_publish_at_needs_future_time_with_timezone(self):
        now = dt.datetime(2026, 10, 18, 10, tzinfo=dt.timezone.utc)
        self.assertEqual(upload.parse_publish_at("2026-10-20T19:00:00+07:00", now), "2026-10-20T12:00:00Z")
        with self.assertRaisesRegex(upload.UsageError, "timezone"):
            upload.parse_publish_at("2026-10-20T19:00:00", now)
        with self.assertRaisesRegex(upload.UsageError, "future"):
            upload.parse_publish_at("2026-10-18T17:05:00+07:00", now)

    def test_landscape_and_long_videos_are_not_shorts(self):
        self.assertEqual(upload.check_short({"width": 1080, "height": 1920, "duration": 15.0}), [])
        self.assertEqual(len(upload.check_short({"width": 1920, "height": 1080, "duration": 200.0})), 2)


class UploadFlowTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.video = self.dir / "export.mp4"
        self.video.write_bytes(b"\0" * 2048)
        self.meta = self.dir / "youtube.toml"
        self.meta.write_text(META, encoding="utf-8")
        self.config = upload.Config(self.dir / "client.json", self.dir / "token.json", "UC7kW-0SrYs4FGm1LFT9zJRw")
        self.ledger = self.dir / "UPLOADS.md"
        self.ledger.write_text("| header |\n", encoding="utf-8")
        upload.LEDGER = self.ledger
        upload.REPO = self.dir
        upload.probe = lambda _video: {"width": 1080, "height": 1920, "duration": 15.0}

    def service(self, *responses):
        from googleapiclient.http import HttpMockSequence
        self.http = HttpMockSequence(list(responses))
        return lambda: upload.youtube(http=self.http)

    def args(self, **overrides):
        values = dict(video=str(self.video), meta=str(self.meta), privacy=None, publish_at=None,
                      dry_run=False, no_ledger=False)
        values.update(overrides)
        return Namespace(**values)

    def uploaded(self, privacy="private", publish_at=None):
        status = {"privacyStatus": privacy}
        if publish_at:
            status["publishAt"] = publish_at
        return [
            ({"status": "200"}, json.dumps(CHANNEL)),
            ({"status": "200", "location": "https://upload.example/session"}, ""),
            ({"status": "200"}, json.dumps({"id": "abc123", "status": status})),
        ]

    def test_dry_run_sends_nothing(self):
        factory = lambda: self.fail("dry run must not build a YouTube client")
        self.assertEqual(upload.cmd_upload(self.args(dry_run=True), self.config, factory), 0)
        self.assertEqual(self.ledger.read_text(), "| header |\n")

    def test_private_upload_sends_private_body_and_records_ledger(self):
        factory = self.service(*self.uploaded())
        captured = {}
        original = upload.upload_video

        def spy(service, video, body, **kw):
            captured["body"] = body
            return original(service, video, body, **kw)

        upload.upload_video = spy
        try:
            self.assertEqual(upload.cmd_upload(self.args(), self.config, factory, ask=self.fail), 0)
        finally:
            upload.upload_video = original
        self.assertEqual(captured["body"]["status"]["privacyStatus"], "private")
        row = self.ledger.read_text().splitlines()[-1]
        self.assertIn("abc123", row)
        self.assertIn("private", row)
        self.assertIn("2026-10-18-calculator-pov-en-v1", row)

    def test_wrong_channel_aborts_before_upload(self):
        other = {"items": [{"id": "UCother", "snippet": {"title": "Personal"}}]}
        factory = self.service(({"status": "200"}, json.dumps(other)))
        with self.assertRaisesRegex(upload.UsageError, "not YOUTUBE_EXPECTED_CHANNEL_ID"):
            upload.cmd_upload(self.args(), self.config, factory)
        self.assertEqual(self.ledger.read_text(), "| header |\n")

    def test_public_needs_typed_confirmation(self):
        factory = self.service(({"status": "200"}, json.dumps(CHANNEL)))
        with self.assertRaisesRegex(upload.UsageError, "cancelled"):
            upload.cmd_upload(self.args(privacy="public"), self.config, factory, ask=lambda _: "yes")

    def test_schedule_uploads_private_with_publish_at_after_confirmation(self):
        factory = self.service(*self.uploaded(publish_at="2030-01-01T12:00:00Z"))
        prompts = []
        self.assertEqual(upload.cmd_upload(self.args(publish_at="2030-01-01T19:00:00+07:00"), self.config,
                                           factory, ask=lambda text: prompts.append(text) or "publish"), 0)
        self.assertEqual(len(prompts), 1)
        self.assertIn("2030-01-01T12:00:00Z", self.ledger.read_text())

    def test_retries_server_errors(self):
        from googleapiclient.http import HttpMockSequence
        http = HttpMockSequence([
            ({"status": "200", "location": "https://upload.example/session"}, ""),
            ({"status": "503"}, "busy"),
            ({"status": "200"}, json.dumps({"id": "retry1", "status": {"privacyStatus": "private"}})),
        ])
        waits = []
        response = upload.upload_video(upload.youtube(http=http), self.video, {"snippet": {}, "status": {}},
                                       sleep=waits.append, log=lambda *_: None)
        self.assertEqual(response["id"], "retry1")
        self.assertEqual(waits, [2])


if __name__ == "__main__":
    unittest.main()
