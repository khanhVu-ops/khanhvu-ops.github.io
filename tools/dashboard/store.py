"""Local SQLite store for metric snapshots. Lives in /.dashboard/ (gitignored): analytics stay private.

Only real numbers go in: every snapshot names its source and when it was read. Missing values stay NULL,
never 0, matching the repo rule that unknown metrics are "chưa có".
"""

from __future__ import annotations

import datetime as dt
import contextlib
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / ".dashboard/dashboard.db"
ICT = dt.timezone(dt.timedelta(hours=7))

METRICS = {
    # key: (label, kind) — kind drives validation and formatting in the UI
    "views": ("View", "int"),
    "likes": ("Like", "int"),
    "comments": ("Bình luận", "int"),
    "shares": ("Chia sẻ", "int"),
    "saves": ("Lưu", "int"),
    "avg_view_s": ("Xem trung bình (giây)", "float"),
    "completion_pct": ("Tỷ lệ xem hết (%)", "float"),
    "watch_time_min": ("Tổng thời gian xem (phút)", "float"),
    "profile_visits": ("Lượt vào profile", "int"),
    "followers": ("Follower mới", "int"),
    "link_clicks": ("Click link", "int"),
    "installs": ("Lượt tải (App Store)", "int"),
}
WINDOWS = ("24h", "7d", "28d", "lifetime")

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT NOT NULL,
    url TEXT NOT NULL,
    creative_id TEXT,
    variant TEXT,
    captured_at TEXT NOT NULL,
    window TEXT NOT NULL,
    source TEXT NOT NULL,
    note TEXT,
    {", ".join(f"{k} REAL" for k in METRICS)}
);
CREATE INDEX IF NOT EXISTS snapshots_url ON snapshots(url, captured_at);
-- App Store listing: the last state both sides agreed on, per field. `local_hash` and `remote_hash` are
-- hashes of the normalized text (or screenshot checksums). Lets the page tell "local changed since the last
-- push" apart from "someone edited App Store Connect by hand", so nothing is pushed twice or overwritten blind.
CREATE TABLE IF NOT EXISTS asc_sync (
    app TEXT NOT NULL,
    locale TEXT NOT NULL,
    field TEXT NOT NULL,
    local_hash TEXT NOT NULL,
    remote_hash TEXT NOT NULL,
    how TEXT NOT NULL,          -- pushed | accepted | matched
    at TEXT NOT NULL,
    PRIMARY KEY (app, locale, field)
);
"""


class StoreError(Exception):
    pass


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    gitignore = path.parent / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")  # belt and braces on top of the repo .gitignore
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


@contextlib.contextmanager
def session(path: Path | None = None):
    """Open, yield, commit/close — one connection per request."""
    conn = connect(path or DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def add_snapshot(conn: sqlite3.Connection, data: dict) -> dict:
    channel = str(data.get("channel", "")).strip()
    url = str(data.get("url", "")).strip()
    if not channel or not url.startswith("https://"):
        raise StoreError("cần kênh và URL bài đăng")
    window = data.get("window", "24h")
    if window not in WINDOWS:
        raise StoreError(f"khoảng đo phải là {', '.join(WINDOWS)}")
    source = str(data.get("source", "")).strip()
    if not source:
        raise StoreError("ghi nguồn số liệu (ví dụ TikTok Studio, YouTube Studio)")
    values = {}
    for key, (label, kind) in METRICS.items():
        raw = data.get(key)
        if raw in (None, ""):
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            raise StoreError(f"«{label}» phải là số") from None
        if value < 0 or (key == "completion_pct" and value > 100):
            raise StoreError(f"«{label}» ngoài khoảng hợp lệ")
        values[key] = int(value) if kind == "int" else value
    if not values:
        raise StoreError("nhập ít nhất một chỉ số")
    captured = data.get("captured_at") or dt.datetime.now(ICT).isoformat(timespec="minutes")
    row = {"channel": channel, "url": url, "creative_id": data.get("creative_id") or None,
           "variant": data.get("variant") or None, "captured_at": captured, "window": window,
           "source": source, "note": (str(data.get("note") or "").strip() or None), **values}
    cols = ", ".join(row)
    conn.execute(f"INSERT INTO snapshots ({cols}) VALUES ({', '.join('?' for _ in row)})", list(row.values()))
    conn.commit()
    return row


def snapshots(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM snapshots ORDER BY captured_at, id").fetchall()
    return [{k: r[k] for k in r.keys() if r[k] is not None} for r in rows]


def delete_snapshot(conn: sqlite3.Connection, snapshot_id: int) -> None:
    if not conn.execute("DELETE FROM snapshots WHERE id = ?", (snapshot_id,)).rowcount:
        raise StoreError("không tìm thấy bản ghi")
    conn.commit()


def compact(n: float) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}k".replace(".0k", "k")
    return f"{int(n)}"


def result_text(conn: sqlite3.Connection, url: str) -> str:
    """Summary for the POSTS.md result column, in the format check-content.py reads:
    `24h 1.2k view, 63% xem hết / 7d 5.4k view · nguồn …`."""
    parts, sources = [], []
    for window in ("24h", "7d"):
        row = conn.execute("SELECT * FROM snapshots WHERE url = ? AND window = ? ORDER BY captured_at DESC, id DESC "
                           "LIMIT 1", (url, window)).fetchone()
        if not row:
            continue
        bits = []
        if row["views"] is not None:
            bits.append(f"{compact(row['views'])} view")
        if row["completion_pct"] is not None:
            bits.append(f"{row['completion_pct']:.0f}% xem hết")
        elif row["avg_view_s"] is not None:
            bits.append(f"xem TB {row['avg_view_s']:.1f}s")
        if row["installs"] is not None:
            bits.append(f"{int(row['installs'])} tải")
        parts.append(f"{window} " + ", ".join(bits or ["đã đo"]))
        sources.append(f"{row['source']} {row['captured_at'][:10]}")
    if not parts:
        raise StoreError("chưa có số 24h hoặc 7d cho bài này")
    return " / ".join(parts) + " · " + "; ".join(dict.fromkeys(sources))


def sync_marks(conn: sqlite3.Connection, app: str) -> dict[tuple[str, str], dict]:
    rows = conn.execute("SELECT locale, field, local_hash, remote_hash, how, at FROM asc_sync WHERE app = ?", (app,))
    return {(r[0], r[1]): {"local_hash": r[2], "remote_hash": r[3], "how": r[4], "at": r[5]} for r in rows}


def set_sync_mark(conn: sqlite3.Connection, app: str, locale: str, field: str, local_hash: str, remote_hash: str,
                  how: str) -> None:
    conn.execute("INSERT OR REPLACE INTO asc_sync VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (app, locale, field, local_hash, remote_hash, how, dt.datetime.now(ICT).isoformat(timespec="seconds")))
