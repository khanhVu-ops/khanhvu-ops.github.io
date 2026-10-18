#!/usr/bin/env python3
"""Lint creative briefs, YouTube metadata, render configs and channel logs; print the pipeline overview.

    check-content.py [--quiet] [--html media/local/pipeline.html] [--now 2026-10-20T08:00+07:00]

Errors (exit 1) block publishing: missing brief fields, unknown status, Pro features not named in
metadata, wrong App Store link, creative_id/hook mismatches, broken internal Markdown links.
Warnings never fail: posts past 24 h / 7 d whose result column is still empty. The tool only reads;
it never fills in numbers. Standard library only (Python 3.11+).
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ("Idea", "Brief", "Producing", "Review", "Ready", "Published", "Measured", "Archived")
APP_STORE = {"veilnest": "https://apps.apple.com/app/id6813747332"}
ICT = dt.timezone(dt.timedelta(hours=7))
PRO = re.compile(r"\bPro\b")
SHORTS = " #Shorts"
LINK = re.compile(r"\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+[\"'][^)]*[\"'])?\s*\)")
APP_LINK = re.compile(r"https?://apps\.apple\.com/[^\s)\"'`<>\\|]*")


@dataclass
class Issue:
    level: str  # "error" | "warning"
    path: str
    message: str

    def __str__(self):
        return f"{self.path}: {self.message}"


@dataclass
class Creative:
    app: str
    dir: Path
    fields: dict[str, str] = field(default_factory=dict)
    has_brief: bool = False
    pro: bool = False
    hooks: dict[str, str] = field(default_factory=dict)      # variant id → hook text (render.toml)
    metas: dict[str, dict] = field(default_factory=dict)     # variant id → youtube toml
    manifest: dict = field(default_factory=dict)
    master: str | None = None
    plan_days: list[str] = field(default_factory=list)
    slots: list[str] = field(default_factory=list)
    posts: list[str] = field(default_factory=list)
    uploads: list[str] = field(default_factory=list)

    @property
    def id(self):
        return self.dir.name

    @property
    def status(self):
        return status_word(self.fields.get("Trạng thái", "")) if self.has_brief else None


class Checker:
    def __init__(self, root: Path, now: dt.datetime):
        self.root = root
        self.now = now
        self.issues: list[Issue] = []
        self.creatives: list[Creative] = []
        self.files = tracked_files(root)

    def rel(self, path: Path | str) -> str:
        if isinstance(path, str):
            return path
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def error(self, path, message):
        self.issues.append(Issue("error", self.rel(path), message))

    def warn(self, path, message):
        self.issues.append(Issue("warning", self.rel(path), message))

    def run(self):
        required = self.template_fields()
        for app_dir in sorted(p for p in (self.root / "content").glob("*/videos") if p.is_dir()):
            for directory in sorted(p for p in app_dir.iterdir() if p.is_dir()):
                creative = Creative(app=app_dir.parent.name, dir=directory)
                self.creatives.append(creative)
                self.check_brief(creative, required)
                self.check_youtube(creative)
                self.check_render(creative)
                self.check_app_links(creative.app, sorted(directory.rglob("*")))
                self.read_exports(creative)
        for app in APP_STORE:
            self.check_app_links(app, [self.root / "docs/apps" / f"{app}.md"])
        self.check_links()
        self.check_plan()
        self.read_calendar()
        self.check_posts()
        self.read_uploads()
        for creative in self.creatives:
            if creative.status in ("Published", "Measured") and not creative.posts:
                self.error(creative.dir / "BRIEF.md", f"trạng thái {creative.status} nhưng chưa có dòng nào trong "
                           "docs/social/channels/*/POSTS.md có URL public")
        return self

    # --- briefs -------------------------------------------------------------------------------

    def template_fields(self) -> list[str]:
        path = self.root / "docs/templates/VIDEO_BRIEF.md"
        if not path.is_file():
            self.error(path, "thiếu mẫu brief")
            return []
        return list(field_table(path.read_text(encoding="utf-8")))

    def check_brief(self, creative: Creative, required: list[str]):
        path = creative.dir / "BRIEF.md"
        if not path.is_file():
            return  # imported production packs keep their README; they are listed in the overview only
        creative.has_brief = True
        creative.fields = field_table(path.read_text(encoding="utf-8"))
        for name in required:
            if name not in creative.fields:
                self.error(path, f"thiếu trường bắt buộc «{name}»")
            elif not creative.fields[name].strip():
                self.error(path, f"trường «{name}» đang trống")
        listed = creative.fields.get("Creative ID", "").strip("` ")
        if listed and listed != creative.id:
            self.error(path, f"Creative ID «{listed}» khác tên thư mục «{creative.id}»")
        raw = creative.fields.get("Trạng thái", "")
        if raw.strip() and creative.status not in STATUSES:
            self.error(path, f"trạng thái «{raw}» không thuộc {'/'.join(STATUSES)}")
        creative.pro = any(PRO.search(v) for v in creative.fields.values())

    # --- YouTube metadata ---------------------------------------------------------------------

    def check_youtube(self, creative: Creative):
        for path in sorted(creative.dir.glob("youtube-*.toml")):
            variant = path.stem.removeprefix("youtube-")
            data = load_toml(path, self)
            if data is None:
                continue
            creative.metas[variant] = data
            yt = data.get("youtube")
            if not isinstance(yt, dict):
                self.error(path, "thiếu bảng [youtube]")
                continue
            expected = f"{creative.id}-hook{variant}"
            cid = data.get("creative_id") or yt.get("creative_id")
            if cid != expected:
                self.error(path, f"creative_id «{cid}» phải là «{expected}»")
            if "synthetic_media" not in yt:
                self.error(path, "thiếu youtube.synthetic_media (true nếu có cảnh AI/chỉnh sửa giống thật)")
            elif not isinstance(yt["synthetic_media"], bool):
                self.error(path, "youtube.synthetic_media phải là true hoặc false")
            for key in ("title", "description"):
                if not str(yt.get(key, "")).strip():
                    self.error(path, f"thiếu youtube.{key}")
            if creative.pro and not (PRO.search(str(yt.get("title", ""))) or PRO.search(str(yt.get("description", "")))):
                self.error(path, "brief có tính năng Pro nhưng title/description không ghi «Pro»")

    # --- render.toml --------------------------------------------------------------------------

    def check_render(self, creative: Creative):
        path = creative.dir / "render.toml"
        if not path.is_file():
            return
        data = load_toml(path, self)
        if data is None:
            return
        if data.get("creative_id") != creative.id:
            self.error(path, f"creative_id «{data.get('creative_id')}» phải là tên thư mục «{creative.id}»")
        creative.master = data.get("master")
        texts = []
        for variant in data.get("variant", []):
            vid, hook = str(variant.get("id", "")), str(variant.get("hook", ""))
            creative.hooks[vid] = hook
            texts.append(hook)
            meta_name = variant.get("meta")
            if not meta_name:
                continue
            meta_path = creative.dir / meta_name
            if not meta_path.is_file():
                self.error(path, f"hook {vid}: không thấy file meta «{meta_name}»")
                continue
            meta = creative.metas.get(meta_path.stem.removeprefix("youtube-")) or load_toml(meta_path, self) or {}
            title = str(meta.get("youtube", {}).get("title", ""))
            if title.removesuffix(SHORTS).strip() != hook.strip():
                self.error(path, f"hook {vid} «{hook}» khác tiêu đề YouTube «{title}» ({meta_name}, bỏ «{SHORTS.strip()}»)")
        for vid in creative.metas:
            if vid not in creative.hooks:
                self.warn(path, f"youtube-{vid}.toml không có [[variant]] id = \"{vid}\" tương ứng")
        texts += [str(t.get("text", "")) for t in data.get("text", [])]
        texts += [str(v) for v in data.get("end_card", {}).values() if isinstance(v, str)]
        if creative.pro and not any(PRO.search(t) for t in texts):
            self.error(path, "brief có tính năng Pro nhưng hook/text/end card trong video không ghi «Pro»")

    # --- App Store links ----------------------------------------------------------------------

    def check_app_links(self, app: str, paths):
        canonical = APP_STORE.get(app)
        if not canonical:
            return
        for path in paths:
            if path.suffix not in (".md", ".toml", ".txt", ".srt") or not path.is_file() or not self.is_tracked(path):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix == ".toml":
                text = text.replace("\\n", "\n")
            for url in APP_LINK.findall(text):
                url = url.rstrip(".,;:")
                parts = urlsplit(url)
                if not re.search(r"/app/|id\d+", parts.path):
                    continue  # account/subscription pages are not app listings
                if f"{parts.scheme}://{parts.netloc}{parts.path}".rstrip("/") != canonical:
                    self.error(path, f"link App Store «{url}» khác link {app} «{canonical}»")

    # --- exports ------------------------------------------------------------------------------

    def read_exports(self, creative: Creative):
        exports = creative.dir / "exports"
        manifest = exports / "render-manifest.json"
        if manifest.is_file():
            try:
                creative.manifest = json.loads(manifest.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                self.warn(manifest, f"không đọc được manifest: {error}")
        if creative.master:
            creative.master = creative.master if (creative.dir / creative.master).is_file() else None
        else:
            found = sorted(p.name for p in exports.glob("master.*") if p.suffix != ".json") if exports.is_dir() else []
            creative.master = f"exports/{found[0]}" if found else None

    # --- Markdown links -----------------------------------------------------------------------

    def is_tracked(self, path: Path) -> bool:
        return self.files is None or path.resolve() in self.files

    def markdown_files(self):
        for base in ("docs", "content"):
            for path in sorted((self.root / base).rglob("*.md")):
                if self.is_tracked(path):
                    yield path

    def check_links(self):
        anchors: dict[Path, set[str]] = {}
        for path in self.markdown_files():
            text = strip_code(path.read_text(encoding="utf-8"))
            for number, line in enumerate(text.splitlines(), 1):
                for target in LINK.findall(line):
                    target = target.strip("<>")
                    url = urlsplit(target)
                    if url.scheme or url.netloc:
                        continue
                    dest = (path.parent / unquote(url.path)).resolve() if url.path else path.resolve()
                    where = f"{self.rel(path)}:{number}"
                    if not dest.is_relative_to(self.root.resolve()):
                        self.issues.append(Issue("error", where, f"link ra ngoài repo: {target}"))
                        continue
                    if not dest.exists():
                        self.issues.append(Issue("error", where, f"link hỏng: {target}"))
                        continue
                    if url.fragment and dest.suffix == ".md":
                        if dest not in anchors:
                            anchors[dest] = heading_anchors(dest.read_text(encoding="utf-8"))
                        if unquote(url.fragment).lower() not in anchors[dest]:
                            self.issues.append(Issue("error", where, f"không có tiêu đề #{url.fragment}: {target}"))

    # --- plans and logs -----------------------------------------------------------------------

    def find_creative(self, app: str, concept: str, lang: str) -> Creative | None:
        pattern = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(concept)}-{lang}-v\d+$", re.I)
        found = [c for c in self.creatives if c.app == app and pattern.match(c.id)]
        return found[-1] if found else None  # newest version wins

    def check_plan(self):
        path = self.root / "docs/content/VEILNEST_14_DAYS.md"
        if not path.is_file():
            return
        for header, rows in md_tables(path.read_text(encoding="utf-8")):
            col = {name: i for i, name in enumerate(header)}
            if "Video" in col and "Hook" in col and "Ngày" in col:
                for number, row in rows:
                    match = re.search(r"([a-z0-9]+(?:-[a-z0-9]+)+)\s+(EN|VI)\b", row[col["Video"]])
                    if not match:
                        continue
                    creative = self.find_creative("veilnest", match[1], match[2])
                    where = f"{self.rel(path)}:{number}"
                    if not creative:
                        self.issues.append(Issue("error", where, f"không tìm thấy creative cho «{match[0]}»"))
                        continue
                    creative.plan_days.append(row[col["Ngày"]])
                    hook = re.match(r"^([A-Za-z])\s*·\s*(.+)$", row[col["Hook"]])
                    if hook:
                        vid = hook[1].lower()
                        if vid not in creative.hooks:
                            self.issues.append(Issue("error", where, f"{creative.id} không có hook {hook[1]}"))
                        elif hook[2].strip() != creative.hooks[vid].strip():
                            self.issues.append(Issue("error", where, f"hook {hook[1]} «{hook[2]}» khác render.toml "
                                                     f"«{creative.hooks[vid]}» ({creative.id})"))
            elif "Video" in col and any(name.startswith("Caption") for name in header):
                caption_col = next(i for i, name in enumerate(header) if name.startswith("Caption"))
                for number, row in rows:
                    match = re.match(r"^([a-z0-9]+(?:-[a-z0-9]+)+)(?:\s+(EN|VI))?$", row[col["Video"]].strip())
                    if not match:
                        continue
                    creative = self.find_creative("veilnest", match[1], match[2] or "EN")
                    if creative and creative.pro and not PRO.search(row[caption_col]):
                        self.issues.append(Issue("error", f"{self.rel(path)}:{number}",
                                                 f"caption {match[0]} là tính năng Pro nhưng không ghi «Pro»"))

    def read_calendar(self):
        path = self.root / "docs/content/CALENDAR.md"
        if not path.is_file():
            return
        for header, rows in md_tables(path.read_text(encoding="utf-8")):
            if header and header[0] == "Slot":
                for _, row in rows:
                    text = " ".join(row)
                    for creative in self.creatives:
                        if f"/{creative.id}/" in text:
                            creative.slots.append(f"slot {row[0]}")

    def check_posts(self):
        for path in sorted((self.root / "docs/social/channels").glob("*/POSTS.md")):
            channel = path.parent.name
            for header, rows in md_tables(path.read_text(encoding="utf-8")):
                result = next((i for i, name in enumerate(header) if name.startswith("Kết quả")), None)
                if result is None:
                    continue
                for number, row in rows:
                    where = f"{self.rel(path)}:{number}"
                    text = " ".join(row)
                    for creative in self.creatives:
                        if creative.id in text:
                            creative.posts.append(channel)
                    when = parse_when(row[0])
                    if when is None:
                        self.issues.append(Issue("error", where, f"không đọc được ngày giờ «{row[0]}» "
                                                 "(dùng 2026-10-20 08:00 ICT hoặc +07:00)"))
                        continue
                    age = self.now - when
                    cell = row[result].strip()
                    has_24h, has_7d = result_state(cell)
                    if age >= dt.timedelta(days=7) and not has_7d:
                        self.warn(where, f"đã đăng {age.days} ngày, cột kết quả chưa có số 7d")
                    elif age >= dt.timedelta(hours=24) and not has_24h:
                        self.warn(where, f"đã đăng {int(age.total_seconds() // 3600)} giờ, cột kết quả 24h còn trống")

    def read_uploads(self):
        path = self.root / "docs/social/channels/youtube/UPLOADS.md"
        if not path.is_file():
            return
        for header, rows in md_tables(path.read_text(encoding="utf-8")):
            if "Creative ID" not in header:
                continue
            col = header.index("Creative ID")
            privacy = next((i for i, name in enumerate(header) if name.startswith("Privacy")), None)
            for _, row in rows:
                for creative in self.creatives:
                    if row[col].strip("` ").startswith(creative.id):
                        state = row[privacy] if privacy is not None else "?"
                        creative.uploads.append(f"YouTube upload {state}".strip())


# --- parsing helpers --------------------------------------------------------------------------

def tracked_files(root: Path) -> set[Path] | None:
    """Files Git would publish (tracked + untracked, minus ignored). None outside a Git checkout."""
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
                             capture_output=True, check=True).stdout.decode()
    except (OSError, subprocess.CalledProcessError):
        return None
    return {(root / name).resolve() for name in out.split("\0") if name}


def load_toml(path: Path, checker: Checker) -> dict | None:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        checker.error(path, f"TOML lỗi: {error}")
        return None


def split_row(line: str) -> list[str]:
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [cell.strip() for cell in cells]


def md_tables(text: str):
    """Yield (header, [(line_number, cells)]) for each pipe table outside code fences."""
    lines = strip_code(text, inline=False).splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            header = split_row(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = split_row(lines[j])
                rows.append((j + 1, (cells + [""] * len(header))[:len(header)]))
                j += 1
            yield header, rows
            i = j
        else:
            i += 1


def field_table(text: str) -> dict[str, str]:
    for header, rows in md_tables(text):
        if header[:1] == ["Trường"]:
            return {cells[0]: cells[1] for _, cells in rows}
    return {}


def status_word(value: str) -> str:
    match = re.match(r"[\s*`_]*([A-Za-z]+)", value)
    return match[1] if match else value.strip()


def strip_code(text: str, inline: bool = True) -> str:
    """Blank out fenced blocks (and inline code) so example links are not checked; line numbers stay."""
    out, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(```|~~~)", line)
        if fence:
            out.append("")
            if marker and marker[1] == fence:
                fence = None
            continue
        if marker:
            fence = marker[1]
            out.append("")
            continue
        out.append(re.sub(r"`[^`]*`", lambda m: " " * len(m[0]), line) if inline else line)
    return "\n".join(out)


def heading_anchors(text: str) -> set[str]:
    """GitHub-style heading slugs, with -1, -2 … for repeats."""
    seen: dict[str, int] = {}
    anchors = set()
    for line in strip_code(text).splitlines():
        match = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if not match:
            continue
        title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", match[1])
        slug = re.sub(r"[^\w\- ]", "", title.lower().replace("`", "").replace("*", "")).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    for match in re.finditer(r"<a\s+(?:name|id)=\"([^\"]+)\"", text):
        anchors.add(match[1].lower())
    return anchors


def parse_when(cell: str) -> dt.datetime | None:
    """`2026-10-20 08:00 ICT`, `2026-10-20T08:00+07:00`, `20/10/2026 08:00 UTC`; no zone means ICT."""
    cell = cell.strip("`* ")
    iso = re.search(r"(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{1,2}):(\d{2}))?", cell)
    vn = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})(?:\s+(\d{1,2}):(\d{2}))?", cell)
    if iso:
        year, month, day, hour, minute = iso.groups()
    elif vn:
        day, month, year, hour, minute = vn.groups()
    else:
        return None
    zone = ICT
    offset = re.search(r"(?:UTC|GMT)?\s*([+-])(\d{1,2}):?(\d{2})?\s*$", cell)
    if offset:
        sign = 1 if offset[1] == "+" else -1
        zone = dt.timezone(sign * dt.timedelta(hours=int(offset[2]), minutes=int(offset[3] or 0)))
    elif re.search(r"\b(UTC|GMT|Z)\b", cell):
        zone = dt.timezone.utc
    try:
        return dt.datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0), tzinfo=zone)
    except ValueError:
        return None


def result_state(cell: str) -> tuple[bool, bool]:
    """(has 24 h, has 7 d). `chưa có` counts as recorded; a report link counts for both windows."""
    text = re.sub(r"<!--.*?-->", "", cell).strip()
    if not text or text in ("—", "-"):
        return False, False
    if re.search(r"\]\([^)]*\.md[^)]*\)", text):
        return True, True
    parts = [p.strip() for p in re.split(r"\s+/\s+", text.split("·")[0]) if p.strip()]
    has_7d = bool(re.search(r"\b7\s*(d|ngày)\b", text, re.I)) or len(parts) >= 2
    return True, has_7d


# --- overview ---------------------------------------------------------------------------------

def overview_rows(creatives: list[Creative]) -> list[list[str]]:
    rows = []
    for c in creatives:
        status = c.fields.get("Trạng thái", "?") if c.has_brief else "pack nhập (không có BRIEF.md)"
        rendered = sorted(v.get("variant", "?") + (" draft" if v.get("draft") else "")
                          for v in c.manifest.values() if isinstance(v, dict))
        hooks = ", ".join(sorted(c.hooks)) or "—"
        published = sorted(set(c.posts)) + c.uploads
        rows.append([
            c.app, c.id, status + (" · Pro" if c.pro else ""), hooks,
            c.master or "—", ", ".join(rendered) or "—",
            ", ".join(c.slots + [f"ngày {d}" for d in c.plan_days]) or "—",
            ", ".join(published) or "—",
        ])
    return rows


HEADER = ["App", "Creative", "Trạng thái", "Hook", "Master", "Export", "Lịch", "Đã đăng / upload"]


def markdown_overview(checker: Checker) -> str:
    counts: dict[str, int] = {}
    for c in checker.creatives:
        counts[c.status or "pack nhập"] = counts.get(c.status or "pack nhập", 0) + 1
    lines = [f"# Pipeline content — {checker.now:%Y-%m-%d %H:%M %Z}", "",
             " · ".join(f"{k}: {v}" for k, v in counts.items()) or "Chưa có creative.", "",
             "| " + " | ".join(HEADER) + " |", "|" + "---|" * len(HEADER)]
    for row in overview_rows(checker.creatives):
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    lines += ["", "Master/export đọc từ `exports/` trên máy này (đã gitignore); máy khác có thể không có file."]
    return "\n".join(lines)


def html_overview(checker: Checker) -> str:
    e = html.escape
    issues = "".join(f"<li class={i.level}>{e(str(i))}</li>" for i in checker.issues) or "<li>Không có lỗi.</li>"
    head = "".join(f"<th>{e(h)}</th>" for h in HEADER)
    body = "".join("<tr>" + "".join(f"<td>{e(cell)}</td>" for cell in row) + "</tr>"
                   for row in overview_rows(checker.creatives))
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pipeline content</title>
<style>
:root{{--bg:#fff;--fg:#1a1a1a;--line:#ddd;--err:#b3261e;--warn:#8a5a00}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151515;--fg:#eee;--line:#333;--err:#ff8a80;--warn:#ffcc66}}}}
body{{background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,system-ui,sans-serif;margin:24px 16px}}
.scroll{{overflow-x:auto}}table{{border-collapse:collapse;min-width:100%}}
th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
.error{{color:var(--err)}}.warning{{color:var(--warn)}}
</style></head><body>
<h1>Pipeline content</h1><p>{e(f"{checker.now:%Y-%m-%d %H:%M %Z}")} · tạo bởi tools/check-content.py</p>
<h2>Lỗi và cảnh báo</h2><ul>{issues}</ul>
<h2>Creative</h2><div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>
</body></html>
"""


def ignored_by_git(root: Path, path: Path) -> bool:
    result = subprocess.run(["git", "-C", str(root), "check-ignore", "-q", "--no-index", str(path)],
                            capture_output=True)
    return result.returncode == 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--now", help="thời điểm so sánh cho cảnh báo 24h/7d (ISO 8601, mặc định: bây giờ)")
    parser.add_argument("--quiet", action="store_true", help="chỉ in lỗi/cảnh báo, không in tổng quan")
    parser.add_argument("--html", type=Path, help="ghi tổng quan HTML (phải nằm ngoài repo hoặc trong thư mục gitignored)")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    now = dt.datetime.fromisoformat(args.now) if args.now else dt.datetime.now(ICT)
    if now.tzinfo is None:
        now = now.replace(tzinfo=ICT)
    if args.html:
        out = args.html.resolve()
        if out.is_relative_to(root) and not ignored_by_git(root, out):
            print(f"--html {args.html}: file nằm trong repo public mà không bị gitignore. "
                  "Dùng media/local/pipeline.html hoặc đường dẫn ngoài repo.", file=sys.stderr)
            return 2

    checker = Checker(root, now).run()
    errors = [i for i in checker.issues if i.level == "error"]
    warnings = [i for i in checker.issues if i.level == "warning"]
    for issue in errors:
        print(f"LỖI  {issue}", file=sys.stderr)
    for issue in warnings:
        print(f"CẢNH BÁO  {issue}", file=sys.stderr)
    if not args.quiet:
        print(markdown_overview(checker))
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(html_overview(checker), encoding="utf-8")
        print(f"\nĐã ghi {args.html}", file=sys.stderr)
    with_brief = sum(c.has_brief for c in checker.creatives)
    print(f"{'FAIL' if errors else 'OK'}: {len(checker.creatives)} creative ({with_brief} có brief), "
          f"{len(errors)} lỗi, {len(warnings)} cảnh báo.", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
