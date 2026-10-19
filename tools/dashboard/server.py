#!/usr/bin/env python3
"""KV Apps studio dashboard — local only.

    python3 tools/dashboard/server.py [--port 8790] [--no-open]

Serves a single-page app on http://127.0.0.1:8790 that reads the repo live (briefs, render outputs,
14-day plan, accounts, channel logs) and keeps private metric snapshots in /.dashboard/ (gitignored).
Standard library only. Binds to 127.0.0.1 and refuses requests from other origins.
"""

from __future__ import annotations

import argparse
import errno
import http.client
import json
import mimetypes
import re
import subprocess
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import appstore  # noqa: E402
import repo  # noqa: E402
import store  # noqa: E402

ROOT = repo.ROOT
STATIC = HERE / "static"
YT_PY = ROOT / "tools/youtube/.venv/bin/python"
MEDIA_ROOTS = (ROOT / "content",)
DB_LOCK = threading.Lock()
ASC_LOCK = threading.Lock()  # one App Store Connect write at a time
ASC_CACHE: dict[str, dict] = {}  # app → last remote listing read from App Store Connect


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


# --- actions -------------------------------------------------------------------------------

def youtube_status() -> dict:
    env = {}
    try:
        sys.path.insert(0, str(ROOT / "tools/youtube"))
        import upload  # noqa: PLC0415 — stdlib-only parts of the module
        config = upload.Config.from_env(upload.load_env())
        env = {"client": config.client_secrets.is_file(), "token": config.token_file.is_file(),
               "expected_channel": config.expected_channel}
    except Exception as exc:  # noqa: BLE001 — status only
        env = {"error": str(exc)}
    return {"venv": YT_PY.is_file(), **env}


def run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ApiError("quá thời gian chờ", 504) from None


def youtube_sync() -> dict:
    if not YT_PY.is_file():
        raise ApiError("chưa cài môi trường tools/youtube (xem tools/youtube/README.md)")
    state = repo.load_state()
    targets: dict[str, dict] = {}
    for up in state["uploads"]:
        if up.get("video_id"):
            targets[up["video_id"]] = {"url": up.get("url") or f"https://youtu.be/{up['video_id']}",
                                       "creative": up.get("creative_id")}
    for post in state["posts"]:
        if post["channel"] != "youtube" or not post.get("url"):
            continue
        m = re.search(r"(?:youtu\.be/|shorts/|v=)([\w-]{11})", post["url"])
        if m:
            targets[m[1]] = {"url": post["url"], "creative": post.get("creative_id"), "variant": post.get("variant")}
    if not targets:
        return {"added": 0, "notes": ["Chưa có video nào trong UPLOADS.md hoặc POSTS.md của YouTube."]}
    result = run([str(YT_PY), str(HERE / "youtube_sync.py"), *targets], timeout=180)
    try:
        data = json.loads(result.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise ApiError(f"youtube_sync lỗi: {(result.stderr or result.stdout).strip()[-400:]}", 502) from None
    if "error" in data:
        raise ApiError(data["error"], 409)
    added, notes = 0, list(data.get("notes", []))
    with DB_LOCK, store.session() as conn:
        for snap in data["snapshots"]:
            if snap.get("privacy") != "public":
                notes.append(f"{snap['video_id']} đang {snap.get('privacy')}: bỏ qua, chưa có người xem thật.")
                continue
            target = targets[snap["video_id"]]
            creative = target.get("creative") or ""
            variant = target.get("variant")
            m = re.match(r"(.+)-hook([a-z0-9]+)$", creative)
            if m:
                creative, variant = m[1], m[2]
            store.add_snapshot(conn, {
                "channel": "youtube", "url": target["url"], "creative_id": creative or None, "variant": variant,
                "captured_at": snap["captured_at"], "window": snap["window"], "source": "YouTube API",
                **{k: snap.get(k) for k in store.METRICS if snap.get(k) is not None},
            })
            added += 1
    return {"added": added, "notes": notes, "channel": data.get("channel")}


def youtube_upload(body: dict) -> dict:
    """Private upload through tools/youtube/upload.py. Never passes --privacy or --publish-at."""
    if not YT_PY.is_file():
        raise ApiError("chưa cài môi trường tools/youtube")
    state = repo.load_state()
    creative = next((c for c in state["creatives"] if c["id"] == body.get("creative")), None)
    if not creative:
        raise ApiError("không có creative này")
    variant = next((v for v in creative["variants"] if v["id"] == body.get("variant")), None)
    render = next((r for r in creative["renders"] if r["variant"] == body.get("variant") and not r["draft"]
                   and r["exists"]), None)
    if not variant or not variant.get("meta_file"):
        raise ApiError("biến thể này chưa có youtube-*.toml")
    if not render:
        raise ApiError("chưa có bản render cuối (không phải draft) cho biến thể này")
    cmd = [str(YT_PY), "tools/youtube/upload.py", "upload", render["file"],
           "--meta", f"{creative['path']}/{variant['meta_file']}"]
    if body.get("dry_run", True):
        cmd.append("--dry-run")
    result = run(cmd, timeout=1800)
    output = (result.stdout + result.stderr).strip()
    if result.returncode:
        raise ApiError(output[-1200:] or "upload.py lỗi", 502)
    return {"ok": True, "dry_run": body.get("dry_run", True), "output": output[-2000:]}


def asc_marks(app: str) -> dict:
    with DB_LOCK, store.session() as conn:
        return store.sync_marks(conn, app)


def asc_mark(app: str, rows: list[tuple[str, str, str]], how: str, remote_hashes: dict | None = None) -> None:
    """rows: (locale, field, local_hash). Remote hash = local hash unless given (accepting the ASC text)."""
    with DB_LOCK, store.session() as conn:
        for locale, field, lh in rows:
            store.set_sync_mark(conn, app, locale, field, lh, (remote_hashes or {}).get((locale, field), lh), how)


def asc_listing(app: str, refresh: bool) -> dict:
    local = appstore.local_listing(app)
    remote = ASC_CACHE.get(app)
    if refresh:
        remote = ASC_CACHE[app] = appstore.remote_listing(appstore.Client(), app)
    compared = appstore.compare(local, remote, asc_marks(app))
    # Equal on both sides (pushed by us or pasted by hand): remember it, so a later local edit reads as "ahead".
    asc_mark(app, compared.pop("matched"), "matched")
    return {"local": local, "remote": remote, "compare": compared, "marks": {
        f"{loc}|{field}": m for (loc, field), m in asc_marks(app).items()}}


def asc_metadata(body: dict) -> dict:
    """dry_run (default) returns the operations; otherwise runs them against a fresh read of ASC."""
    app = str(body.get("app", ""))
    with ASC_LOCK:
        client = appstore.Client()
        remote = ASC_CACHE[app] = appstore.remote_listing(client, app, screenshots=False) | {
            "screenshots": (ASC_CACHE.get(app) or {}).get("screenshots", {})}
        ops = appstore.plan_metadata(appstore.local_listing(app), remote, body.get("items") or [], asc_marks(app))
        if body.get("dry_run", True):
            return {"dry_run": True, "ops": ops, "version": remote["version"], "info": remote["info"]}
        done = appstore.apply_metadata(client, ops, on_done=lambda op: asc_mark(app, appstore.pushed_marks(op), "pushed"))
        ASC_CACHE[app] = appstore.remote_listing(client, app)
        return {"dry_run": False, "done": done}


def asc_screenshots(body: dict) -> dict:
    app, locale = str(body.get("app", "")), str(body.get("locale", ""))
    with ASC_LOCK:
        client = appstore.Client()
        remote = ASC_CACHE[app] = appstore.remote_listing(client, app)
        plan = appstore.plan_screenshots(app, remote, locale, asc_marks(app), bool(body.get("override")))
        if body.get("dry_run", True):
            return {"dry_run": True, "plan": plan}
        result = appstore.apply_screenshots(client, app, plan)
        asc_mark(app, [(locale, "screenshots", plan["key"])], "pushed")
        ASC_CACHE[app] = appstore.remote_listing(client, app)
        return {"dry_run": False, "plan": plan, **result}


def asc_accept(body: dict) -> dict:
    """Keep what is on ASC for these fields: no push until the local text changes again."""
    app, locale = str(body.get("app", "")), str(body.get("locale", ""))
    remote = ASC_CACHE.get(app)
    if not remote:
        raise ApiError("Tải từ App Store Connect trước", 409)
    local = appstore.local_listing(app)["locales"].get(locale)
    if not local:
        raise ApiError(f"{locale}: không có trong dữ liệu local")
    rows, remote_hashes = [], {}
    for field in body.get("fields") or []:
        if field == "screenshots":
            dtype = next((s["display_type"] for s in local["screenshots"] if s["display_type"]), None)
            lv = appstore.shots_key(local["screenshots"])
            rv = appstore.shots_key(appstore.remote_shots(remote, locale, dtype))
        elif field in appstore.FIELDS:
            lv = appstore.normalize(field, local["fields"][field])
            rv = appstore.normalize(field, (remote["locales"].get(locale) or {}).get(field))
        else:
            continue
        rows.append((locale, field, appstore.digest(lv)))
        remote_hashes[(locale, field)] = appstore.digest(rv)
    asc_mark(app, rows, "accepted", remote_hashes)
    return {"ok": True, "fields": [r[1] for r in rows]}


def asc_import(body: dict) -> dict:
    app = str(body.get("app", ""))
    with ASC_LOCK:
        remote = ASC_CACHE[app] = appstore.remote_listing(appstore.Client(), app)
        return appstore.import_listing(app, remote)


def asc_shot_file(query: dict) -> Path | None:
    """A local screenshot of a configured app, and nothing else."""
    src = appstore.store_paths(query.get("app", [""])[0])
    if not src:
        return None
    root = src["screenshots"].resolve()
    target = (root / query.get("locale", [""])[0] / query.get("file", [""])[0]).resolve()
    if root not in target.parents or target.suffix.lower() not in appstore.IMAGE_EXT:
        return None
    return target if target.is_file() else None


def reveal(path: str) -> dict:
    target = (ROOT / path).resolve()
    if ROOT not in target.parents or not target.exists():
        raise ApiError("đường dẫn không hợp lệ")
    subprocess.run(["open", "-R", str(target)], check=False)
    return {"ok": True}


# --- HTTP ----------------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "KVDashboard/1.0"

    def log_message(self, fmt, *args):  # quieter console: only errors
        if args and str(args[1])[:1] in "45":
            super().log_message(fmt, *args)

    # security: only our own origin on loopback
    def allowed(self) -> bool:
        port = self.server.server_address[1]
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in hosts:
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin in {f"http://{h}" for h in hosts}

    def send_json(self, data, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        if not self.headers.get("Content-Type", "").startswith("application/json"):
            raise ApiError("cần Content-Type application/json", 415)
        length = int(self.headers.get("Content-Length") or 0)
        if length > 1_000_000:
            raise ApiError("payload quá lớn", 413)
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            raise ApiError("JSON lỗi") from None
        if not isinstance(data, dict):
            raise ApiError("JSON phải là object")
        return data

    def handle_api(self, method: str):
        if not self.allowed():
            return self.send_json({"error": "forbidden"}, 403)
        path = urlparse(self.path).path
        try:
            body = self.read_json() if method in ("POST", "DELETE") else {}
            data = self.route(method, path, body)
            self.send_json(data)
        except (ApiError, repo.RepoError, store.StoreError, appstore.AscError) as exc:
            self.send_json({"error": str(exc)}, getattr(exc, "status", 400))
        except Exception as exc:  # noqa: BLE001 — surface to the UI instead of a dropped socket
            self.send_json({"error": f"lỗi máy chủ: {exc}"}, 500)

    def route(self, method: str, path: str, body: dict):
        if method == "GET" and path == "/api/state":
            state = repo.load_state()
            with DB_LOCK, store.session() as conn:
                state["snapshots"] = store.snapshots(conn)
            state["metric_defs"] = {k: {"label": v[0], "kind": v[1]} for k, v in store.METRICS.items()}
            state["windows"] = store.WINDOWS
            state["youtube"] = youtube_status()
            state["appstore"] = appstore.status()
            return state
        if method == "POST" and path == "/api/snapshots":
            with DB_LOCK, store.session() as conn:
                return store.add_snapshot(conn, body)
        if method == "DELETE" and (m := re.fullmatch(r"/api/snapshots/(\d+)", path)):
            with DB_LOCK, store.session() as conn:
                store.delete_snapshot(conn, int(m[1]))
            return {"ok": True}
        if method == "POST" and path == "/api/posts":
            return repo.append_post(body.get("channel", ""), body)
        if method == "POST" and path == "/api/posts/result":
            with DB_LOCK, store.session() as conn:
                text = store.result_text(conn, body.get("url", ""))
            return {**repo.write_result(body.get("channel", ""), body.get("url", ""), text), "text": text}
        if method == "POST" and path == "/api/campaigns":
            return repo.add_campaign(body)
        if method == "DELETE" and (m := re.fullmatch(r"/api/campaigns/(\w+)", path)):
            repo.delete_campaign(m[1])
            return {"ok": True}
        if method == "POST" and path == "/api/campaigns/provider":
            repo.set_provider_token(str(body.get("provider_token", "")))
            return {"ok": True}
        if method == "POST" and path == "/api/campaigns/suggest":
            return {"ct": repo.suggest_ct(body.get("channel", ""), body.get("lang", ""), body.get("creative", ""),
                                          body.get("variant", ""))}
        if method == "POST" and path == "/api/youtube/sync":
            return youtube_sync()
        if method == "POST" and path == "/api/youtube/upload":
            return youtube_upload(body)
        if method == "GET" and path == "/api/appstore/status":
            return appstore.status()
        if method == "POST" and path == "/api/appstore/listing":
            return asc_listing(str(body.get("app", "")), bool(body.get("refresh")))
        if method == "POST" and path == "/api/appstore/metadata":
            return asc_metadata(body)
        if method == "POST" and path == "/api/appstore/screenshots":
            return asc_screenshots(body)
        if method == "POST" and path == "/api/appstore/accept":
            return asc_accept(body)
        if method == "POST" and path == "/api/appstore/import":
            return asc_import(body)
        if method == "POST" and path == "/api/appstore/discover":
            return {"apps": appstore.discover(appstore.Client())}
        if method == "POST" and path == "/api/appstore/link":
            with ASC_LOCK:
                return {"app": appstore.link_app(appstore.Client(), str(body.get("app_store_id", ""))),
                        "status": appstore.status()}
        if method == "POST" and path == "/api/appstore/products":
            return appstore.products(appstore.Client(), str(body.get("app", "")))
        if method == "POST" and path == "/api/reveal":
            return reveal(str(body.get("path", "")))
        raise ApiError("không có endpoint này", 404)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            return self.handle_api("GET")
        if not self.allowed():
            return self.send_error(HTTPStatus.FORBIDDEN)
        if parsed.path == "/media":
            rel_path = unquote(parse_qs(parsed.query).get("path", [""])[0])
            target = (ROOT / rel_path).resolve()
            if not any(r in target.parents for r in MEDIA_ROOTS) or not target.is_file():
                return self.send_error(HTTPStatus.NOT_FOUND)
            return self.send_file(target)
        if parsed.path == "/asc-shot":
            target = asc_shot_file(parse_qs(parsed.query))
            if not target:
                return self.send_error(HTTPStatus.NOT_FOUND)
            return self.send_file(target)
        name = "index.html" if parsed.path in ("/", "") else parsed.path.lstrip("/")
        target = (STATIC / name).resolve()
        if STATIC not in target.parents or not target.is_file():
            return self.send_error(HTTPStatus.NOT_FOUND)
        self.send_file(target, cache=False)

    def do_POST(self):
        self.handle_api("POST")

    def do_DELETE(self):
        self.handle_api("DELETE")

    def send_file(self, path: Path, cache: bool = True):
        """Static/media with HTTP Range, so <video> can seek."""
        size = path.stat().st_size
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        status = 200
        if rng and (m := re.fullmatch(r"bytes=(\d*)-(\d*)", rng.strip())):
            if m[1]:
                start = int(m[1])
                end = int(m[2]) if m[2] else end
            elif m[2]:
                start = max(0, size - int(m[2]))
            end = min(end, size - 1)
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            status = 206
        self.send_response(status)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text/") else ""))
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "max-age=60" if cache else "no-cache")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with path.open("rb") as f:
            f.seek(start)
            remaining = end - start + 1
            try:
                while remaining > 0:
                    chunk = f.read(min(1 << 16, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass


def already_running(port: int) -> bool:
    """True when the process on that port is this dashboard (answers /api/state as we do)."""
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        conn.request("GET", "/", headers={"Host": f"127.0.0.1:{port}"})
        res = conn.getresponse()
        return res.getheader("Server", "").startswith(Handler.server_version)
    except OSError:
        return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8790)
    parser.add_argument("--no-open", action="store_true", help="không tự mở trình duyệt")
    args = parser.parse_args(argv)
    url = f"http://127.0.0.1:{args.port}/"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as exc:
        if exc.errno != errno.EADDRINUSE:
            raise
        if already_running(args.port):
            print(f"Dashboard đã chạy sẵn ở {url} — mở lại trong trình duyệt.")
            if not args.no_open:
                webbrowser.open(url)
            return 0
        print(f"Cổng {args.port} đang bị chương trình khác dùng. Chạy với cổng khác, ví dụ: "
              f"python3 tools/dashboard/server.py --port {args.port + 1}", file=sys.stderr)
        return 1
    print(f"KV Apps dashboard → {url}  (Ctrl+C để dừng)")
    if not args.no_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
