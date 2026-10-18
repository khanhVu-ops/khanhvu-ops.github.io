"""Read the studio repo into one JSON-able state, and write back the few things the dashboard owns.

The repo stays the source of truth: briefs, render configs, the 14-day plan, ACCOUNTS.md and the
channel logs (POSTS.md, UPLOADS.md) are parsed on every request. The dashboard only writes:
new rows / result cells in POSTS.md, and docs/social/campaign-links.json.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import re
import secrets
import sys
import tomllib
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
CHANNELS_DIR = ROOT / "docs/social/channels"
PLAN = ROOT / "docs/content/VEILNEST_14_DAYS.md"
ACCOUNTS = ROOT / "docs/social/ACCOUNTS.md"
CAMPAIGNS = ROOT / "docs/social/campaign-links.json"
ICT = dt.timezone(dt.timedelta(hours=7))

APPS = {
    "veilnest": {"name": "Veilnest", "app_store_id": "6813747332"},
    "color-meter": {"name": "Color Meter", "app_store_id": None},
    "paper-drift": {"name": "Paper Drift", "app_store_id": None},
}

# Fixed order = fixed categorical colour slot in the UI (never re-assigned by rank).
CHANNELS = [
    {"key": "youtube", "label": "YouTube Shorts", "account": "YouTube", "short": "yt_shorts"},
    {"key": "tiktok", "label": "TikTok", "account": "TikTok", "short": "tiktok"},
    {"key": "instagram", "label": "Instagram Reels", "account": "Instagram", "short": "ig_reels"},
    {"key": "threads", "label": "Threads", "account": "Threads", "short": "threads"},
    {"key": "facebook", "label": "Facebook Page", "account": "Facebook Page", "short": "fb_page"},
    {"key": "reddit", "label": "Reddit", "account": "Reddit", "short": "reddit"},
    {"key": "facebook-groups", "label": "Nhóm Facebook", "account": None, "short": "fb_groups"},
]


class RepoError(Exception):
    """A write the dashboard refuses: unknown channel, bad input, row not found."""


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_content", ROOT / "tools/check-content.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_content"] = module  # dataclasses look their module up while decorating
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


check_content = _load_checker()
md_tables = check_content.md_tables
split_row = check_content.split_row
parse_when = check_content.parse_when


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def md_link(cell: str) -> tuple[str, str | None]:
    """`[label](url)` → (label, url); plain text → (text, None)."""
    m = re.search(r"\[([^\]]+)\]\(([^)\s]+)\)", cell)
    if m:
        return m[1], m[2]
    return cell.strip(), None


def plain(cell: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", cell)
    return re.sub(r"[*`]", "", text).strip()


def section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m[1] if m else ""


# --- creatives ---------------------------------------------------------------------------

def creative_state(c, captions: dict[str, str]) -> dict:
    exports = c.dir / "exports"
    renders = []
    for name, entry in sorted(c.manifest.items()):
        if not isinstance(entry, dict):
            continue
        cover = entry.get("cover")
        renders.append({
            "file": entry.get("file"), "name": name, "variant": entry.get("variant"), "hook": entry.get("hook"),
            "draft": bool(entry.get("draft")), "duration": entry.get("duration"), "bytes": entry.get("bytes"),
            "lufs": entry.get("integrated_lufs"), "true_peak": entry.get("true_peak_dbtp"),
            "cover": cover if cover and (ROOT / cover).is_file() else None,
            "sheet": entry.get("review_sheet"), "preview": entry.get("safezone_preview"),
            "exists": bool(entry.get("file")) and (ROOT / entry["file"]).is_file(),
            "warnings": entry.get("warnings", []), "rendered_at": entry.get("rendered_at"),
        })
    layout = exports / "review" / f"{c.id}-layout.jpg"
    variants = []
    for vid, hook in sorted(c.hooks.items()):
        meta = c.metas.get(vid) or {}
        yt = meta.get("youtube", {}) if isinstance(meta, dict) else {}
        meta_file = c.dir / f"youtube-{vid}.toml"
        variants.append({"id": vid, "hook": hook, "title": yt.get("title"), "description": yt.get("description"),
                         "tags": yt.get("tags", []), "meta_file": meta_file.name if meta_file.is_file() else None})
    lang = "vi" if "-vi-" in c.id else ("en" if "-en-" in c.id else None)
    concept = re.sub(r"^\d{4}-\d{2}-\d{2}-|-(en|vi)-v\d+$", "", c.id)
    fields = c.fields
    return {
        "id": c.id, "app": c.app, "app_name": APPS.get(c.app, {}).get("name", c.app), "path": rel(c.dir),
        "has_brief": c.has_brief, "status": c.status or "Pack", "pro": c.pro, "lang": lang, "concept": concept,
        "situation": plain(fields.get("Tình huống người dùng", "")),
        "benefit": plain(fields.get("Một lợi ích chính", "")),
        "footage": plain(fields.get("Footage thật / AI / mockup", "")),
        "duration_plan": plain(fields.get("Thời lượng / tỷ lệ khung", "")),
        "channels_plan": plain(fields.get("Kênh dự kiến", "")),
        "based_on": plain(fields.get("Based on", "")),
        "cta": plain(fields.get("CTA / URL đích đã xác minh", "")),
        "variants": variants, "renders": renders, "master": c.master,
        "layout": rel(layout) if layout.is_file() else None,
        "plan_days": c.plan_days, "slots": c.slots, "posted_on": sorted(set(c.posts)), "uploads": c.uploads,
        "caption": captions.get(f"{concept}|{lang}") or captions.get(f"{concept}|en" if lang == "en" else ""),
        "has_render_config": (c.dir / "render.toml").is_file(),
    }


# --- plan ---------------------------------------------------------------------------------

def read_plan(creatives: list[dict]) -> tuple[list[dict], dict[str, str]]:
    if not PLAN.is_file():
        return [], {}
    text = PLAN.read_text(encoding="utf-8")

    def match(video: str) -> dict | None:
        words = plain(video).split()
        if not words:
            return None
        concept = words[0]
        lang = (words[1].lower() if len(words) > 1 and words[1].upper() in ("EN", "VI") else "en")
        return next((c for c in creatives if c["concept"] == concept and c["lang"] == lang), None)

    captions = {}
    for header, rows in md_tables(section(text, "Caption")):
        for _, cells in rows:
            words = plain(cells[0]).split()
            if words:
                lang = words[1].lower() if len(words) > 1 else "en"
                captions[f"{words[0]}|{lang}"] = plain(cells[1])

    days = []
    for header, rows in md_tables(section(text, "Lịch")):
        if header[:2] != ["Ngày", "Video"]:
            continue
        for _, cells in rows:
            day, video, hook, channels, community, status = (cells + [""] * 6)[:6]
            creative = match(video)
            hook_text = plain(hook)
            variant = None
            m = re.match(r"([A-Z])\s*·\s*(.*)", hook_text)
            if m:
                variant, hook_text = m[1].lower(), m[2]
            community_label, community_url = md_link(community)
            days.append({
                "day": plain(day), "video": plain(video), "creative": creative["id"] if creative else None,
                "variant": variant, "hook": hook_text, "channels": plain(channels),
                "community": plain(community_label) if community_label not in ("—", "") else None,
                "status": plain(status),
            })
    return days, captions


# --- accounts -----------------------------------------------------------------------------

def read_accounts() -> list[dict]:
    if not ACCOUNTS.is_file():
        return []
    out = []
    for header, rows in md_tables(ACCOUNTS.read_text(encoding="utf-8")):
        if header[:1] != ["Nền tảng"]:
            continue
        for _, cells in rows:
            platform, profile, status, owner, todo = (cells + [""] * 5)[:5]
            label, url = md_link(profile)
            channel = next((c["key"] for c in CHANNELS if c["account"] == plain(platform)), None)
            out.append({"platform": plain(platform), "channel": channel, "profile": plain(label), "url": url,
                        "status": plain(status), "owner": plain(owner), "todo": plain(todo)})
    return out


# --- channel logs --------------------------------------------------------------------------

FIELD_HEADERS = [
    ("when", ("Ngày giờ",)), ("creative", ("Creative ID", "App / creative ID")), ("app", ("App",)),
    ("lang", ("Ngôn ngữ",)), ("url", ("URL",)), ("link", ("Link đích", "Có link?")), ("place", ("Subreddit", "Nhóm")),
    ("kind", ("Loại",)), ("rules_read", ("Rule đã đọc", "Nội quy")), ("result", ("Kết quả",)),
]


def header_fields(header: list[str]) -> list[str | None]:
    names = []
    for cell in header:
        found = None
        for key, prefixes in FIELD_HEADERS:
            if any(cell.startswith(p) for p in prefixes):
                found = key
                break
        names.append(found)
    return names


def post_table(path: Path) -> tuple[list[str], int, int, int] | None:
    """(header cells, header line idx, separator idx, last row idx) for the log table with a result column."""
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines[:-1]):
        if line.lstrip().startswith("|") and "Kết quả" in line and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            last = i + 1
            while last + 1 < len(lines) and lines[last + 1].lstrip().startswith("|"):
                last += 1
            return split_row(line), i, i + 1, last
    return None


def read_posts(now: dt.datetime) -> list[dict]:
    posts = []
    for path in sorted(CHANNELS_DIR.glob("*/POSTS.md")):
        table = post_table(path)
        if not table:
            continue
        header, _, sep, last = table
        names = header_fields(header)
        lines = path.read_text(encoding="utf-8").splitlines()
        for n in range(sep + 1, last + 1):
            cells = (split_row(lines[n]) + [""] * len(header))[:len(header)]
            row = {name: plain(cells[i]) for i, name in enumerate(names) if name}
            url_label, url = md_link(next((cells[i] for i, name in enumerate(names) if name == "url"), ""))
            row["url"] = url or (url_label if url_label.startswith("http") else row.get("url"))
            when = parse_when(row.get("when", ""))
            row.update(channel=path.parent.name, line=n + 1, file=rel(path),
                       at=when.isoformat() if when else None,
                       age_hours=round((now - when).total_seconds() / 3600, 1) if when else None)
            m = re.search(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+?-v\d+(?:-hook([a-z0-9]+))?", " ".join(cells))
            row["creative_id"] = re.sub(r"-hook[a-z0-9]+$", "", m[0]) if m else None
            row["variant"] = m[1] if m and m[1] else None
            posts.append(row)
    return posts


def read_uploads() -> list[dict]:
    path = CHANNELS_DIR / "youtube/UPLOADS.md"
    if not path.is_file():
        return []
    out = []
    for header, rows in md_tables(path.read_text(encoding="utf-8")):
        if "Video ID" not in header:
            continue
        for _, cells in rows:
            row = dict(zip(header, (plain(c) for c in cells)))
            out.append({"at": row.get("Thời điểm upload"), "creative_id": row.get("Creative ID"),
                        "export": row.get("Bản export"), "video_id": row.get("Video ID"), "url": row.get("URL"),
                        "privacy": row.get("Privacy lúc upload"), "scheduled": row.get("Hẹn public (UTC)")})
    return out


def cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def append_post(channel: str, data: dict) -> dict:
    """Add one row to docs/social/channels/<channel>/POSTS.md, filling columns by header name."""
    path = CHANNELS_DIR / channel / "POSTS.md"
    if channel not in {c["key"] for c in CHANNELS} or not path.is_file():
        raise RepoError(f"kênh '{channel}' không có POSTS.md")
    url = str(data.get("url", "")).strip()
    if not re.match(r"^https://\S+$", url):
        raise RepoError("URL bài đăng phải bắt đầu bằng https://")
    when = parse_when(str(data.get("when", "")))
    if not when:
        raise RepoError("thời điểm đăng không hợp lệ (ví dụ 2026-10-20 08:00)")
    if when > dt.datetime.now(ICT) + dt.timedelta(minutes=5):
        raise RepoError("thời điểm đăng ở tương lai; chỉ ghi bài đã đăng thật")
    table = post_table(path)
    if not table:
        raise RepoError(f"{rel(path)} không có bảng nhật ký")
    header, _, _, last = table
    if url in path.read_text(encoding="utf-8"):
        raise RepoError("URL này đã có trong nhật ký")
    creative = str(data.get("creative", "")).strip()
    values = {
        "when": when.astimezone(ICT).strftime("%Y-%m-%d %H:%M ICT"),
        "app": APPS.get(data.get("app", ""), {}).get("name", data.get("app", "")),
        "creative": f"`{creative}`" if creative else "—", "lang": str(data.get("lang", "")).upper(),
        "url": url, "link": data.get("link") or "—", "place": data.get("place") or "—",
        "kind": data.get("kind") or "bài", "rules_read": data.get("rules_read") or "—", "result": "",
    }
    names = header_fields(header)
    cells = [cell(values.get(name, "—")) if name else "—" for name in names]
    if "app" in names and "creative" not in names and creative:
        cells[names.index("app")] = cell(f"{values['app']} · `{creative}`")
    row = "| " + " | ".join(cells) + " |"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines.insert(last + 1, row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"file": rel(path), "row": row}


def write_result(channel: str, url: str, text: str) -> dict:
    """Replace the result cell of the row holding `url` in that channel's POSTS.md."""
    path = CHANNELS_DIR / channel / "POSTS.md"
    table = post_table(path) if path.is_file() else None
    if not table:
        raise RepoError(f"kênh '{channel}' không có nhật ký")
    header, _, sep, last = table
    col = next(i for i, name in enumerate(header) if name.startswith("Kết quả"))
    lines = path.read_text(encoding="utf-8").splitlines()
    for n in range(sep + 1, last + 1):
        if url in lines[n]:
            cells = (split_row(lines[n]) + [""] * len(header))[:len(header)]
            cells[col] = cell(text)
            lines[n] = "| " + " | ".join(cells) + " |"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return {"file": rel(path), "line": n + 1}
    raise RepoError("không tìm thấy dòng có URL này trong nhật ký")


# --- campaign links ------------------------------------------------------------------------

CT_RE = re.compile(r"^[A-Za-z0-9_.-]{1,40}$")


def read_campaigns() -> dict:
    if not CAMPAIGNS.is_file():
        return {"provider_token": "", "links": []}
    data = json.loads(CAMPAIGNS.read_text(encoding="utf-8"))
    data.setdefault("provider_token", "")
    data.setdefault("links", [])
    for link in data["links"]:
        link["url"] = campaign_url(link.get("app", ""), data["provider_token"], link["ct"], link.get("ppid"))
    return data


def save_campaigns(data: dict) -> None:
    clean = {"_note": "Campaign link App Store của studio. Do tools/dashboard quản lý; pt/ct không phải bí mật "
                      "(nằm trong URL public). Không ghi số liệu vào đây.",
             "provider_token": data.get("provider_token", ""),
             "links": [{k: v for k, v in link.items() if k != "url"} for link in data.get("links", [])]}
    CAMPAIGNS.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def campaign_url(app: str, pt: str, ct: str, ppid: str | None = None) -> str | None:
    app_id = APPS.get(app, {}).get("app_store_id")
    if not app_id:
        return None
    url = f"https://apps.apple.com/app/apple-store/id{app_id}?"
    params = [f"pt={quote(pt)}"] if pt else []
    params.append(f"ct={quote(ct)}")
    if ppid:
        params.append(f"ppid={quote(ppid)}")
    return url + "&".join(params + ["mt=8"])


def suggest_ct(channel: str, lang: str, creative: str = "", variant: str = "") -> str:
    short = next((c["short"] for c in CHANNELS if c["key"] == channel), channel)
    concept = re.sub(r"^\d{4}-\d{2}-\d{2}-|-(en|vi)-v\d+$", "", creative)
    parts = [short, lang.lower()] + ([concept] if concept else []) + ([variant] if variant else [])
    return "_".join(p for p in parts if p)[:40].strip("_")


def add_campaign(data: dict) -> dict:
    store = read_campaigns()
    app = data.get("app", "")
    if not APPS.get(app, {}).get("app_store_id"):
        raise RepoError("app chưa có App Store ID đã xác minh")
    ct = str(data.get("ct", "")).strip()
    if not CT_RE.match(ct):
        raise RepoError("ct chỉ gồm chữ, số, _ . - và tối đa 40 ký tự (giới hạn của App Store Connect)")
    if any(link["ct"] == ct and link["app"] == app for link in store["links"]):
        raise RepoError(f"ct '{ct}' đã tồn tại cho app này")
    ppid = str(data.get("ppid") or "").strip() or None
    if ppid and not re.match(r"^[0-9a-fA-F-]{8,64}$", ppid):
        raise RepoError("ppid (Custom Product Page ID) có dạng UUID")
    link = {"id": secrets.token_hex(4), "app": app, "ct": ct, "channel": data.get("channel") or None,
            "lang": data.get("lang") or None, "creative": data.get("creative") or None,
            "variant": data.get("variant") or None, "ppid": ppid, "cpp_name": data.get("cpp_name") or None,
            "note": str(data.get("note") or "").strip() or None,
            "created": dt.datetime.now(ICT).strftime("%Y-%m-%d")}
    store["links"].append(link)
    save_campaigns(store)
    return link


def delete_campaign(link_id: str) -> None:
    store = read_campaigns()
    before = len(store["links"])
    store["links"] = [l for l in store["links"] if l["id"] != link_id]
    if len(store["links"]) == before:
        raise RepoError("không tìm thấy link")
    save_campaigns(store)


def set_provider_token(pt: str) -> None:
    pt = pt.strip()
    if pt and not re.match(r"^\d{4,20}$", pt):
        raise RepoError("provider token (pt) là dãy số trong App Store Connect → Analytics → Campaigns")
    store = read_campaigns()
    store["provider_token"] = pt
    save_campaigns(store)


# --- whole state -------------------------------------------------------------------------

def load_state(now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(ICT)
    checker = check_content.Checker(ROOT, now).run()
    rough = [creative_state(c, {}) for c in checker.creatives]
    plan, captions = read_plan(rough)
    creatives = [creative_state(c, captions) for c in checker.creatives]
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "apps": APPS,
        "channels": CHANNELS,
        "creatives": creatives,
        "issues": [{"level": i.level, "path": i.path, "message": i.message} for i in checker.issues],
        "plan": plan,
        "accounts": read_accounts(),
        "posts": read_posts(now),
        "uploads": read_uploads(),
        "campaigns": read_campaigns(),
    }
