#!/usr/bin/env python3
"""Read real numbers for KV Apps Shorts from the YouTube Data + Analytics APIs; print JSON.

Run with the YouTube tool's venv (it has the Google libraries); the dashboard calls it as a subprocess:

    tools/youtube/.venv/bin/python tools/dashboard/youtube_sync.py VIDEO_ID [VIDEO_ID…]

Read-only: it never uploads or changes a video. Window labels are honest: a snapshot is called
"24h" only if read 24–36 h after publishing, "7d" only 7–7.5 days after; otherwise "lifetime".
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "youtube"))
import upload  # noqa: E402

ANALYTICS_SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"


def window_for(published: dt.datetime, now: dt.datetime) -> str:
    age = now - published
    if dt.timedelta(hours=24) <= age < dt.timedelta(hours=36):
        return "24h"
    if dt.timedelta(days=7) <= age < dt.timedelta(days=7, hours=12):
        return "7d"
    return "lifetime"


def analytics(creds, video_id: str, start: dt.date, end: dt.date) -> dict:
    from googleapiclient.discovery import build
    service = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
    report = service.reports().query(
        ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(),
        metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,shares,subscribersGained",
        filters=f"video=={video_id}",
    ).execute()
    rows = report.get("rows") or []
    if not rows:
        return {}
    names = [h["name"] for h in report.get("columnHeaders", [])]
    values = dict(zip(names, rows[0]))
    return {
        "watch_time_min": values.get("estimatedMinutesWatched"),
        "avg_view_s": values.get("averageViewDuration"),
        "completion_pct": values.get("averageViewPercentage"),
        "shares": values.get("shares"),
        "followers": values.get("subscribersGained"),
    }


def main(argv: list[str]) -> int:
    ids = [v for v in argv if v]
    try:
        config = upload.Config.from_env(upload.load_env())
        creds = upload.credentials(config)
        service = upload.youtube(creds)
        channel = upload.ensure_channel(service, config.expected_channel)
    except upload.UsageError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1
    now = dt.datetime.now(dt.timezone.utc)
    snapshots, notes = [], []
    has_analytics = ANALYTICS_SCOPE in (getattr(creds, "scopes", None) or [])
    if ids and not has_analytics:
        notes.append("Token chưa có quyền YouTube Analytics: chạy lại `upload.py auth` để lấy thời gian xem và tỷ lệ xem hết.")
    for start in range(0, len(ids), 50):
        batch = ids[start:start + 50]
        items = service.videos().list(part="snippet,statistics,status", id=",".join(batch)).execute().get("items", [])
        found = {item["id"] for item in items}
        notes += [f"Không thấy video {v} trên kênh (đã xoá hoặc sai ID)." for v in batch if v not in found]
        for item in items:
            stats = item.get("statistics", {})
            status = item.get("status", {})
            published = dt.datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00"))
            snap = {
                "video_id": item["id"], "title": item["snippet"]["title"], "privacy": status.get("privacyStatus"),
                "published_at": published.isoformat(), "window": window_for(published, now),
                "captured_at": now.astimezone(dt.timezone(dt.timedelta(hours=7))).isoformat(timespec="minutes"),
                "views": int(stats["viewCount"]) if "viewCount" in stats else None,
                "likes": int(stats["likeCount"]) if "likeCount" in stats else None,
                "comments": int(stats["commentCount"]) if "commentCount" in stats else None,
            }
            if has_analytics and status.get("privacyStatus") == "public":
                try:
                    snap.update({k: v for k, v in analytics(creds, item["id"], published.date(), now.date()).items()
                                 if v is not None})
                except Exception as exc:  # analytics lag a day or two behind; keep the Data API numbers
                    notes.append(f"{item['id']}: YouTube Analytics chưa trả số ({str(exc)[:120]}).")
            snapshots.append(snap)
    print(json.dumps({"channel": channel, "snapshots": snapshots, "notes": notes}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
