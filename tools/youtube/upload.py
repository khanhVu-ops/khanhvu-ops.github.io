#!/usr/bin/env python3
"""Upload a finished Short to the KV Apps YouTube channel with the official Data API v3.

Uploads are private by default. A video only becomes public when the owner asks for it on
the command line (`--privacy public` or `--publish-at`) and confirms at an interactive
prompt; there is no flag that skips that prompt.

    upload.py auth                                   one-time browser sign-in, stores a token
    upload.py channel                                show which channel the token uploads to
    upload.py upload VIDEO --meta META.toml [--dry-run] [--privacy …] [--publish-at …]
    upload.py status VIDEO_ID                        privacy, schedule and processing state
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEDGER = REPO / "docs/social/channels/youtube/UPLOADS.md"
SCOPES = (
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
)
PRIVACY = ("private", "unlisted", "public")
SHORTS_MAX_SECONDS = 180
RETRY_STATUS = {500, 502, 503, 504}


class UsageError(Exception):
    """A problem the owner can fix: bad metadata, missing credentials, wrong channel."""


# --- configuration ---------------------------------------------------------------------

def load_env(path: Path = REPO / ".env") -> dict[str, str]:
    values: dict[str, str] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    values.update({k: v for k, v in os.environ.items() if k.startswith("YOUTUBE_")})
    return values


@dataclass
class Config:
    client_secrets: Path
    token_file: Path
    expected_channel: str | None

    @classmethod
    def from_env(cls, env: dict[str, str]) -> "Config":
        def path(key: str, default: str) -> Path:
            value = Path(env.get(key) or default).expanduser()
            return value if value.is_absolute() else REPO / value
        return cls(
            client_secrets=path("YOUTUBE_CLIENT_SECRETS", ".secrets/youtube-client.json"),
            token_file=path("YOUTUBE_TOKEN_FILE", ".secrets/youtube-token.json"),
            expected_channel=env.get("YOUTUBE_EXPECTED_CHANNEL_ID") or None,
        )


# --- metadata --------------------------------------------------------------------------

@dataclass
class Meta:
    creative_id: str
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    category_id: str = "28"
    language: str = "en"
    made_for_kids: bool = False
    synthetic_media: bool = False
    privacy: str = "private"
    publish_at: str | None = None

    @classmethod
    def load(cls, path: Path) -> "Meta":
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as error:
            raise UsageError(f"{path}: {error}") from error
        yt = data.get("youtube", {})
        missing = [key for key in ("creative_id", "title", "description")
                   if not (data.get(key) or yt.get(key))]
        if missing:
            raise UsageError(f"{path}: missing {', '.join(missing)}")
        if "synthetic_media" not in yt:
            raise UsageError(f"{path}: set youtube.synthetic_media to true or false; "
                             "YouTube asks whether realistic content is altered or AI-generated")
        return cls(
            creative_id=data.get("creative_id") or yt["creative_id"],
            title=yt.get("title", data.get("title", "")).strip(),
            description=yt.get("description", data.get("description", "")).strip(),
            tags=list(yt.get("tags", [])),
            category_id=str(yt.get("category_id", "28")),
            language=yt.get("language", "en"),
            made_for_kids=bool(yt.get("made_for_kids", False)),
            synthetic_media=bool(yt["synthetic_media"]),
            privacy=yt.get("privacy", "private"),
            publish_at=yt.get("publish_at"),
        )


def parse_publish_at(value: str, now: dt.datetime | None = None) -> str:
    try:
        moment = dt.datetime.fromisoformat(value)
    except ValueError as error:
        raise UsageError(f"--publish-at must be ISO 8601 with a timezone, "
                         f"e.g. 2026-10-20T19:00:00+07:00 (got {value!r})") from error
    if moment.tzinfo is None:
        raise UsageError("--publish-at needs a timezone offset, e.g. +07:00 for Vietnam")
    now = now or dt.datetime.now(dt.timezone.utc)
    if moment <= now + dt.timedelta(minutes=15):
        raise UsageError("--publish-at must be at least 15 minutes in the future; "
                         "a past time would publish immediately")
    return moment.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate(meta: Meta) -> list[str]:
    problems = []
    if meta.privacy not in PRIVACY:
        problems.append(f"privacy must be one of {', '.join(PRIVACY)}")
    if meta.publish_at and meta.privacy != "private":
        problems.append("a scheduled video must upload as private; YouTube makes it public at publish_at")
    if not 1 <= len(meta.title) <= 100:
        problems.append(f"title must be 1–100 characters (has {len(meta.title)})")
    if len(meta.description.encode("utf-8")) > 5000:
        problems.append("description is over 5000 bytes")
    for name, text in (("title", meta.title), ("description", meta.description)):
        if "<" in text or ">" in text:
            problems.append(f"{name} may not contain < or >")
    if sum(len(tag) + (2 if " " in tag else 0) for tag in meta.tags) + max(len(meta.tags) - 1, 0) > 500:
        problems.append("tags are over YouTube's 500-character total")
    return problems


def probe(video: Path) -> dict:
    """Width, height and duration via ffprobe; None values when ffprobe is unavailable."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height:format=duration", "-of", "json", str(video)],
            check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {"width": None, "height": None, "duration": None}
    data = json.loads(out)
    stream = (data.get("streams") or [{}])[0]
    duration = data.get("format", {}).get("duration")
    return {"width": stream.get("width"), "height": stream.get("height"),
            "duration": float(duration) if duration else None}


def check_short(info: dict) -> list[str]:
    problems = []
    if info["width"] and info["height"] and info["width"] > info["height"]:
        problems.append(f"video is landscape ({info['width']}×{info['height']}); Shorts need square or vertical")
    if info["duration"] and info["duration"] > SHORTS_MAX_SECONDS:
        problems.append(f"video is {info['duration']:.0f}s; Shorts are at most {SHORTS_MAX_SECONDS}s")
    return problems


def request_body(meta: Meta) -> dict:
    status = {
        "privacyStatus": meta.privacy,
        "selfDeclaredMadeForKids": meta.made_for_kids,
        "containsSyntheticMedia": meta.synthetic_media,
        "embeddable": True,
    }
    if meta.publish_at:
        status["publishAt"] = meta.publish_at
    return {
        "snippet": {
            "title": meta.title,
            "description": meta.description,
            "tags": meta.tags,
            "categoryId": meta.category_id,
            "defaultLanguage": meta.language,
            "defaultAudioLanguage": meta.language,
        },
        "status": status,
    }


# --- Google API ------------------------------------------------------------------------

def credentials(config: Config, interactive: bool = False):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = None
    if config.token_file.is_file():
        creds = Credentials.from_authorized_user_file(str(config.token_file), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_token(config, creds)
            return creds
        except Exception as error:  # refresh tokens of a "Testing" consent screen expire after 7 days
            if not interactive:
                raise UsageError(f"stored token could not be refreshed ({error}); run `upload.py auth` again")
    if not interactive:
        raise UsageError("no YouTube token yet; run `upload.py auth` first")
    if not config.client_secrets.is_file():
        raise UsageError(f"OAuth client file not found: {config.client_secrets}. "
                         "Download the Desktop OAuth client JSON there (see tools/youtube/README.md)")
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(config.client_secrets), SCOPES)
    creds = flow.run_local_server(host="127.0.0.1", port=0, open_browser=True)
    save_token(config, creds)
    return creds


def save_token(config: Config, creds) -> None:
    config.token_file.parent.mkdir(parents=True, exist_ok=True)
    config.token_file.write_text(creds.to_json(), encoding="utf-8")
    config.token_file.chmod(0o600)


def youtube(creds=None, http=None):
    from googleapiclient.discovery import build
    if http is not None:
        return build("youtube", "v3", http=http, static_discovery=True, cache_discovery=False)
    return build("youtube", "v3", credentials=creds, static_discovery=True, cache_discovery=False)


def my_channel(service) -> dict:
    items = service.channels().list(part="snippet", mine=True).execute().get("items", [])
    if not items:
        raise UsageError("this Google account has no YouTube channel")
    return {"id": items[0]["id"], "title": items[0]["snippet"]["title"]}


def ensure_channel(service, expected: str | None) -> dict:
    channel = my_channel(service)
    if expected and channel["id"] != expected:
        raise UsageError(f"token belongs to {channel['title']} ({channel['id']}), not "
                         f"YOUTUBE_EXPECTED_CHANNEL_ID={expected}; run `upload.py auth` with the studio account")
    return channel


def upload_video(service, video: Path, body: dict, chunk_mb: int = 8, sleep=time.sleep, log=print) -> dict:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(video), chunksize=chunk_mb * 1024 * 1024, resumable=True,
                            mimetype="video/*")
    request = service.videos().insert(part="snippet,status", body=body, media_body=media,
                                      notifySubscribers=True)
    response, attempt = None, 0
    while response is None:
        try:
            progress, response = request.next_chunk()
            if progress:
                log(f"  uploaded {progress.progress() * 100:.0f}%")
        except HttpError as error:
            if error.resp.status not in RETRY_STATUS or attempt >= 5:
                raise
            attempt += 1
            wait = 2 ** attempt
            log(f"  YouTube returned {error.resp.status}; retrying in {wait}s ({attempt}/5)")
            sleep(wait)
    return response


# --- ledger ----------------------------------------------------------------------------

def append_ledger(meta: Meta, video: Path, response: dict, channel: dict, ledger: Path | None = None) -> None:
    ledger = ledger or LEDGER
    status = response.get("status", {})
    when = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")
    scheduled = status.get("publishAt", "—")
    try:
        export = video.resolve().relative_to(REPO).as_posix()
    except ValueError:
        export = video.name
    row = (f"| {when} | {meta.creative_id} | `{export}` | {response['id']} "
           f"| https://youtu.be/{response['id']} | {status.get('privacyStatus', meta.privacy)} "
           f"| {scheduled} | {channel['title']} |\n")
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(row)


# --- commands --------------------------------------------------------------------------

def confirm_publication(meta: Meta, channel: dict, ask=input) -> None:
    when = f"at {meta.publish_at} (UTC)" if meta.publish_at else "IMMEDIATELY"
    print(f"\nThis video will become PUBLIC {when} on {channel['title']} ({channel['id']}):")
    print(f"  {meta.title}")
    answer = ask("Type 'publish' to continue, anything else to cancel: ")
    if answer.strip() != "publish":
        raise UsageError("cancelled; nothing was uploaded")


def cmd_upload(args, config: Config, service_factory=None, ask=input) -> int:
    video = Path(args.video).expanduser().resolve()
    if not video.is_file():
        raise UsageError(f"video not found: {video}")
    meta = Meta.load(Path(args.meta).expanduser())
    if args.privacy:
        meta.privacy = args.privacy
    if args.publish_at:
        meta.publish_at = args.publish_at
        if not args.privacy:
            meta.privacy = "private"
    if meta.publish_at:
        meta.publish_at = parse_publish_at(meta.publish_at)

    problems = validate(meta) + check_short(probe(video))
    if problems:
        raise UsageError("cannot upload:\n  - " + "\n  - ".join(problems))
    body = request_body(meta)
    print(f"Creative {meta.creative_id} · {video.name} · {video.stat().st_size / 1e6:.1f} MB")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    if args.dry_run:
        print("\nDry run: metadata and file are valid; nothing was sent to YouTube.")
        return 0

    service = service_factory() if service_factory else youtube(credentials(config))
    channel = ensure_channel(service, config.expected_channel)
    if meta.privacy == "public" or meta.publish_at:
        confirm_publication(meta, channel, ask=ask)
    print(f"\nUploading to {channel['title']} ({channel['id']}) as {meta.privacy} …")
    response = upload_video(service, video, body)
    print(f"Done: https://youtu.be/{response['id']} · Studio: "
          f"https://studio.youtube.com/video/{response['id']}/edit")
    if not args.no_ledger:
        append_ledger(meta, video, response, channel)
        print(f"Recorded in {LEDGER.relative_to(REPO)}. After it is public, log it in POSTS.md.")
    return 0


def cmd_status(args, config: Config, service_factory=None) -> int:
    service = service_factory() if service_factory else youtube(credentials(config))
    items = service.videos().list(part="status,processingDetails,snippet", id=args.video_id).execute()["items"]
    if not items:
        raise UsageError(f"no video {args.video_id} visible to this account")
    item = items[0]
    print(json.dumps({"title": item["snippet"]["title"], "status": item["status"],
                      "processing": item.get("processingDetails", {})}, indent=2, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("auth", help="sign in with the studio Google account and store a token")
    sub.add_parser("channel", help="show the channel the stored token uploads to")
    up = sub.add_parser("upload", help="upload one finished export")
    up.add_argument("video")
    up.add_argument("--meta", required=True, help="TOML with creative_id and a [youtube] table")
    up.add_argument("--privacy", choices=PRIVACY, help="override the TOML; default private")
    up.add_argument("--publish-at", help="schedule, ISO 8601 with offset, e.g. 2026-10-20T19:00:00+07:00")
    up.add_argument("--dry-run", action="store_true", help="validate only, no network")
    up.add_argument("--no-ledger", action="store_true", help="do not append to UPLOADS.md")
    st = sub.add_parser("status", help="show privacy, schedule and processing of a video")
    st.add_argument("video_id")
    args = parser.parse_args(argv)
    config = Config.from_env(load_env())
    try:
        if args.command == "auth":
            service = youtube(credentials(config, interactive=True))
            channel = ensure_channel(service, config.expected_channel)
            print(f"Signed in. Uploads go to {channel['title']} ({channel['id']}).")
            return 0
        if args.command == "channel":
            channel = ensure_channel(youtube(credentials(config)), config.expected_channel)
            print(f"{channel['title']} ({channel['id']})")
            return 0
        if args.command == "upload":
            return cmd_upload(args, config)
        return cmd_status(args, config)
    except UsageError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
