"""Offline tests for the App Store page: local listing, JWT signing, and every ASC call against a fake API.

Nothing here reaches Apple. The fake server keeps an in-memory app (one live version, one version in
Prepare for Submission, two languages) and records each request so the tests can assert exact calls.
"""

import base64
import hashlib
import http.client
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import unicodedata
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).parent))
import appstore  # noqa: E402
import repo  # noqa: E402
import server  # noqa: E402
import store  # noqa: E402


def jpeg(w: int, h: int, payload: bytes = b"") -> bytes:
    """Smallest JPEG-shaped bytes image_size() can read: SOI, an APP0, then SOF0 with the size."""
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
    sof = b"\xff\xc0" + struct.pack(">HBHH", 11, 8, h, w) + b"\x01\x01\x11\x00"
    return b"\xff\xd8" + app0 + sof + payload + b"\xff\xd9"


def make_app_repo(root: Path) -> None:
    locales = {
        "en-US": {"name": "Veilnest: Private Photo Vault", "subtitle": "Hide Pictures & Videos",
                  "keywords": "vault,hide", "promotional_text": "New promo", "description": "Desc EN",
                  "whats_new": "Fixes"},
        "de-DE": {"name": "Veilnest: Fotos verstecken", "subtitle": "Privater Foto-Tresor",
                  "keywords": "geheim", "promotional_text": "Promo DE", "description": "Desc DE", "whats_new": "Neu"},
        "ja": {"name": "Veilnest: 写真を隠す", "subtitle": "x" * 31, "keywords": "電卓",
               "promotional_text": "", "description": "説明", "whats_new": "修正"},
    }
    for code, meta in locales.items():
        d = root / "Docs/ASO/locales" / code
        d.mkdir(parents=True)
        (d / "locale.json").write_text(json.dumps({"locale": code, "tier": 1, "whats_new_version": "1.5",
                                                   "metadata": meta}), encoding="utf-8")
        shots = root / "Docs/ASO/screenshots" / code
        shots.mkdir(parents=True)
        for i in (1, 2):
            (shots / f"0{i}-shot.jpg").write_bytes(jpeg(1206, 2622, f"{code}{i}".encode()))


class FakeASC:
    """Just enough of App Store Connect for the dashboard."""

    def __init__(self):
        self.calls = []
        self.uploads = {}
        self.app = {"name": "Veilnest", "bundleId": "com.khanhvu.veilnest", "primaryLocale": "en-US"}
        self.versions = {
            "v-live": {"versionString": "1.4", "appVersionState": "READY_FOR_DISTRIBUTION", "createdDate": "2026-09-01"},
            "v-next": {"versionString": "1.5", "appVersionState": "PREPARE_FOR_SUBMISSION", "createdDate": "2026-10-01"},
        }
        self.infos = {"i-live": {"state": "READY_FOR_DISTRIBUTION"}, "i-next": {"state": "PREPARE_FOR_SUBMISSION"}}
        self.info_locs = {
            "il-en": {"locale": "en-US", "name": "Veilnest: Private Photo Vault", "subtitle": "Old subtitle",
                      "privacyPolicyUrl": "https://example.com/privacy", "_parent": "i-next"},
            "il-de": {"locale": "de-DE", "name": "Veilnest: Fotos verstecken", "subtitle": "Privater Foto-Tresor",
                      "_parent": "i-next"},
        }
        self.version_locs = {
            "vl-en": {"locale": "en-US", "keywords": "vault,hide", "promotionalText": "Old promo",
                      "description": "Desc EN", "whatsNew": "", "supportUrl": "https://example.com/support",
                      "_parent": "v-next"},
            "vl-de": {"locale": "de-DE", "keywords": "geheim", "promotionalText": "Promo DE",
                      "description": "Desc DE", "whatsNew": "Neu", "_parent": "v-next"},
        }
        self.sets = {"set-en": {"screenshotDisplayType": "APP_IPHONE_61", "_parent": "vl-en", "items": ["s1", "s2"]}}
        self.shots = {"s1": {"fileName": "old-1.jpg", "sourceFileChecksum": "aaa"},
                      "s2": {"fileName": "old-2.jpg", "sourceFileChecksum": "bbb"}}
        self.seq = 0

    def new_id(self, prefix):
        self.seq += 1
        return f"{prefix}-{self.seq}"

    @staticmethod
    def res(type_, id_, attrs, rels=None):
        out = {"type": type_, "id": id_, "attributes": {k: v for k, v in attrs.items() if not k.startswith("_")}}
        if rels:
            out["relationships"] = rels
        return out

    def handle(self, method, path, query, body):
        self.calls.append((method, path, body))
        m = re.fullmatch
        if method == "GET" and path == "/v1/apps":
            return {"data": [self.res("apps", "6813747332", self.app),
                             self.res("apps", "6700000001", {"name": "Color Meter: Pick Colors",
                                                             "bundleId": "com.khanhvu.ColorMeter"}),
                             self.res("apps", "6700000002", {"name": "Brand New", "bundleId": "com.khanhvu.brandnew"})]}
        if method == "GET" and path == "/v1/apps/6813747332":
            return {"data": self.res("apps", "6813747332", self.app)}
        if method == "GET" and path == "/v1/apps/6813747332/appStoreVersions":
            return {"data": [self.res("appStoreVersions", k, v) for k, v in self.versions.items()]}
        if method == "GET" and path == "/v1/apps/6813747332/appInfos":
            return {"data": [self.res("appInfos", k, v) for k, v in self.infos.items()]}
        if method == "GET" and (g := m(r"/v1/appInfos/([\w-]+)/appInfoLocalizations", path)):
            return {"data": [self.res("appInfoLocalizations", k, v) for k, v in self.info_locs.items()
                             if v["_parent"] == g[1]]}
        if method == "GET" and (g := m(r"/v1/appStoreVersions/([\w-]+)/appStoreVersionLocalizations", path)):
            items = [self.res("appStoreVersionLocalizations", k, v) for k, v in self.version_locs.items()
                     if v["_parent"] == g[1]]
            # Paginate to prove links.next is followed.
            if "cursor" not in query and len(items) > 1:
                return {"data": items[:1], "links": {"next": f"{self.base}{path}?cursor=2"}}
            return {"data": items[1:] if "cursor" in query else items}
        if method == "GET" and (g := m(r"/v1/appStoreVersionLocalizations/([\w-]+)/appScreenshotSets", path)):
            sets = {k: v for k, v in self.sets.items() if v["_parent"] == g[1]}
            return {"data": [self.res("appScreenshotSets", k, {"screenshotDisplayType": v["screenshotDisplayType"]},
                                      {"appScreenshots": {"data": [{"type": "appScreenshots", "id": i} for i in v["items"]]}})
                             for k, v in sets.items()],
                    "included": [self.res("appScreenshots", i, self.shots[i]) for v in sets.values() for i in v["items"]]}
        if method == "PATCH" and (g := m(r"/v1/(appInfoLocalizations|appStoreVersionLocalizations)/([\w-]+)", path)):
            table = self.info_locs if g[1] == "appInfoLocalizations" else self.version_locs
            table[g[2]].update(body["data"]["attributes"])
            return {"data": self.res(g[1], g[2], table[g[2]])}
        if method == "POST" and path in ("/v1/appInfoLocalizations", "/v1/appStoreVersionLocalizations"):
            kind = path.rsplit("/", 1)[1]
            rel = next(iter(body["data"]["relationships"].values()))["data"]["id"]
            if kind == "appStoreVersionLocalizations":
                lang = body["data"]["attributes"]["locale"]
                if not any(v["locale"] == lang for v in self.info_locs.values()):
                    return 409, {"errors": [{"title": "Language missing", "detail": "Add it in App Information first"}]}
            table = self.info_locs if kind == "appInfoLocalizations" else self.version_locs
            new = self.new_id(kind[:2])
            table[new] = {**body["data"]["attributes"], "_parent": rel}
            return 201, {"data": self.res(kind, new, table[new])}
        if method == "POST" and path == "/v1/appScreenshotSets":
            new = self.new_id("set")
            self.sets[new] = {"screenshotDisplayType": body["data"]["attributes"]["screenshotDisplayType"],
                              "_parent": body["data"]["relationships"]["appStoreVersionLocalization"]["data"]["id"],
                              "items": []}
            return 201, {"data": self.res("appScreenshotSets", new, {})}
        if method == "DELETE" and (g := m(r"/v1/appScreenshots/([\w-]+)", path)):
            for s in self.sets.values():
                if g[1] in s["items"]:
                    s["items"].remove(g[1])
            self.shots.pop(g[1])
            return 204, None
        if method == "POST" and path == "/v1/appScreenshots":
            a = body["data"]["attributes"]
            set_id = body["data"]["relationships"]["appScreenshotSet"]["data"]["id"]
            if len(self.sets[set_id]["items"]) >= 10:
                return 409, {"errors": [{"title": "Too many screenshots"}]}
            new = self.new_id("shot")
            self.shots[new] = {"fileName": a["fileName"]}
            self.sets[set_id]["items"].append(new)
            half = a["fileSize"] // 2
            ops = [{"method": "PUT", "url": f"{self.base}/upload/{new}/0", "offset": 0, "length": half,
                    "requestHeaders": [{"name": "Content-Type", "value": "image/jpeg"}]},
                   {"method": "PUT", "url": f"{self.base}/upload/{new}/1", "offset": half,
                    "length": a["fileSize"] - half, "requestHeaders": []}]
            return 201, {"data": self.res("appScreenshots", new, {**self.shots[new], "uploadOperations": ops})}
        if method == "PATCH" and (g := m(r"/v1/appScreenshots/([\w-]+)", path)):
            self.shots[g[1]].update(sourceFileChecksum=body["data"]["attributes"]["sourceFileChecksum"])
            return {"data": self.res("appScreenshots", g[1], self.shots[g[1]])}
        if method == "PATCH" and (g := m(r"/v1/appScreenshotSets/([\w-]+)/relationships/appScreenshots", path)):
            self.sets[g[1]]["items"] = [x["id"] for x in body["data"]]
            return 204, None
        if method == "GET" and path == "/v1/apps/6813747332/subscriptionGroups":
            return {"data": [self.res("subscriptionGroups", "g1", {"referenceName": "Veilnest Pro"},
                                      {"subscriptions": {"data": [{"type": "subscriptions", "id": "sub1"}]}})],
                    "included": [self.res("subscriptions", "sub1", {"name": "Yearly", "productId": "pro.yearly",
                                                                    "state": "APPROVED", "subscriptionPeriod": "ONE_YEAR",
                                                                    "groupLevel": 1})]}
        if method == "GET" and path == "/v1/subscriptions/sub1/prices":
            return {"data": [self.res("subscriptionPrices", "p1", {"startDate": None},
                                      {"subscriptionPricePoint": {"data": {"type": "subscriptionPricePoints", "id": "pp1"}}})],
                    "included": [self.res("subscriptionPricePoints", "pp1", {"customerPrice": "19.99", "proceeds": "16.99"})]}
        if method == "GET" and path == "/v1/apps/6813747332/inAppPurchasesV2":
            return {"data": [self.res("inAppPurchases", "iap1", {"name": "Lifetime", "productId": "pro.lifetime",
                                                                  "inAppPurchaseType": "NON_CONSUMABLE", "state": "APPROVED"})]}
        return 404, {"errors": [{"title": "Not found", "detail": f"{method} {path}"}]}


def serve(fake: FakeASC):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def go(self, method):
            u = urlparse(self.path)
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            if u.path.startswith("/upload/"):
                fake.uploads[u.path] = (raw, self.headers.get("Authorization"), self.headers.get("Content-Type"))
                self.send_response(200)
                self.end_headers()
                return
            auth = self.headers.get("Authorization", "")
            if not re.fullmatch(r"Bearer [\w-]+\.[\w-]+\.[\w-]+", auth):
                self.send_response(401)
                self.end_headers()
                return
            out = fake.handle(method, u.path, parse_qs(u.query), json.loads(raw) if raw else None)
            status, payload = out if isinstance(out, tuple) else (200, out)
            body = json.dumps(payload).encode() if payload is not None else b""
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            self.go("GET")

        def do_POST(self):
            self.go("POST")

        def do_PATCH(self):
            self.go("PATCH")

        def do_PUT(self):
            self.go("PUT")

        def do_DELETE(self):
            self.go("DELETE")

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
    fake.base = f"http://127.0.0.1:{httpd.server_address[1]}"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def make_key(folder: Path) -> tuple[Path, Path]:
    """A throwaway P-256 key as App Store Connect hands it out (.p8), plus its public key for verifying."""
    key = folder / "ec.pem"
    subprocess.run(["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", key], check=True)
    subprocess.run(["openssl", "pkcs8", "-topk8", "-nocrypt", "-in", key, "-out", folder / "AuthKey_TEST.p8"], check=True)
    subprocess.run(["openssl", "ec", "-in", key, "-pubout", "-out", folder / "pub.pem"], check=True, capture_output=True)
    return folder / "AuthKey_TEST.p8", folder / "pub.pem"


class AppStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.p8, cls.pub = make_key(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        use_workspace(self)
        self.fake = FakeASC()
        self.httpd = serve(self.fake)
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)
        self.client = appstore.Client(self.fake.base, {"key_id": "TEST", "issuer_id": "iss", "key_path": self.p8,
                                                       "ready": True})

    def marks(self):
        with store.session() as conn:
            return store.sync_marks(conn, "veilnest")

    def mark(self, rows, how="matched", remote=None):
        with store.session() as conn:
            for locale, field, lh in rows:
                store.set_sync_mark(conn, "veilnest", locale, field, lh, (remote or {}).get((locale, field), lh), how)

    def test_token_verifies_with_openssl(self):
        for _ in range(10):  # r or s with a high bit / leading zero must still come out 32+32 bytes
            header, payload, sig = appstore.make_token("TEST", "iss", self.p8).split(".")
            raw = base64.urlsafe_b64decode(sig + "==")
            self.assertEqual(len(raw), 64)

            def integer(x):
                x = x.lstrip(b"\0") or b"\0"
                return b"\x02" + bytes([len(x) + (x[0] >> 7)]) + (b"\0" if x[0] & 0x80 else b"") + x
            seq = integer(raw[:32]) + integer(raw[32:])
            (self.tmp / "sig").write_bytes(b"\x30" + bytes([len(seq)]) + seq)
            res = subprocess.run(["openssl", "dgst", "-sha256", "-verify", self.pub, "-signature", self.tmp / "sig"],
                                 input=f"{header}.{payload}".encode(), capture_output=True)
            self.assertIn(b"Verified OK", res.stdout)
        claims = json.loads(base64.urlsafe_b64decode(payload + "=="))
        self.assertEqual(claims["aud"], "appstoreconnect-v1")
        self.assertLessEqual(claims["exp"] - claims["iat"], 1200)

    def test_local_listing_and_limits(self):
        local = appstore.local_listing("veilnest")
        self.assertEqual(sorted(local["locales"]), ["de-DE", "en-US", "ja"])
        shot = local["locales"]["en-US"]["screenshots"][0]
        self.assertEqual((shot["width"], shot["height"], shot["display_type"]), (1206, 2622, "APP_IPHONE_61"))
        self.assertEqual(local["locales"]["ja"]["problems"], ["Subtitle 31/30"])

    def test_remote_listing_picks_editable_version_and_follows_pages(self):
        remote = appstore.remote_listing(self.client, "veilnest")
        v = remote["version"]
        self.assertEqual((v["id"], v["version"], v["state"], v["editable"], v["locked"]),
                         ("v-next", "1.5", "PREPARE_FOR_SUBMISSION", True, None))
        self.assertEqual(remote["live_version"]["version"], "1.4")
        self.assertEqual([x["version"] for x in remote["versions"]], ["1.5", "1.4"])
        self.assertEqual(remote["info"]["id"], "i-next")
        self.assertEqual(sorted(remote["locales"]), ["de-DE", "en-US"])
        self.assertEqual(remote["locales"]["de-DE"]["version_loc_id"], "vl-de")  # second page
        self.assertEqual([i["file"] for i in remote["screenshots"]["en-US"]["APP_IPHONE_61"]["items"]],
                         ["old-1.jpg", "old-2.jpg"])

    def test_compare(self):
        rows = {r["locale"]: r for r in appstore.compare(appstore.local_listing("veilnest"),
                                                         appstore.remote_listing(self.client, "veilnest"))["rows"]}
        en = rows["en-US"]["fields"]
        self.assertEqual(en["name"]["status"], "same")
        self.assertEqual(en["subtitle"]["status"], "differs")  # no mark: maybe edited by hand on ASC
        self.assertEqual(en["whats_new"]["status"], "new")
        self.assertFalse(rows["ja"]["remote_exists"])
        self.assertTrue(rows["ja"]["fields"]["subtitle"]["over"])
        self.assertEqual(rows["ja"]["fields"]["promotional_text"]["status"], "empty")
        self.assertEqual(rows["en-US"]["shots_status"], "differs")
        self.assertEqual(rows["de-DE"]["shots_status"], "new")

    def test_hand_pasted_text_counts_as_same(self):
        """CRLF, trailing spaces, NFD accents and spaces in keywords are what ASC does to pasted text."""
        self.fake.version_locs["vl-de"].update(keywords=" geheim ", description="Desc DE  \r\n",
                                               promotionalText=unicodedata.normalize("NFD", "Promo DE"))
        rows = {r["locale"]: r for r in appstore.compare(appstore.local_listing("veilnest"),
                                                         appstore.remote_listing(self.client, "veilnest"))["rows"]}
        de = rows["de-DE"]["fields"]
        self.assertEqual({k: de[k]["status"] for k in ("keywords", "description", "promotional_text")},
                         {"keywords": "same", "description": "same", "promotional_text": "same"})

    def test_metadata_needs_override_for_text_changed_on_asc(self):
        local = appstore.local_listing("veilnest")
        remote = appstore.remote_listing(self.client, "veilnest")
        with self.assertRaisesRegex(appstore.AscError, "Subtitle dài 31/30"):
            appstore.plan_metadata(local, remote, [{"locale": "ja", "fields": ["subtitle"]}])
        with self.assertRaisesRegex(appstore.AscError, "en-US · Subtitle: khác ASC, chưa có mốc"):
            appstore.plan_metadata(local, remote, [{"locale": "en-US", "fields": list(appstore.FIELDS)}])
        ops = appstore.plan_metadata(local, remote, [
            {"locale": "en-US", "fields": list(appstore.FIELDS), "override": ["subtitle", "promotional_text"]},
            {"locale": "ja", "fields": ["name", "keywords", "description"]}])
        summary = [(o["locale"], o["resource"], o["op"], tuple(o["fields"])) for o in ops]
        self.assertEqual(summary, [
            ("en-US", "info", "update", ("subtitle",)),
            ("en-US", "version", "update", ("promotional_text", "whats_new")),
            ("ja", "info", "create", ("name",)),
            ("ja", "version", "create", ("keywords", "description")),
        ])
        # New language copies the primary locale's URLs so ASC accepts it.
        self.assertEqual(ops[2]["attributes"]["privacyPolicyUrl"], "https://example.com/privacy")
        self.assertEqual(ops[3]["attributes"]["supportUrl"], "https://example.com/support")
        done = appstore.apply_metadata(self.client, ops, on_done=lambda op: self.mark(appstore.pushed_marks(op), "pushed"))
        self.assertEqual(len(done), 4)
        self.assertEqual(self.fake.info_locs["il-en"]["subtitle"], "Hide Pictures & Videos")
        self.assertEqual(self.marks()[("en-US", "whats_new")]["how"], "pushed")
        # Pushing the same selection again sends nothing.
        again = appstore.remote_listing(self.client, "veilnest")
        self.assertEqual(appstore.plan_metadata(local, again, [
            {"locale": "en-US", "fields": list(appstore.FIELDS), "override": list(appstore.FIELDS)},
            {"locale": "ja", "fields": ["name", "keywords", "description"]}]), [])

    def test_marks_tell_local_edits_from_asc_edits(self):
        local = appstore.local_listing("veilnest")
        remote = appstore.remote_listing(self.client, "veilnest")
        compared = appstore.compare(local, remote, self.marks())
        self.mark(compared["matched"])  # what the server does after every read
        self.assertIn(("de-DE", "keywords", appstore.digest("geheim")), compared["matched"])

        # 1. Local edit after a match → ahead, pushed without override.
        meta = self.app_repo / "Docs/ASO/locales/de-DE/locale.json"
        data = json.loads(meta.read_text())
        data["metadata"]["keywords"] = "geheim,tresor"
        meta.write_text(json.dumps(data))
        local = appstore.local_listing("veilnest")
        row = next(r for r in appstore.compare(local, remote, self.marks())["rows"] if r["locale"] == "de-DE")
        self.assertEqual(row["fields"]["keywords"]["status"], "ahead")
        ops = appstore.plan_metadata(local, remote, [{"locale": "de-DE", "fields": ["keywords"]}], self.marks())
        self.assertEqual(ops[0]["attributes"], {"keywords": "geheim,tresor"})

        # 2. Someone edits ASC by hand after the match → conflict, refused without override.
        self.fake.version_locs["vl-de"]["description"] = "Edited in App Store Connect"
        remote = appstore.remote_listing(self.client, "veilnest")
        row = next(r for r in appstore.compare(local, remote, self.marks())["rows"] if r["locale"] == "de-DE")
        self.assertEqual(row["fields"]["description"]["status"], "conflict")
        with self.assertRaisesRegex(appstore.AscError, "ASC đã sửa tay"):
            appstore.plan_metadata(local, remote, [{"locale": "de-DE", "fields": ["description"]}], self.marks())

        # 3. Keep the ASC text → accepted, nothing to push; a later local edit makes it ahead again.
        self.mark([("de-DE", "description", appstore.digest("Desc DE"))], "accepted",
                  {("de-DE", "description"): appstore.digest("Edited in App Store Connect")})
        row = next(r for r in appstore.compare(local, remote, self.marks())["rows"] if r["locale"] == "de-DE")
        self.assertEqual(row["fields"]["description"]["status"], "accepted")
        data["metadata"]["description"] = "Desc DE v2"
        meta.write_text(json.dumps(data))
        row = next(r for r in appstore.compare(appstore.local_listing("veilnest"), remote, self.marks())["rows"]
                   if r["locale"] == "de-DE")
        self.assertEqual(row["fields"]["description"]["status"], "ahead")

    def test_newest_version_wins_even_while_in_review(self):
        """1.5 waiting for review must be what the page shows and compares against, not the live 1.4."""
        self.fake.versions["v-next"]["appVersionState"] = "WAITING_FOR_REVIEW"
        self.fake.infos["i-next"]["state"] = "WAITING_FOR_REVIEW"
        local = appstore.local_listing("veilnest")
        remote = appstore.remote_listing(self.client, "veilnest")
        self.assertEqual((remote["version"]["id"], remote["version"]["editable"]), ("v-next", False))
        self.assertEqual(remote["info"]["id"], "i-next")
        self.assertIn("Remove from Review", remote["version"]["locked"])
        self.assertEqual(remote["locales"]["en-US"]["version_loc_id"], "vl-en", "fields come from 1.5")
        with self.assertRaisesRegex(appstore.AscError, "1.5 đang chờ review: Apple khoá metadata"):
            appstore.plan_metadata(local, remote, [{"locale": "en-US", "fields": ["whats_new"]}])
        with self.assertRaisesRegex(appstore.AscError, "chờ review"):
            appstore.plan_metadata(local, remote, [{"locale": "en-US", "fields": ["subtitle"], "override": ["subtitle"]}])
        ops = appstore.plan_metadata(local, remote, [{"locale": "en-US", "fields": ["promotional_text"],
                                                      "override": ["promotional_text"]}])
        self.assertEqual(ops[0]["id"], "vl-en")
        with self.assertRaisesRegex(appstore.AscError, "Không thay được screenshot: version 1.5 đang chờ review"):
            appstore.plan_screenshots("veilnest", remote, "de-DE")

    def test_only_promo_is_editable_on_a_live_version(self):
        del self.fake.versions["v-next"]
        self.fake.infos.pop("i-next")
        for loc in self.fake.version_locs.values():
            loc["_parent"] = "v-live"
        for loc in self.fake.info_locs.values():
            loc["_parent"] = "i-live"
        local = appstore.local_listing("veilnest")
        remote = appstore.remote_listing(self.client, "veilnest")
        self.assertFalse(remote["version"]["editable"])
        ops = appstore.plan_metadata(local, remote, [{"locale": "en-US", "fields": ["promotional_text"],
                                                      "override": ["promotional_text"]}])
        self.assertEqual([o["fields"] for o in ops], [["promotional_text"]])
        with self.assertRaisesRegex(appstore.AscError, "version 1.4 đang bán: tạo version mới"):
            appstore.plan_metadata(local, remote, [{"locale": "en-US", "fields": ["whats_new"]}])
        with self.assertRaisesRegex(appstore.AscError, "Subtitle: version 1.4 đang bán"):
            appstore.plan_metadata(local, remote, [{"locale": "en-US", "fields": ["subtitle"],
                                                    "override": ["subtitle"]}])

    def test_screenshots_replace_existing_set_in_order(self):
        remote = appstore.remote_listing(self.client, "veilnest")
        with self.assertRaisesRegex(appstore.AscError, "khác ASC, chưa có mốc"):
            appstore.plan_screenshots("veilnest", remote, "en-US")
        plan = appstore.plan_screenshots("veilnest", remote, "en-US", override=True)
        self.assertEqual(plan["delete"], ["s1", "s2"])
        self.assertEqual([s["file"] for s in plan["upload"]], ["01-shot.jpg", "02-shot.jpg"])
        result = appstore.apply_screenshots(self.client, "veilnest", plan)
        self.assertEqual((result["uploaded"], result["deleted"]), (2, 2))
        items = self.fake.sets["set-en"]["items"]
        self.assertEqual([self.fake.shots[i]["fileName"] for i in items], ["01-shot.jpg", "02-shot.jpg"])
        folder = self.app_repo / "Docs/ASO/screenshots/en-US"
        for i, name in zip(items, ["01-shot.jpg", "02-shot.jpg"]):
            data = (folder / name).read_bytes()
            self.assertEqual(self.fake.shots[i]["sourceFileChecksum"], hashlib.md5(data).hexdigest())
            parts = self.fake.uploads[f"/upload/{i}/0"][0] + self.fake.uploads[f"/upload/{i}/1"][0]
            self.assertEqual(parts, data)
            self.assertIsNone(self.fake.uploads[f"/upload/{i}/0"][1], "upload URLs must not get the ASC token")
        # Same files again (also when uploaded by hand: ASC keeps the MD5) → nothing to do, no override needed.
        again = appstore.plan_screenshots("veilnest", appstore.remote_listing(self.client, "veilnest"), "en-US")
        self.assertTrue(again["unchanged"])
        self.assertEqual(again["status"], "same")

    def test_screenshots_create_set_and_refuse_unknown_language(self):
        remote = appstore.remote_listing(self.client, "veilnest")
        plan = appstore.plan_screenshots("veilnest", remote, "de-DE")
        self.assertEqual(plan["status"], "new")
        self.assertIsNone(plan["set_id"])
        appstore.apply_screenshots(self.client, "veilnest", plan)
        new_set = next(v for v in self.fake.sets.values() if v["_parent"] == "vl-de")
        self.assertEqual(len(new_set["items"]), 2)
        with self.assertRaisesRegex(appstore.AscError, "chưa có ngôn ngữ này"):
            appstore.plan_screenshots("veilnest", remote, "ja")

    def test_discover_and_link_apps(self):
        found = {a["app_store_id"]: a for a in appstore.discover(self.client)}
        self.assertTrue(found["6813747332"]["linked"])
        color = found["6700000001"]
        self.assertEqual((color["registry_id"], color["linked"]), ("color-meter", False))
        self.assertEqual(found["6700000002"]["repo"], "Apps/BrandNew")  # found by bundle id in the project
        self.assertEqual(appstore.link_app(self.client, "6700000001"), "color-meter")
        self.assertEqual(repo.APPS["color-meter"]["app_store_id"], "6700000001")
        self.assertEqual(repo.APPS["color-meter"]["name"], "Color Meter", "linking keeps the registry name")
        self.assertEqual(appstore.link_app(self.client, "6700000002"), "brand-new")
        self.assertEqual(repo.load_registry()["brand-new"]["repo"], "Apps/BrandNew")

    def test_import_listing_never_overwrites(self):
        appstore.link_app(self.client, "6700000001")
        self.fake_app_as("6700000001")
        local = appstore.local_listing("color-meter")
        self.assertEqual(local["locales"], {})
        remote = appstore.remote_listing(self.client, "color-meter")
        result = appstore.import_listing("color-meter", remote)
        self.assertEqual(result["created"], ["de-DE", "en-US"])
        self.assertEqual(repo.APPS["color-meter"]["store"], appstore.IMPORT_STORE)
        rows = appstore.compare(appstore.local_listing("color-meter"), remote)["rows"]
        statuses = {f["status"] for r in rows for f in r["fields"].values()}
        self.assertLessEqual(statuses, {"same", "empty"}, "imported text must not show up as something to push")
        target = self.workspace / "Apps/Color-Meter/AppStore/locales/en-US/locale.json"
        target.write_text(json.dumps({"metadata": {"name": "Mine"}}))
        again = appstore.import_listing("color-meter", remote)
        self.assertEqual((again["created"], again["skipped"]), ([], ["de-DE", "en-US"]))
        self.assertEqual(json.loads(target.read_text())["metadata"]["name"], "Mine")

    def fake_app_as(self, store_id):
        """Serve the same fake listing under another App Store ID."""
        handle = self.fake.handle

        def patched(method, path, query, body):
            return handle(method, path.replace(f"/v1/apps/{store_id}", "/v1/apps/6813747332"), query, body)
        self.fake.handle = patched

    def test_products(self):
        p = appstore.products(self.client, "veilnest")
        sub = p["groups"][0]["subscriptions"][0]
        self.assertEqual((sub["product_id"], sub["price"]["price"]), ("pro.yearly", "19.99"))
        self.assertEqual(p["iaps"][0]["product_id"], "pro.lifetime")

    def test_api_errors_are_readable(self):
        with self.assertRaisesRegex(appstore.AscError, "HTTP 404: Not found — GET /v1/nope"):
            self.client.request("GET", "/v1/nope")

    def test_not_configured(self):
        with self.assertRaisesRegex(appstore.AscError, "Chưa cấu hình"):
            appstore.Client(self.fake.base, {"ready": False})


def use_workspace(test):
    """Temp ~/personal: Apps/IOS-Vault with a listing, Apps/Color-Meter and Apps/BrandNew without, own registry
    and own SQLite. Nothing touches the real registry, repos or .dashboard/."""
    ws = Path(tempfile.mkdtemp())
    test.addCleanup(shutil.rmtree, ws, True)
    test.workspace = ws
    test.app_repo = ws / "Apps/IOS-Vault"
    make_app_repo(test.app_repo)
    (ws / "Apps/Color-Meter").mkdir(parents=True)
    (ws / "Apps/BrandNew").mkdir(parents=True)
    (ws / "Apps/BrandNew/project.yml").write_text("targets:\n  App:\n    PRODUCT_BUNDLE_IDENTIFIER: com.khanhvu.brandnew\n")
    registry = ws / "registry.json"
    registry.write_text(json.dumps({"apps": [
        {"id": "veilnest", "name": "Veilnest", "bundle_id": "com.khanhvu.veilnest", "app_store_id": "6813747332",
         "repo": "Apps/IOS-Vault", "store": {"locales": "Docs/ASO/locales", "screenshots": "Docs/ASO/screenshots"}},
        {"id": "color-meter", "name": "Color Meter", "bundle_id": "com.khanhvu.ColorMeter", "app_store_id": None,
         "repo": "Apps/Color-Meter", "store": None}]}))
    for patcher in (mock.patch.object(repo, "WORKSPACE", ws), mock.patch.object(repo, "REGISTRY", registry),
                    mock.patch.dict(repo.APPS, {}, clear=True), mock.patch.object(store, "DB_PATH", ws / "d.db")):
        patcher.start()
        test.addCleanup(patcher.stop)
    repo.APPS.update(repo.load_registry())


class AppStoreServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.p8, _ = make_key(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        use_workspace(self)
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)
        self.addCleanup(server.ASC_CACHE.clear)

    def request(self, method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        headers = {"Host": f"127.0.0.1:{self.port}"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=json.dumps(body) if body is not None else None, headers=headers)
        res = conn.getresponse()
        try:
            return res.status, res.read()
        finally:
            conn.close()

    def test_state_flags_stale_server_code(self):
        with mock.patch.object(store, "DB_PATH", self.workspace / "s.db"):
            self.assertFalse(json.loads(self.request("GET", "/api/state")[1])["stale_code"])
            with mock.patch.object(server, "CODE_STAMP", server.CODE_STAMP - 60):
                self.assertTrue(json.loads(self.request("GET", "/api/state")[1])["stale_code"])

    def test_listing_without_key_and_shot_files(self):
        status, body = self.request("POST", "/api/appstore/listing", {"app": "veilnest"})
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIsNone(data["remote"])
        self.assertEqual(len(data["compare"]["rows"]), 3)
        status, body = self.request("POST", "/api/appstore/listing", {"app": "color-meter"})
        self.assertEqual((status, json.loads(body)["compare"]["rows"]), (200, []))
        self.assertEqual(self.request("GET", "/asc-shot?app=veilnest&locale=en-US&file=01-shot.jpg")[0], 200)
        self.assertEqual(self.request("GET", "/asc-shot?app=veilnest&locale=..&file=locales/en-US/locale.json")[0], 404)
        self.assertEqual(self.request("GET", "/asc-shot?app=veilnest&locale=../../..&file=etc/passwd")[0], 404)
        with mock.patch.object(appstore, "credentials", return_value={"ready": False}):
            status, body = self.request("POST", "/api/appstore/metadata", {"app": "veilnest", "items": []})
        self.assertEqual(status, 409)
        self.assertIn("Chưa cấu hình", json.loads(body)["error"])

    def test_reading_records_matches_and_accept_keeps_asc_text(self):
        fake = FakeASC()
        httpd = serve(fake)
        self.addCleanup(httpd.server_close)
        self.addCleanup(httpd.shutdown)
        cred = {"key_id": "T", "issuer_id": "i", "key_path": self.p8, "ready": True}
        with mock.patch.object(appstore, "API", fake.base), mock.patch.object(appstore, "credentials", return_value=cred):
            status, body = self.request("POST", "/api/appstore/listing", {"app": "veilnest", "refresh": True})
            self.assertEqual(status, 200, body)
            marks = json.loads(body)["marks"]
            self.assertEqual(marks["de-DE|keywords"]["how"], "matched")
            self.assertNotIn("en-US|subtitle", marks)
            status, body = self.request("POST", "/api/appstore/accept",
                                        {"app": "veilnest", "locale": "en-US", "fields": ["subtitle", "screenshots"]})
            self.assertEqual(status, 200, body)
            rows = json.loads(self.request("POST", "/api/appstore/listing", {"app": "veilnest"})[1])["compare"]["rows"]
            en = next(r for r in rows if r["locale"] == "en-US")
            self.assertEqual((en["fields"]["subtitle"]["status"], en["shots_status"]), ("accepted", "accepted"))
            status, body = self.request("POST", "/api/appstore/metadata", {"app": "veilnest", "items": [
                {"locale": "en-US", "fields": ["subtitle", "whats_new"]}]})
            ops = json.loads(body)["ops"]
            self.assertEqual([o["fields"] for o in ops], [["whats_new"]], "accepted field is skipped, not refused")


if __name__ == "__main__":
    unittest.main()
