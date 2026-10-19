"""App Store listing: local copy (app repo) ↔ App Store Connect API.

Local side, needs nothing: reads `locales/<locale>/locale.json` and `screenshots/<locale>/*.jpg|png`
from the app repo listed in `docs/apps/registry.json` (`repo` + `store`), and checks App Store limits.

Remote side, needs an App Store Connect API key in `.env` (gitignored):

    ASC_KEY_ID=ABC123DEFG
    ASC_ISSUER_ID=69a6de7f-…
    ASC_PRIVATE_KEY=.secrets/appstore/AuthKey_ABC123DEFG.p8   # optional, this is the default

The JWT is signed with the system `openssl`, so the dashboard stays standard-library only.

Writes are always two steps: `plan_*` returns the exact operations, `apply_*` runs them. Nothing here
submits a version for review, changes prices or releases anything.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import struct
import subprocess
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import repo

API = "https://api.appstoreconnect.apple.com"
ENV_FILE = repo.ROOT / ".env"

# locale.json metadata key → (ASC resource, ASC attribute, limit, label)
FIELDS = {
    "name": ("info", "name", 30, "Tên app"),
    "subtitle": ("info", "subtitle", 30, "Subtitle"),
    "keywords": ("version", "keywords", 100, "Keywords"),
    "promotional_text": ("version", "promotionalText", 170, "Promotional text"),
    "description": ("version", "description", 4000, "Mô tả"),
    "whats_new": ("version", "whatsNew", 4000, "What's New"),
}
# Metadata is editable only before the version (or app info) is submitted.
EDITABLE = {"PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED", "METADATA_REJECTED",
            "INVALID_BINARY", "READY_FOR_REVIEW"}
# Pixel size → ASC display type. Portrait and landscape both map.
DISPLAY_TYPES = {
    (1320, 2868): "APP_IPHONE_67", (1290, 2796): "APP_IPHONE_67", (1260, 2736): "APP_IPHONE_67",
    (1284, 2778): "APP_IPHONE_65", (1242, 2688): "APP_IPHONE_65",
    (1206, 2622): "APP_IPHONE_61", (1179, 2556): "APP_IPHONE_61", (1170, 2532): "APP_IPHONE_61",
    (1125, 2436): "APP_IPHONE_58", (1080, 2340): "APP_IPHONE_58",
    (1242, 2208): "APP_IPHONE_55",
    (2064, 2752): "APP_IPAD_PRO_3GEN_129", (2048, 2732): "APP_IPAD_PRO_3GEN_129",
}
DISPLAY_LABELS = {"APP_IPHONE_67": 'iPhone 6.9"', "APP_IPHONE_65": 'iPhone 6.5"', "APP_IPHONE_61": 'iPhone 6.3"',
                  "APP_IPHONE_58": 'iPhone 5.8"', "APP_IPHONE_55": 'iPhone 5.5"',
                  "APP_IPAD_PRO_3GEN_129": 'iPad 13"'}
IMAGE_EXT = {".jpg", ".jpeg", ".png"}


class AscError(Exception):
    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


# --- configuration -------------------------------------------------------------------------

def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    values.update({k: v for k, v in os.environ.items() if k.startswith("ASC_")})
    return values


def credentials() -> dict:
    env = load_env()
    key_id, issuer = env.get("ASC_KEY_ID", ""), env.get("ASC_ISSUER_ID", "")
    key = Path(env.get("ASC_PRIVATE_KEY") or f".secrets/appstore/AuthKey_{key_id}.p8").expanduser()
    if not key.is_absolute():
        key = repo.ROOT / key
    return {"key_id": key_id, "issuer_id": issuer, "key_path": key,
            "ready": bool(key_id and issuer and key.is_file())}


def status() -> dict:
    cred = credentials()
    apps = []
    for app_id, app in repo.APPS.items():
        base = repo.app_repo(app_id)
        src = store_paths(app_id)
        apps.append({"id": app_id, "name": app["name"], "app_store_id": app.get("app_store_id"),
                     "bundle_id": app.get("bundle_id"), "repo": app.get("repo"),
                     "repo_path": str(base.relative_to(repo.WORKSPACE)) if base else None,
                     "has_source": bool(src and src["locales"].is_dir()),
                     "source": str(src["locales"].relative_to(repo.WORKSPACE)) if src else None})
    return {"configured": cred["ready"], "key_id": cred["key_id"] or None, "issuer": bool(cred["issuer_id"]),
            "key_file": cred["key_path"].is_file(),
            "key_path": str(cred["key_path"]).replace(str(repo.ROOT) + "/", "") if cred["key_id"]
            else ".secrets/appstore/AuthKey_<KEY_ID>.p8",
            "apps": apps}


def store_paths(app: str) -> dict | None:
    conf = repo.APPS.get(app, {}).get("store")
    base = repo.app_repo(app)
    if not conf or not base:
        return None
    return {"repo": base, "locales": base / conf["locales"], "screenshots": base / conf["screenshots"]}


# --- local listing -------------------------------------------------------------------------

def image_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as f:
        head = f.read(26)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", head[16:24])
        if head[:2] != b"\xff\xd8":
            return None
        f.seek(2)
        while True:
            marker = f.read(2)
            if len(marker) < 2 or marker[0] != 0xFF:
                return None
            if marker[1] in (0xD8, 0x01) or 0xD0 <= marker[1] <= 0xD7:
                continue
            length = struct.unpack(">H", f.read(2))[0]
            if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">xHH", f.read(5))
                return w, h
            f.seek(length - 2, 1)


_MD5_CACHE: dict[tuple, str] = {}


def md5(path: Path) -> str:
    st = path.stat()
    key = (str(path), st.st_size, st.st_mtime_ns)
    if key in _MD5_CACHE:
        return _MD5_CACHE[key]
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    _MD5_CACHE[key] = h.hexdigest()
    return _MD5_CACHE[key]


def local_screenshots(app: str, locale: str, checksum: bool = False) -> list[dict]:
    src = store_paths(app)
    folder = src["screenshots"] / locale if src else None
    if not folder or not folder.is_dir():
        return []
    shots = []
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in IMAGE_EXT or p.name.startswith("."):
            continue
        size = image_size(p)
        dtype = DISPLAY_TYPES.get(tuple(sorted(size))) if size else None
        shots.append({"file": p.name, "bytes": p.stat().st_size, "width": size[0] if size else None,
                      "height": size[1] if size else None, "display_type": dtype,
                      **({"checksum": md5(p)} if checksum else {})})
    return shots


def local_listing(app: str) -> dict:
    """Empty (not an error) when the app has no listing in its repo yet: the page then offers an import."""
    if app not in repo.APPS:
        raise AscError(f"Không có app {app} trong docs/apps/registry.json", 404)
    src = store_paths(app)
    if not src or not src["locales"].is_dir():
        return {"app": app, "source": None, "locales": {}}
    locales = {}
    for path in sorted(src["locales"].glob("*/locale.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise AscError(f"{path}: JSON lỗi ({exc})", 422) from None
        meta = data.get("metadata", {})
        fields = {k: (meta.get(k) or "").strip() for k in FIELDS}
        problems = [f"{FIELDS[k][3]} {len(v)}/{FIELDS[k][2]}" for k, v in fields.items() if len(v) > FIELDS[k][2]]
        shots = local_screenshots(app, path.parent.name, checksum=True)
        sizes = {(s["width"], s["height"]) for s in shots}
        if shots and len(sizes) > 1:
            problems.append("ảnh khác kích thước nhau")
        if shots and not all(s["display_type"] for s in shots):
            problems.append("ảnh có kích thước App Store không nhận")
        if len(shots) > 10:
            problems.append(f"{len(shots)} ảnh, tối đa 10")
        locales[path.parent.name] = {"fields": fields, "tier": data.get("tier"),
                                     "whats_new_version": data.get("whats_new_version"),
                                     "screenshots": shots, "problems": problems}
    return {"app": app, "source": str(src["locales"]), "locales": locales}


# --- App Store Connect client --------------------------------------------------------------

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def der_to_raw(sig: bytes) -> bytes:
    """openssl writes ECDSA as DER SEQUENCE{r, s}; JWS ES256 wants r‖s, 32 bytes each."""
    if sig[0] != 0x30:
        raise AscError("chữ ký openssl không phải DER")
    i = 3 if sig[1] & 0x80 else 2
    out = b""
    for _ in range(2):
        if sig[i] != 0x02:
            raise AscError("chữ ký openssl không đúng định dạng")
        n = sig[i + 1]
        out += sig[i + 2:i + 2 + n].lstrip(b"\x00").rjust(32, b"\x00")
        i += 2 + n
    return out


def make_token(key_id: str, issuer: str, key_path: Path, now: int | None = None) -> str:
    now = int(now or time.time())
    header = _b64(json.dumps({"alg": "ES256", "kid": key_id, "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64(json.dumps({"iss": issuer, "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"},
                              separators=(",", ":")).encode())
    signing_input = f"{header}.{payload}".encode()
    try:
        result = subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(key_path)], input=signing_input,
                                capture_output=True, timeout=20)
    except FileNotFoundError:
        raise AscError("không tìm thấy lệnh openssl", 500) from None
    if result.returncode:
        raise AscError(f"openssl không ký được bằng {key_path.name}: {result.stderr.decode(errors='replace')[-300:]}", 500)
    return f"{header}.{payload}.{_b64(der_to_raw(result.stdout))}"


class Client:
    def __init__(self, base: str | None = None, cred: dict | None = None):
        self.base = (base or API).rstrip("/")
        self.cred = cred or credentials()
        if not self.cred.get("ready"):
            raise AscError("Chưa cấu hình App Store Connect API key (ASC_KEY_ID, ASC_ISSUER_ID, file .p8).", 409)
        self._token, self._token_at = "", 0.0

    def token(self) -> str:
        if time.time() - self._token_at > 900:
            self._token = make_token(self.cred["key_id"], self.cred["issuer_id"], self.cred["key_path"])
            self._token_at = time.time()
        return self._token

    def request(self, method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
        url = path if path.startswith("http") else self.base + path
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {self.token()}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                raw = res.read()
        except urllib.error.HTTPError as exc:
            raise AscError(f"{method} {urllib.parse.urlparse(url).path}: {describe(exc)}", exc.code) from None
        except urllib.error.URLError as exc:
            raise AscError(f"Không kết nối được App Store Connect: {exc.reason}") from None
        return json.loads(raw) if raw else {}

    def get_all(self, path: str, params: dict | None = None) -> tuple[list, list]:
        """Follows links.next. Returns (data, included)."""
        data, included = [], []
        page = self.request("GET", path, params)
        while True:
            data += page.get("data") or []
            included += page.get("included") or []
            nxt = (page.get("links") or {}).get("next")
            if not nxt:
                return data, included
            page = self.request("GET", nxt)

    def upload(self, op: dict, chunk: bytes) -> None:
        headers = {h["name"]: h["value"] for h in op.get("requestHeaders") or []}
        req = urllib.request.Request(op["url"], data=chunk, method=op.get("method", "PUT"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=300):
                pass
        except urllib.error.HTTPError as exc:
            raise AscError(f"upload phần ảnh lỗi: HTTP {exc.code}") from None


def describe(exc: urllib.error.HTTPError) -> str:
    try:
        errors = json.loads(exc.read()).get("errors") or []
        msgs = [" — ".join(x for x in (e.get("title"), e.get("detail")) if x) for e in errors]
        return f"HTTP {exc.code}: " + "; ".join(m for m in msgs if m)
    except ValueError:
        return f"HTTP {exc.code}"


def state_of(attrs: dict) -> str:
    return attrs.get("appVersionState") or attrs.get("state") or attrs.get("appStoreState") or ""


# --- remote listing ------------------------------------------------------------------------

def app_store_id(app: str) -> str:
    asc_id = repo.APPS.get(app, {}).get("app_store_id")
    if not asc_id:
        raise AscError(f"{app} chưa liên kết App Store Connect (thiếu app_store_id trong docs/apps/registry.json)", 404)
    return asc_id


def remote_listing(client: Client, app: str, screenshots: bool = True) -> dict:
    asc_id = app_store_id(app)
    app_attrs = client.request("GET", f"/v1/apps/{asc_id}")["data"]["attributes"]

    versions, _ = client.get_all(f"/v1/apps/{asc_id}/appStoreVersions",
                                 {"filter[platform]": "IOS", "limit": 10})
    versions.sort(key=lambda v: v["attributes"].get("createdDate") or "", reverse=True)
    editable = next((v for v in versions if state_of(v["attributes"]) in EDITABLE), None)
    live = next((v for v in versions if state_of(v["attributes"]) == "READY_FOR_DISTRIBUTION"), None)
    version = editable or live or (versions[0] if versions else None)

    infos, _ = client.get_all(f"/v1/apps/{asc_id}/appInfos")
    info = next((i for i in infos if state_of(i["attributes"]) in EDITABLE), None) or (infos[0] if infos else None)

    locales: dict[str, dict] = {}
    if info:
        for loc in client.get_all(f"/v1/appInfos/{info['id']}/appInfoLocalizations", {"limit": 50})[0]:
            a = loc["attributes"]
            locales.setdefault(a["locale"], {}).update({
                "info_loc_id": loc["id"], "name": a.get("name") or "", "subtitle": a.get("subtitle") or "",
                "privacy_url": a.get("privacyPolicyUrl")})
    if version:
        for loc in client.get_all(f"/v1/appStoreVersions/{version['id']}/appStoreVersionLocalizations",
                                  {"limit": 50})[0]:
            a = loc["attributes"]
            locales.setdefault(a["locale"], {}).update({
                "version_loc_id": loc["id"], "keywords": a.get("keywords") or "",
                "promotional_text": a.get("promotionalText") or "", "description": a.get("description") or "",
                "whats_new": a.get("whatsNew") or "", "support_url": a.get("supportUrl"),
                "marketing_url": a.get("marketingUrl")})

    shots: dict[str, dict] = {}
    if screenshots and version:
        targets = [(code, l["version_loc_id"]) for code, l in locales.items() if l.get("version_loc_id")]
        with ThreadPoolExecutor(max_workers=6) as pool:
            for code, sets in pool.map(lambda t: (t[0], screenshot_sets(client, t[1])), targets):
                shots[code] = sets

    def vinfo(v):
        return v and {"id": v["id"], "version": v["attributes"].get("versionString"),
                      "state": state_of(v["attributes"]), "editable": state_of(v["attributes"]) in EDITABLE}

    return {
        "app": {"id": asc_id, "name": app_attrs.get("name"), "bundle_id": app_attrs.get("bundleId"),
                "primary_locale": app_attrs.get("primaryLocale")},
        "version": vinfo(version), "live_version": vinfo(live),
        "info": info and {"id": info["id"], "state": state_of(info["attributes"]),
                          "editable": state_of(info["attributes"]) in EDITABLE},
        "locales": locales, "screenshots": shots,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }


def screenshot_sets(client: Client, version_loc_id: str) -> dict:
    sets, included = client.get_all(f"/v1/appStoreVersionLocalizations/{version_loc_id}/appScreenshotSets",
                                    {"include": "appScreenshots", "limit": 50, "limit[appScreenshots]": 10})
    by_id = {x["id"]: x for x in included if x.get("type") == "appScreenshots"}
    out = {}
    for s in sets:
        order = ((s.get("relationships") or {}).get("appScreenshots") or {}).get("data") or []
        items = []
        for ref in order:
            a = by_id.get(ref["id"], {}).get("attributes", {})
            items.append({"id": ref["id"], "file": a.get("fileName"), "checksum": a.get("sourceFileChecksum"),
                          "state": ((a.get("assetDeliveryState") or {}).get("state")),
                          "url": thumb(a.get("imageAsset"))})
        out[s["attributes"]["screenshotDisplayType"]] = {"set_id": s["id"], "items": items}
    return out


def thumb(asset: dict | None, width: int = 300) -> str | None:
    if not asset or not asset.get("templateUrl"):
        return None
    h = round(width * asset.get("height", 2) / max(asset.get("width", 1), 1))
    return asset["templateUrl"].replace("{w}", str(width)).replace("{h}", str(h)).replace("{f}", "jpg")


# --- compare -------------------------------------------------------------------------------
#
# A field's state, from the local text, the text on ASC and the last mark both sides agreed on:
#   same      equal after normalizing (also when you pasted it into ASC by hand)
#   new       ASC has nothing yet
#   ahead     ASC still holds what we last agreed on; only local changed → safe to push
#   conflict  ASC changed after the last mark (edited in App Store Connect) → push only on explicit override
#   differs   they differ and there is no mark: unknown which side is newer → override only
#   accepted  you chose to keep the ASC text; stays put until local changes again (then: ahead)
#   empty     nothing local to send

AUTO = {"new", "ahead"}
OVERRIDE = {"conflict", "differs", "accepted"}
STATE_VI = {"same": "đã khớp", "new": "ASC còn trống", "ahead": "local mới hơn", "conflict": "ASC đã sửa tay sau lần đồng bộ",
            "differs": "khác ASC, chưa có mốc", "accepted": "đang giữ bản ASC", "empty": "local trống"}


def normalize(key: str, text: str | None) -> str:
    """What App Store Connect treats as the same text: NFC, \n newlines, no trailing spaces; keywords as a list."""
    t = unicodedata.normalize("NFC", text or "").replace("\r\n", "\n").replace("\r", "\n")
    t = "\n".join(line.rstrip() for line in t.split("\n")).strip()
    if key == "keywords":
        t = ",".join(k.strip() for k in t.split(",") if k.strip())
    return t


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def state(local: str, remote: str, mark: dict | None) -> str:
    if not local:
        return "empty"
    if not remote:
        return "new"
    lh, rh = digest(local), digest(remote)
    if lh == rh:
        return "same"
    if not mark:
        return "differs"
    if mark["remote_hash"] != rh:
        return "conflict"
    return "accepted" if mark["local_hash"] == lh else "ahead"


def shots_key(shots: list[dict]) -> str:
    return ",".join(s.get("checksum") or "" for s in shots)


def remote_shots(remote: dict, code: str, dtype: str | None) -> list[dict]:
    return ((remote.get("screenshots", {}).get(code) or {}).get(dtype) or {}).get("items") or []


def field_editable(remote: dict, key: str) -> tuple[bool, str]:
    resource = FIELDS[key][0]
    if resource == "info":
        if not remote.get("info"):
            return False, "app chưa có App Information"
        return (True, "") if remote["info"]["editable"] else (False, "chỉ sửa khi có version mới đang chuẩn bị")
    v = remote.get("version")
    if not v:
        return False, "app chưa có version nào"
    if v["editable"] or key == "promotional_text":
        return True, ""
    return False, f"version {v['version']} đang {v['state']}, chưa có version mới để sửa"


def compare(local: dict, remote: dict | None, marks: dict | None = None) -> dict:
    """Rows for the page, plus `matched`: fields equal on both sides whose mark should be (re)recorded, so a
    later local edit shows as `ahead` instead of `differs`."""
    marks = marks or {}
    rows, matched = [], []
    for code, l in local["locales"].items():
        r = (remote or {}).get("locales", {}).get(code)
        fields = {}
        for key, (_, _, limit, label) in FIELDS.items():
            value = l["fields"][key]
            entry = {"local": value, "len": len(value), "limit": limit, "over": len(value) > limit}
            if remote is not None:
                current = (r or {}).get(key) or ""
                mark = marks.get((code, key))
                st = state(normalize(key, value), normalize(key, current), mark)
                entry.update(remote=current, status=st, mark=mark and {"how": mark["how"], "at": mark["at"]})
                entry["editable"], entry["why"] = field_editable(remote, key)
                if st == "same" and (not mark or mark["local_hash"] != digest(normalize(key, value))):
                    matched.append((code, key, digest(normalize(key, value))))
            fields[key] = entry
        row = {"locale": code, "tier": l["tier"], "fields": fields, "problems": l["problems"],
               "whats_new_version": l["whats_new_version"], "shots": len(l["screenshots"]),
               "display_type": next((s["display_type"] for s in l["screenshots"] if s["display_type"]), None)}
        if remote is not None:
            row["remote_exists"] = bool(r)
            remote_items = remote_shots(remote, code, row["display_type"])
            lk, rk = shots_key(l["screenshots"]), shots_key(remote_items)
            mark = marks.get((code, "screenshots"))
            row["shots_status"] = "none" if not l["screenshots"] else state(lk, rk, mark)
            row["shots_remote"] = len(remote_items)
            if row["shots_status"] == "same" and (not mark or mark["local_hash"] != digest(lk)):
                matched.append((code, "screenshots", digest(lk)))
        rows.append(row)
    extra = sorted(set((remote or {}).get("locales", {})) - set(local["locales"]))
    return {"rows": rows, "remote_only": extra, "matched": matched}


# --- metadata push -------------------------------------------------------------------------

def plan_metadata(local: dict, remote: dict, items: list[dict], marks: dict | None = None) -> list[dict]:
    """items: [{locale, fields: [key…], override: [key…]}] → ordered operations.

    Equal fields are skipped, so pushing twice never sends anything twice. `ahead`/`new` fields go through;
    a field ASC changed by hand (`conflict`, `differs`, `accepted`) only when it is listed in `override`.
    Raises on anything App Store Connect would reject."""
    if not items:
        raise AscError("Chưa chọn locale hay field nào.", 400)
    marks = marks or {}
    primary = remote["locales"].get(remote["app"]["primary_locale"]) or {}
    ops = []
    for item in items:
        code = item.get("locale")
        if code not in local["locales"]:
            raise AscError(f"{code}: không có trong dữ liệu local", 400)
        wanted = [k for k in item.get("fields") or [] if k in FIELDS]
        override = set(item.get("override") or [])
        l, r = local["locales"][code]["fields"], remote["locales"].get(code, {})
        for resource in ("info", "version"):
            attrs, keys = {}, []
            for key in wanted:
                res, attr, limit, label = FIELDS[key]
                if res != resource:
                    continue
                st = state(normalize(key, l[key]), normalize(key, r.get(key)), marks.get((code, key)))
                # Equal, nothing local, or "keep the ASC text": skip quietly unless explicitly overridden.
                if st in ("same", "empty") or (st == "accepted" and key not in override):
                    continue
                if st in OVERRIDE and key not in override:
                    raise AscError(f"{code} · {label}: {STATE_VI[st]}. Tick ghi đè nếu muốn thay bản trên ASC.", 409)
                if len(l[key]) > limit:
                    raise AscError(f"{code} · {label} dài {len(l[key])}/{limit} ký tự", 422)
                ok, why = field_editable(remote, key)
                if not ok:
                    raise AscError(f"{code} · {label}: {why}", 409)
                attrs[attr] = l[key]
                keys.append(key)
            if not attrs:
                continue
            loc_id = r.get(f"{resource}_loc_id")
            target = remote[resource]["id"]
            values = {k: l[k] for k in keys}
            if loc_id:
                ops.append({"op": "update", "resource": resource, "locale": code, "id": loc_id,
                            "fields": keys, "attributes": attrs, "values": values})
                continue
            if resource == "info" and primary.get("privacy_url"):
                attrs["privacyPolicyUrl"] = primary["privacy_url"]
            if resource == "version":
                for src, dst in (("support_url", "supportUrl"), ("marketing_url", "marketingUrl")):
                    if primary.get(src):
                        attrs[dst] = primary[src]
            ops.append({"op": "create", "resource": resource, "locale": code, "parent": target,
                        "fields": keys, "attributes": {"locale": code, **attrs}, "values": values})
    # A new language must exist in App Information before its version localization.
    ops.sort(key=lambda o: (o["locale"], o["resource"] != "info"))
    return ops


RESOURCE = {"info": ("appInfoLocalizations", "appInfo", "appInfos"),
            "version": ("appStoreVersionLocalizations", "appStoreVersion", "appStoreVersions")}


def apply_metadata(client: Client, ops: list[dict], on_done=None) -> list[dict]:
    """Runs ops in order. `on_done(op)` is called after each success, so marks are saved even if a later op
    fails — the next plan then skips what already went through instead of sending it again."""
    done = []
    for op in ops:
        kind, rel, parent_type = RESOURCE[op["resource"]]
        try:
            if op["op"] == "update":
                client.request("PATCH", f"/v1/{kind}/{op['id']}", body={"data": {
                    "type": kind, "id": op["id"], "attributes": op["attributes"]}})
            else:
                client.request("POST", f"/v1/{kind}", body={"data": {
                    "type": kind, "attributes": op["attributes"],
                    "relationships": {rel: {"data": {"type": parent_type, "id": op["parent"]}}}}})
        except AscError as exc:
            raise AscError(f"Dừng ở {op['locale']} ({op['resource']}): {exc}. {len(done)} lệnh trước đó đã xong.",
                           exc.status) from None
        done.append({**op, "ok": True})
        if on_done:
            on_done(op)
    return done


def pushed_marks(op: dict) -> list[tuple[str, str, str]]:
    return [(op["locale"], key, digest(normalize(key, value))) for key, value in op["values"].items()]


# --- screenshots push ----------------------------------------------------------------------

def plan_screenshots(app: str, remote: dict, code: str, marks: dict | None = None, override: bool = False) -> dict:
    shots = local_screenshots(app, code, checksum=True)
    if not shots:
        raise AscError(f"{code}: không có ảnh local", 404)
    types = {s["display_type"] for s in shots}
    if None in types or len(types) != 1:
        sizes = ", ".join("%s %s×%s" % (s["file"], s["width"], s["height"]) for s in shots)
        raise AscError(f"{code}: ảnh phải cùng một kích thước App Store nhận ({sizes})", 422)
    if len(shots) > 10:
        raise AscError(f"{code}: {len(shots)} ảnh, App Store nhận tối đa 10", 422)
    v = remote.get("version")
    if not v or not v["editable"]:
        raise AscError("Screenshot chỉ thay được trên version đang chuẩn bị (Prepare for Submission).", 409)
    loc = remote["locales"].get(code, {})
    if not loc.get("version_loc_id"):
        raise AscError(f"{code}: version chưa có ngôn ngữ này. Đẩy metadata của locale trước.", 409)
    dtype = types.pop()
    current = remote.get("screenshots", {}).get(code, {}).get(dtype) or {"set_id": None, "items": []}
    st = state(shots_key(shots), shots_key(current["items"]), (marks or {}).get((code, "screenshots")))
    if st in OVERRIDE and not override:
        raise AscError(f"{code}: ảnh trên ASC {STATE_VI[st]}. Xác nhận ghi đè nếu muốn thay.", 409)
    same = st == "same"
    return {"locale": code, "display_type": dtype, "label": DISPLAY_LABELS.get(dtype, dtype), "status": st,
            "version_loc_id": loc["version_loc_id"], "set_id": current["set_id"],
            "delete": [] if same else [i["id"] for i in current["items"]],
            "upload": [] if same else shots, "unchanged": same, "key": digest(shots_key(shots)),
            "remote_files": [i["file"] for i in current["items"]]}


def apply_screenshots(client: Client, app: str, plan: dict) -> dict:
    if plan["unchanged"]:
        return {"uploaded": 0, "deleted": 0}
    folder = store_paths(app)["screenshots"] / plan["locale"]
    set_id = plan["set_id"]
    if not set_id:
        set_id = client.request("POST", "/v1/appScreenshotSets", body={"data": {
            "type": "appScreenshotSets", "attributes": {"screenshotDisplayType": plan["display_type"]},
            "relationships": {"appStoreVersionLocalization": {"data": {
                "type": "appStoreVersionLocalizations", "id": plan["version_loc_id"]}}}}})["data"]["id"]
    # Delete first: a set holds at most 10, so old + new would not fit.
    for shot_id in plan["delete"]:
        client.request("DELETE", f"/v1/appScreenshots/{shot_id}")
    new_ids = []
    for shot in plan["upload"]:
        data = (folder / shot["file"]).read_bytes()
        res = client.request("POST", "/v1/appScreenshots", body={"data": {
            "type": "appScreenshots", "attributes": {"fileName": shot["file"], "fileSize": len(data)},
            "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": set_id}}}}})["data"]
        for op in res["attributes"].get("uploadOperations") or []:
            client.upload(op, data[op["offset"]:op["offset"] + op["length"]])
        client.request("PATCH", f"/v1/appScreenshots/{res['id']}", body={"data": {
            "type": "appScreenshots", "id": res["id"],
            "attributes": {"uploaded": True, "sourceFileChecksum": shot["checksum"]}}})
        new_ids.append(res["id"])
    client.request("PATCH", f"/v1/appScreenshotSets/{set_id}/relationships/appScreenshots",
                   body={"data": [{"type": "appScreenshots", "id": i} for i in new_ids]})
    return {"uploaded": len(new_ids), "deleted": len(plan["delete"]), "set_id": set_id}


# --- products (read-only) ------------------------------------------------------------------

def products(client: Client, app: str, territory: str = "USA") -> dict:
    asc_id = app_store_id(app)
    groups, included = client.get_all(f"/v1/apps/{asc_id}/subscriptionGroups",
                                      {"include": "subscriptions", "limit": 50})
    subs = {x["id"]: x for x in included if x.get("type") == "subscriptions"}
    out_groups = []
    for g in groups:
        items = []
        for ref in ((g.get("relationships") or {}).get("subscriptions") or {}).get("data") or []:
            s = subs.get(ref["id"])
            if not s:
                continue
            a = s["attributes"]
            items.append({"id": s["id"], "name": a.get("name"), "product_id": a.get("productId"),
                          "state": a.get("state"), "period": a.get("subscriptionPeriod"),
                          "level": a.get("groupLevel"), "price": subscription_price(client, s["id"], territory)})
        items.sort(key=lambda x: x["level"] or 0)
        out_groups.append({"id": g["id"], "name": g["attributes"].get("referenceName"), "subscriptions": items})
    iaps = []
    for p in client.get_all(f"/v1/apps/{asc_id}/inAppPurchasesV2", {"limit": 200})[0]:
        a = p["attributes"]
        iaps.append({"id": p["id"], "name": a.get("name"), "product_id": a.get("productId"),
                     "type": a.get("inAppPurchaseType"), "state": a.get("state")})
    return {"territory": territory, "groups": out_groups, "iaps": iaps}


def subscription_price(client: Client, sub_id: str, territory: str) -> dict | None:
    try:
        prices, included = client.get_all(f"/v1/subscriptions/{sub_id}/prices", {
            "filter[territory]": territory, "include": "subscriptionPricePoint", "limit": 50})
    except AscError:
        return None
    points = {x["id"]: x["attributes"] for x in included if x.get("type") == "subscriptionPricePoints"}
    today = dt.date.today().isoformat()
    current = [p for p in prices if (p["attributes"].get("startDate") or "") <= today]
    current.sort(key=lambda p: p["attributes"].get("startDate") or "")
    if not current:
        return None
    ref = ((current[-1].get("relationships") or {}).get("subscriptionPricePoint") or {}).get("data") or {}
    pp = points.get(ref.get("id"), {})
    return {"price": pp.get("customerPrice"), "proceeds": pp.get("proceeds")} if pp else None


# --- apps on App Store Connect ↔ registry ----------------------------------------------------

def find_repo_for_bundle(bundle_id: str) -> str | None:
    """A checkout under ~/personal/Apps (or the workspace root) whose project declares this bundle id."""
    needle = bundle_id.encode()
    for group in ("Apps", ""):
        base = repo.WORKSPACE / group
        if not base.is_dir():
            continue
        for d in sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")):
            files = [*d.glob("*.xcodeproj/project.pbxproj"), *d.glob("*/*.xcodeproj/project.pbxproj"),
                     *d.glob("project.yml"), *d.glob("*/project.yml")]
            if any(needle in f.read_bytes() for f in files):
                return str(d.relative_to(repo.WORKSPACE))
    return None


def discover(client: Client) -> list[dict]:
    """Every app of the team on App Store Connect, matched to the registry by App Store ID or bundle id."""
    apps, _ = client.get_all("/v1/apps", {"limit": 200, "fields[apps]": "name,bundleId,primaryLocale,sku"})
    by_store = {a.get("app_store_id"): k for k, a in repo.APPS.items() if a.get("app_store_id")}
    by_bundle = {a.get("bundle_id"): k for k, a in repo.APPS.items() if a.get("bundle_id")}
    out = []
    for a in apps:
        attrs = a["attributes"]
        linked = by_store.get(a["id"])
        match = linked or by_bundle.get(attrs.get("bundleId"))
        out.append({"app_store_id": a["id"], "name": attrs.get("name"), "bundle_id": attrs.get("bundleId"),
                    "registry_id": match, "linked": bool(linked),
                    "repo": repo.APPS[match].get("repo") if match else find_repo_for_bundle(attrs.get("bundleId") or "")})
    return sorted(out, key=lambda x: (x["linked"], x["name"] or ""))


def slug(name: str) -> str:
    base = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return "-".join(w for w in "".join(c if c.isalnum() else " " for c in base).split()) or "app"


def link_app(client: Client, app_store_id: str) -> str:
    """Adds an ASC app to the registry, or fills in the App Store ID of the matching registry entry."""
    found = next((a for a in discover(client) if a["app_store_id"] == app_store_id), None)
    if not found:
        raise AscError(f"Không thấy app {app_store_id} trong tài khoản App Store Connect này", 404)
    app_id = found["registry_id"] or slug(found["name"])
    while not found["registry_id"] and app_id in repo.APPS:
        app_id += "-app"
    entry = {"app_store_id": app_store_id, "bundle_id": found["bundle_id"]}
    if not found["registry_id"]:
        entry.update(name=found["name"], repo=found["repo"], store=None)
    repo.save_app(app_id, entry)
    return app_id


# --- import ASC → app repo -------------------------------------------------------------------

IMPORT_STORE = {"locales": "AppStore/locales", "screenshots": "AppStore/screenshots"}


def import_listing(app: str, remote: dict) -> dict:
    """Writes `locales/<locale>/locale.json` in the app repo for every ASC locale that has no local file yet.

    Never overwrites. For an app whose listing you localized by hand in App Store Connect, this makes the repo
    the source of truth without retyping, and every imported field starts as `same` (nothing to push)."""
    base = repo.app_repo(app)
    if not base:
        raise AscError(f"Không tìm thấy repo của {app} trong {repo.WORKSPACE} (registry: {repo.APPS[app].get('repo')})", 404)
    if not repo.APPS[app].get("store"):
        repo.save_app(app, {"store": dict(IMPORT_STORE)})
    src = store_paths(app)
    created, skipped = [], []
    today = dt.date.today().isoformat()
    for code, r in sorted(remote["locales"].items()):
        target = src["locales"] / code / "locale.json"
        if target.exists():
            skipped.append(code)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        meta = {k: r.get(k) or "" for k in FIELDS}
        target.write_text(json.dumps({"locale": code, "tier": None, "imported_from_asc": today,
                                      "whats_new_version": (remote.get("version") or {}).get("version"),
                                      "metadata": meta}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created.append(code)
    return {"created": created, "skipped": skipped, "folder": str(src["locales"].relative_to(repo.WORKSPACE))}
