#!/usr/bin/env python3
"""Render hook variants of one clean master into platform-ready vertical videos.

One filmed master + `render.toml` in the creative folder → per hook variant: a 1080×1920
H.264/AAC MP4 with burned-in hook, text and subtitles, loudness-normalised audio, a cover
frame, a review sheet with TikTok/Reels/Shorts safe zones, and a manifest entry. Text is
drawn with Pillow and checked against every platform's UI before ffmpeg runs.

    render.py init DIR [--force]              write render.toml from BRIEF.md hook table
    render.py check DIR...                    validate config + layout, write layout sheet
    render.py render DIR... [--variant a] [--draft] [--preview] [--force]
    render.py safezones [--out DIR]           PNG overlays for editing apps (CapCut, …)

DIR is a creative folder such as content/veilnest/videos/2026-10-18-decoy-pin-en-v1.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

try:
    from PIL import Image
    import layout
    from layout import H, W, Layer, LayoutError, SafeZone
except ModuleNotFoundError as exc:  # pragma: no cover - depends on the venv
    sys.exit(f"Thiếu {exc.name}. Chạy bằng tools/render/.venv/bin/python (xem tools/render/README.md).")

REPO = Path(__file__).resolve().parents[2]
TOOL_VERSION = "1.0"
CONFIG_NAME = "render.toml"
TRUE_PEAK = -1.5      # dBTP; headroom for AAC re-encoding by the platforms
LRA = 11
MAX_SIDE_LAYERS = 60  # ffmpeg inputs; a 15–60s short never needs more


class UsageError(Exception):
    """Something the owner can fix: config, missing master, HDR footage, unsafe text."""


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path)


# --- config ----------------------------------------------------------------------------

@dataclass
class Variant:
    id: str
    hook: str
    meta: str | None = None
    cover_at: float | None = None


@dataclass
class TextSpec:
    text: str
    start: float
    end: float
    style: str = "caption"
    position: str | float = "lower"


@dataclass
class ImageSpec:
    file: str
    start: float
    end: float
    width: int = 300
    position: str | float = "center"


@dataclass
class EndCard:
    start: float
    title: str
    end: float | None = None
    subtitle: str = ""
    cta: str = ""
    icon: str | None = None
    background: str = "#0b0b10"


@dataclass
class Config:
    dir: Path
    creative_id: str
    variants: list[Variant]
    master: str | None = None
    trim: tuple[float, float] | None = None
    fit: str = "auto"
    fps: int | None = None
    loudness: float | None = -14.0
    platforms: list[str] = field(default_factory=lambda: ["tiktok", "reels", "shorts"])
    hook_duration: float = 2.0
    hook_position: str | float = "upper"
    hook_style: str = "hook"
    captions_file: str | None = None
    captions_style: str = "caption"
    captions_position: str | float = "lower"
    texts: list[TextSpec] = field(default_factory=list)
    images: list[ImageSpec] = field(default_factory=list)
    end_card: EndCard | None = None
    styles: dict[str, dict] = field(default_factory=dict)

    @property
    def exports(self) -> Path:
        return self.dir / "exports"

    def output(self, variant: Variant, draft: bool = False) -> Path:
        suffix = "-draft" if draft else ""
        return self.exports / f"{self.creative_id}-hook{variant.id}{suffix}.mp4"

    @classmethod
    def load(cls, directory: Path) -> "Config":
        path = directory / CONFIG_NAME
        if not path.is_file():
            raise UsageError(f"{rel(path)} chưa có. Tạo bằng: render.py init {rel(directory)}")
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            raise UsageError(f"{rel(path)}: TOML lỗi — {exc}") from exc
        return cls.parse(directory, data)

    @classmethod
    def parse(cls, directory: Path, data: dict) -> "Config":
        errors: list[str] = []

        def num(table: dict, key: str, where: str, default=None):
            value = table.get(key, default)
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
                errors.append(f"{where}.{key} phải là số")
                return default
            return value

        def timed(table: dict, where: str) -> tuple[float, float]:
            start, end = num(table, "start", where), num(table, "end", where)
            if start is None or end is None:
                errors.append(f"{where} cần start và end (giây)")
                return 0.0, 0.0
            if not 0 <= start < end:
                errors.append(f"{where}: cần 0 ≤ start < end (đang {start}–{end})")
            return float(start), float(end)

        creative_id = data.get("creative_id") or ""
        if not creative_id:
            errors.append("thiếu creative_id")
        elif creative_id != directory.name:
            errors.append(f"creative_id '{creative_id}' khác tên thư mục '{directory.name}'")

        variants = []
        for i, v in enumerate(data.get("variant", []), 1):
            vid = str(v.get("id", "")).lower()
            if not re.fullmatch(r"[a-z0-9]{1,8}", vid):
                errors.append(f"variant {i}: id phải là chữ thường/số, ví dụ 'a'")
            if not str(v.get("hook", "")).strip():
                errors.append(f"variant {vid or i}: thiếu hook")
            variants.append(Variant(vid, str(v.get("hook", "")), v.get("meta"), num(v, "cover_at", f"variant {vid}")))
        if not variants:
            errors.append("cần ít nhất một [[variant]] có id và hook")
        dupes = {v.id for v in variants if [x.id for x in variants].count(v.id) > 1}
        if dupes:
            errors.append(f"id biến thể trùng: {', '.join(sorted(dupes))}")

        hook = data.get("hook", {})
        captions = data.get("captions", {})
        if isinstance(captions, str):
            captions = {"file": captions}

        texts = []
        for i, t in enumerate(data.get("text", []), 1):
            start, end = timed(t, f"text {i}")
            texts.append(TextSpec(str(t.get("text", "")), start, end, t.get("style", "caption"),
                                  t.get("position", "lower")))
            if not texts[-1].text.strip():
                errors.append(f"text {i}: thiếu nội dung")
        images = []
        for i, m in enumerate(data.get("image", []), 1):
            start, end = timed(m, f"image {i}")
            if not m.get("file"):
                errors.append(f"image {i}: thiếu file")
            images.append(ImageSpec(m.get("file", ""), start, end, int(m.get("width", 300)),
                                    m.get("position", "center")))
        end_card = None
        if "end_card" in data:
            e = data["end_card"]
            if num(e, "start", "end_card") is None or not e.get("title"):
                errors.append("end_card cần start và title")
            else:
                end_card = EndCard(float(e["start"]), e["title"], num(e, "end", "end_card"), e.get("subtitle", ""),
                                   e.get("cta", ""), e.get("icon"), e.get("background", "#0b0b10"))

        trim = data.get("trim")
        if trim is not None and (len(trim) != 2 or not 0 <= trim[0] < trim[1]):
            errors.append("trim phải là [start, end] với 0 ≤ start < end")
        fit = data.get("fit", "auto")
        if fit not in ("auto", "scale", "crop", "pad", "blur"):
            errors.append("fit phải là auto, scale, crop, pad hoặc blur")
        loudness = data.get("loudness", -14.0)
        if loudness is False:
            loudness = None
        elif isinstance(loudness, bool) or not isinstance(loudness, (int, float)) or not -30 <= loudness <= -5:
            errors.append("loudness là LUFS từ -30 đến -5, hoặc false để giữ nguyên")
        fps = num(data, "fps", "config")
        if fps is not None and fps not in (24, 25, 30, 50, 60):
            errors.append("fps chỉ nhận 24, 25, 30, 50 hoặc 60")
        platforms = data.get("platforms", ["tiktok", "reels", "shorts"])
        known = layout.load_safezones()
        unknown = [p for p in platforms if p not in known]
        if unknown or not platforms:
            errors.append(f"platforms lạ: {', '.join(unknown) or '(rỗng)'}; có {', '.join(known)}")

        if errors:
            raise UsageError(f"{rel(directory / CONFIG_NAME)}:\n  - " + "\n  - ".join(errors))
        return cls(
            dir=directory, creative_id=creative_id, variants=variants, master=data.get("master"),
            trim=tuple(trim) if trim else None, fit=fit, fps=fps, loudness=loudness, platforms=platforms,
            hook_duration=float(hook.get("duration", 2.0)), hook_position=hook.get("position", "upper"),
            hook_style=hook.get("style", "hook"), captions_file=captions.get("file"),
            captions_style=captions.get("style", "caption"), captions_position=captions.get("position", "lower"),
            texts=texts, images=images, end_card=end_card, styles=resolve_fonts(directory, data.get("styles", {})),
        )

    def zones(self) -> list[SafeZone]:
        known = layout.load_safezones()
        return [known[p] for p in self.platforms]

    def resolve_master(self) -> Path | None:
        if self.master:
            path = (self.dir / self.master).resolve()
            return path if path.is_file() else None
        found = sorted(p for p in glob.glob(str(self.exports / "master.*")) if not p.endswith(".json"))
        if len(found) > 1:
            raise UsageError(f"có nhiều master trong {rel(self.exports)}: {', '.join(Path(p).name for p in found)}. "
                             f"Ghi rõ master = \"exports/…\" trong {CONFIG_NAME}.")
        return Path(found[0]) if found else None


def resolve_fonts(directory: Path, styles: dict[str, dict]) -> dict[str, dict]:
    """Font paths in render.toml are relative to the creative folder, like every other path there."""
    out = {}
    for name, values in styles.items():
        values = dict(values)
        if "font" in values:
            font = Path(values["font"]).expanduser()
            values["font"] = str(font if font.is_absolute() else (directory / font).resolve())
        out[name] = values
    return out


# --- subtitles -------------------------------------------------------------------------

@dataclass
class Cue:
    start: float
    end: float
    text: str


def parse_time(stamp: str) -> float:
    m = re.fullmatch(r"(\d+):(\d{2}):(\d{2})[,.](\d{1,3})", stamp.strip())
    if not m:
        raise ValueError(stamp)
    h, mnt, s, ms = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000


def parse_srt(text: str) -> list[Cue]:
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        if lines and lines[0].strip().isdigit():
            lines = lines[1:]
        if not lines or "-->" not in lines[0]:
            continue
        a, b = lines[0].split("-->")
        try:
            start, end = parse_time(a), parse_time(b.split()[0])
        except ValueError as exc:
            raise UsageError(f"SRT: mốc thời gian lỗi '{exc}'") from None
        body = "\n".join(re.sub(r"</?[a-zA-Z][^>]*>", "", l).strip() for l in lines[1:]).strip()
        if body and end > start:
            cues.append(Cue(start, end, body))
    return cues


# --- brief → config ---------------------------------------------------------------------

def hooks_from_brief(text: str) -> list[tuple[str, str, str | None]]:
    """Rows of the 'Biến thể hook' table: (id, hook, meta file). Falls back to the 'Hook 0–2s' field."""
    rows = []
    section = re.search(r"^## Biến thể hook\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if section:
        for line in section.group(1).splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and re.fullmatch(r"[A-Za-z0-9]{1,8}", cells[0]) and cells[0].lower() != "biến":
                meta = re.search(r"youtube-[\w-]+\.toml", cells[2]) if len(cells) > 2 else None
                rows.append((cells[0].lower(), cells[1], meta.group(0) if meta else None))
    if not rows:
        field_ = re.search(r"^\|\s*Hook 0–2s\s*\|\s*(.+?)\s*\|", text, re.M)
        if field_ and field_.group(1) and "bảng" not in field_.group(1):
            rows.append(("a", field_.group(1), None))
    return rows


def init_config(directory: Path) -> str:
    brief = directory / "BRIEF.md"
    if not brief.is_file():
        raise UsageError(f"{rel(directory)} chưa có BRIEF.md")
    hooks = hooks_from_brief(brief.read_text(encoding="utf-8"))
    if not hooks:
        raise UsageError("không đọc được hook từ BRIEF.md (bảng 'Biến thể hook' hoặc trường 'Hook 0–2s')")
    lang = "vi" if "-vi-" in directory.name else "en"
    cta = 'Tìm “Veilnest” trên App Store' if lang == "vi" else "Search “Veilnest” on the App Store"
    out = [
        f"# Cấu hình render cho {directory.name}. Xem tools/render/README.md.",
        "# Thời gian theo kịch bản trong BRIEF.md — chỉnh lại theo footage thật sau khi quay.",
        f'creative_id = "{directory.name}"',
        '# master = "exports/master.mov"   # mặc định: exports/master.* (thư mục đã gitignore)',
        "# trim = [0.0, 15.0]               # cắt master trước khi dựng, giây",
        'fit = "auto"                       # auto | scale | crop | pad | blur (nền mờ khi khác 9:16)',
        "loudness = -14.0                   # LUFS; false để giữ nguyên âm lượng",
        'platforms = ["tiktok", "reels", "shorts"]',
        "",
        "[hook]",
        "duration = 2.0",
        'position = "upper"                 # top | upper | center | lower | bottom | số 0–1',
        'style = "hook"',
        "",
        "# [captions]",
        '# file = "captions.srt"',
        '# style = "caption"',
        '# position = "lower"',
        "",
    ]
    for vid, hook, meta in hooks:
        out += ["[[variant]]", f'id = "{vid}"', f"hook = {json.dumps(hook, ensure_ascii=False)}"]
        if meta:
            out.append(f'meta = "{meta}"')
        out.append("")
    out += [
        "# [[text]]",
        '# text = "…"',
        "# start = 10.0",
        "# end = 13.0",
        '# style = "label"                 # hook | caption | label | outline | cta',
        '# position = "lower"',
        "",
        "# [end_card]",
        "# start = 13.0",
        '# title = "Veilnest"',
        f"# cta = {json.dumps(cta, ensure_ascii=False)}",
        '# icon = "../veilnest-us-pov-v2-2026-10-04/assets/veilnest-icon.png"',
    ]
    return "\n".join(out) + "\n"


# --- probing ---------------------------------------------------------------------------

@dataclass
class MasterInfo:
    path: Path
    width: int
    height: int
    fps: float
    duration: float
    has_audio: bool
    codec: str
    transfer: str | None = None

    @property
    def hdr(self) -> bool:
        return self.transfer in ("arib-std-b67", "smpte2084")

    def describe(self) -> str:
        audio = "có tiếng" if self.has_audio else "không có tiếng"
        hdr = " · HDR" if self.hdr else ""
        return f"{self.width}×{self.height} {self.fps:g}fps {self.duration:.2f}s {self.codec} · {audio}{hdr}"


def need(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise UsageError(f"cần {tool} (brew install ffmpeg)")
    return path


def ratio(value: str | None) -> float:
    if not value or value in ("0/0", "N/A"):
        return 0.0
    num, _, den = value.partition("/")
    return float(num) / float(den or 1) if float(den or 1) else 0.0


def probe(path: Path) -> dict:
    result = subprocess.run(
        [need("ffprobe"), "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise UsageError(f"ffprobe không đọc được {rel(path)}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def master_info(path: Path, data: dict | None = None) -> MasterInfo:
    data = data or probe(path)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video:
        raise UsageError(f"{rel(path)} không có luồng video")
    width, height = int(video["width"]), int(video["height"])
    rotation = 0
    for side in video.get("side_data_list", []):
        rotation = int(side.get("rotation", rotation) or 0)
    rotation = int(video.get("tags", {}).get("rotate", rotation) or 0)
    if abs(rotation) % 180 == 90:  # ffmpeg auto-rotates, so the frame we work with is swapped
        width, height = height, width
    fps = ratio(video.get("avg_frame_rate")) or ratio(video.get("r_frame_rate"))
    duration = float(data.get("format", {}).get("duration") or video.get("duration") or 0)
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
    return MasterInfo(path, width, height, fps, duration, has_audio, video.get("codec_name", "?"),
                      video.get("color_transfer"))


def output_fps(config: Config, info: MasterInfo | None) -> int:
    if config.fps:
        return config.fps
    if not info or not info.fps:
        return 30
    # Screen recordings are often variable rate; settle on the nearest common rate.
    return min((24, 25, 30, 50, 60), key=lambda r: abs(r - info.fps))


def output_duration(config: Config, info: MasterInfo | None) -> float | None:
    if config.trim:
        end = config.trim[1] if not info else min(config.trim[1], info.duration)
        return end - config.trim[0]
    return info.duration if info else None


# --- layers ----------------------------------------------------------------------------

def build_layers(config: Config, variant: Variant, duration: float | None) -> list[Layer]:
    """Every overlay for one variant, in draw order: images, texts, captions, hook, end card."""
    zones = config.zones()
    style = lambda name: layout.style_from(name, config.styles)  # noqa: E731
    layers: list[Layer] = []
    for i, spec in enumerate(config.images, 1):
        layers.append(layout.image_layer(f"image {i}", (config.dir / spec.file).resolve(), spec.start, spec.end,
                                         spec.width, spec.position, zones))
    for i, spec in enumerate(config.texts, 1):
        layers.append(layout.text_layer(f"text {i}", spec.text, spec.start, spec.end, style(spec.style),
                                        spec.position, zones))
    if config.captions_file:
        path = config.dir / config.captions_file
        if not path.is_file():
            raise UsageError(f"không tìm thấy {rel(path)}")
        for i, cue in enumerate(parse_srt(path.read_text(encoding="utf-8")), 1):
            layers.append(layout.text_layer(f"caption {i}", cue.text, cue.start, cue.end,
                                            style(config.captions_style), config.captions_position, zones))
    layers.append(layout.text_layer("hook", variant.hook, 0.0, config.hook_duration, style(config.hook_style),
                                    config.hook_position, zones))
    if config.end_card:
        e = config.end_card
        end = e.end or duration or e.start + 2.0
        icon = (config.dir / e.icon).resolve() if e.icon else None
        layers.append(layout.end_card_layer(e.start, end, zones, title=e.title, subtitle=e.subtitle, cta=e.cta,
                                            icon=icon, background=e.background, overrides=config.styles))
    if len(layers) > MAX_SIDE_LAYERS:
        raise UsageError(f"{len(layers)} lớp chữ/ảnh là quá nhiều; gộp bớt subtitle")
    return layers


def blocking(layers: list[Layer]) -> list[str]:
    return [f"{l.name} “{l.text[:40]}”: {msg}" for l in layers for msg in l.issues
            if not msg.startswith("đã thu nhỏ")]


def timing_issues(layers: list[Layer], duration: float | None) -> list[str]:
    if duration is None:
        return []
    return [f"{l.name} kết thúc {l.end:.2f}s nhưng video chỉ dài {duration:.2f}s"
            for l in layers if l.end > duration + 0.05]


def key_times(layers: list[Layer], duration: float | None, limit: int = 12) -> list[float]:
    """Moments worth a review tile: middle of every overlay, plus start and end of the video."""
    times = {0.5 if (duration or 1) > 1 else 0.0}
    times.update(round((l.start + min(l.end, duration or l.end)) / 2, 2) for l in layers)
    if duration:
        times.add(round(max(0.0, duration - 0.3), 2))
    picked: list[float] = []
    for t in sorted(times):
        if not picked or t - picked[-1] >= 0.3:
            picked.append(t)
    if len(picked) > limit:
        step = len(picked) / limit
        picked = [picked[int(i * step)] for i in range(limit)]
    return picked


# --- ffmpeg ----------------------------------------------------------------------------

def fit_mode(config: Config, info: MasterInfo) -> str:
    if config.fit != "auto":
        return config.fit
    return "scale" if abs((info.width / info.height) / (W / H) - 1) < 0.01 else "blur"


def base_filter(mode: str, fps: int, source: str = "0:v", out: str = "base") -> str:
    fill = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
    fitin = f"scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos"
    tail = f"setsar=1,fps={fps}"
    if mode == "scale":
        return f"[{source}]scale={W}:{H}:flags=lanczos,{tail}[{out}]"
    if mode == "crop":
        return f"[{source}]{fill},{tail}[{out}]"
    if mode == "pad":
        return f"[{source}]{fitin},pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,{tail}[{out}]"
    if mode == "blur":
        return (f"[{source}]split=2[bgsrc][fgsrc];"
                f"[bgsrc]{fill},gblur=sigma=50,eq=brightness=-0.12:saturation=1.15[bg];"
                f"[fgsrc]{fitin}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,{tail}[{out}]")
    raise UsageError(f"fit '{mode}' không hợp lệ")


@dataclass
class Loudness:
    input_i: float
    input_tp: float
    input_lra: float
    input_thresh: float
    target_offset: float

    def filter(self, target: float) -> str:
        return (f"loudnorm=I={target}:TP={TRUE_PEAK}:LRA={LRA}:measured_I={self.input_i}:"
                f"measured_TP={self.input_tp}:measured_LRA={self.input_lra}:"
                f"measured_thresh={self.input_thresh}:offset={self.target_offset}:linear=true")


def input_args(config: Config, master: Path) -> list[str]:
    args = []
    if config.trim:
        args += ["-ss", f"{config.trim[0]:.3f}", "-to", f"{config.trim[1]:.3f}"]
    return args + ["-i", str(master)]


def measure_loudness(config: Config, master: Path, target: float) -> Loudness | None:
    """First loudnorm pass over the master's audio; None when the track is silent."""
    result = subprocess.run(
        [need("ffmpeg"), "-hide_banner", "-nostats", *input_args(config, master), "-vn",
         "-af", f"loudnorm=I={target}:TP={TRUE_PEAK}:LRA={LRA}:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    blocks = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", result.stderr)
    if result.returncode or not blocks:
        raise UsageError(f"đo loudness thất bại: {result.stderr.strip()[-400:]}")
    data = json.loads(blocks[-1])
    if "inf" in data["input_i"]:
        return None
    return Loudness(*(float(data[k]) for k in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")))


def build_command(config: Config, info: MasterInfo, layers: list[tuple[Layer, Path]], out: Path, *,
                  fps: int, duration: float, loudness: Loudness | None, draft: bool,
                  title: str = "") -> list[str]:
    """Full ffmpeg invocation; pure so it can be unit-tested and printed with --dry-run."""
    cmd = [need("ffmpeg"), "-hide_banner", "-y", "-loglevel", "error", "-progress", "pipe:1", "-nostats"]
    cmd += input_args(config, info.path)
    for layer, png in layers:
        cmd += ["-loop", "1", "-framerate", str(fps), "-t", f"{min(layer.end, duration):.3f}", "-i", str(png)]
    silent_index = None
    if not info.has_audio:
        silent_index = len(layers) + 1
        cmd += ["-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]

    graph = [base_filter(fit_mode(config, info), fps)]
    prev = "base"
    for i, (layer, _) in enumerate(layers, 1):
        end = min(layer.end, duration)
        chain = "format=rgba"
        fade = min(layer.fade, (end - layer.start) / 3)
        if fade > 0 and layer.start > 0:
            chain += f",fade=t=in:st={layer.start:.3f}:d={fade:.3f}:alpha=1"
        if fade > 0 and end < duration - 0.01:
            chain += f",fade=t=out:st={end - fade:.3f}:d={fade:.3f}:alpha=1"
        graph.append(f"[{i}:v]{chain}[l{i}]")
        graph.append(f"[{prev}][l{i}]overlay=x={layer.x}:y={layer.y}:eof_action=pass:"
                     f"enable='between(t,{layer.start:.3f},{end:.3f})'[v{i}]")
        prev = f"v{i}"
    graph.append(f"[{prev}]format=yuv420p[vout]")

    if silent_index is not None:
        audio = f"{silent_index}:a"
    else:
        chain = "aresample=48000"
        if loudness and not draft and config.loudness is not None:
            chain = f"{loudness.filter(config.loudness)},aresample=48000"
        graph.append(f"[0:a]{chain}[aout]")
        audio = "[aout]"

    if draft:
        video = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "24"]
    else:
        video = ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-level:v", "4.2",
                 "-bf", "2", "-g", str(fps * 2), "-keyint_min", str(fps)]
    cmd += ["-filter_complex", ";".join(graph), "-map", "[vout]", "-map", audio]
    cmd += video + ["-pix_fmt", "yuv420p", "-r", str(fps),
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-t", f"{duration:.3f}", "-movflags", "+faststart",
                    # Drop source metadata: iPhone footage carries GPS location and device details.
                    "-map_metadata", "-1", "-map_chapters", "-1",
                    "-metadata", f"title={title or out.stem}", "-metadata", f"comment={config.creative_id}",
                    str(out)]
    return cmd


def run_ffmpeg(cmd: list[str], duration: float, label: str) -> None:
    tty = sys.stdout.isatty()
    shown = -1
    # -loglevel error keeps stderr tiny, so reading it after stdout cannot deadlock.
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
        assert proc.stdout is not None and proc.stderr is not None
        for line in proc.stdout:
            if line.startswith("out_time_us=") and duration > 0:
                try:
                    pct = min(100, int(int(line.split("=")[1]) / 1e6 / duration * 100))
                except ValueError:
                    continue
                if tty and pct != shown:
                    bar = "█" * (pct // 4) + "░" * (25 - pct // 4)
                    print(f"\r    {label} {bar} {pct:3d}%", end="", flush=True)
                    shown = pct
        err = proc.stderr.read()
        code = proc.wait()
    if tty:
        print("\r" + " " * 70 + "\r", end="")
    if code:
        raise UsageError(f"ffmpeg lỗi khi render {label}:\n{err.strip()[-1500:]}")


def grab_frame(video: Path, t: float, vf: str | None = None, trim_start: float = 0.0) -> Image.Image:
    cmd = [need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-ss", f"{trim_start + t:.3f}", "-i", str(video)]
    if vf:
        cmd += ["-filter_complex", vf, "-map", "[base]"]
    cmd += ["-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode or not result.stdout:
        raise UsageError(f"không lấy được khung hình {t:.2f}s từ {rel(video)}: {result.stderr.decode()[-300:]}")
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")


def measure_output(video: Path) -> dict:
    """Integrated loudness and true peak of the finished file (EBU R128 scan)."""
    result = subprocess.run(
        [need("ffmpeg"), "-hide_banner", "-nostats", "-i", str(video), "-map", "0:a",
         "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    summary = result.stderr.rsplit("Summary:", 1)[-1]
    i = re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", summary)
    peak = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", summary)
    as_float = lambda m: None if not m or "inf" in m.group(1) else float(m.group(1))  # noqa: E731
    return {"integrated_lufs": as_float(i), "true_peak_dbtp": as_float(peak)}


def verify(video: Path, fps: int, duration: float) -> tuple[dict, list[str]]:
    data = probe(video)
    v = next(s for s in data["streams"] if s["codec_type"] == "video")
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    spec = {
        "width": v["width"], "height": v["height"], "video_codec": v["codec_name"], "profile": v.get("profile"),
        "pix_fmt": v.get("pix_fmt"), "fps": round(ratio(v.get("avg_frame_rate")), 3),
        "duration": round(float(data["format"]["duration"]), 3), "bytes": int(data["format"]["size"]),
        "audio_codec": a and a["codec_name"], "sample_rate": a and int(a["sample_rate"]), "channels": a and a["channels"],
    }
    problems = []
    if (spec["width"], spec["height"]) != (W, H):
        problems.append(f"kích thước {spec['width']}×{spec['height']} khác {W}×{H}")
    if spec["video_codec"] != "h264" or spec["pix_fmt"] != "yuv420p":
        problems.append(f"video {spec['video_codec']}/{spec['pix_fmt']} thay vì h264/yuv420p")
    if abs(spec["fps"] - fps) > 0.05:
        problems.append(f"fps {spec['fps']} khác {fps}")
    if abs(spec["duration"] - duration) > 0.15:
        problems.append(f"thời lượng {spec['duration']}s khác {duration:.2f}s")
    if not a or a["codec_name"] != "aac" or spec["sample_rate"] != 48000 or spec["channels"] != 2:
        problems.append("audio không phải AAC 48 kHz stereo")
    if spec["bytes"] > 250 * 1024 * 1024:
        problems.append("file > 250 MB, quá giới hạn upload trên web của một số nền tảng")
    return spec, problems


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --- metadata cross-check --------------------------------------------------------------

def meta_warnings(config: Config, variant: Variant) -> list[str]:
    if not variant.meta:
        return []
    path = config.dir / variant.meta
    if not path.is_file():
        return [f"{variant.meta} không tồn tại"]
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        return [f"{variant.meta}: TOML lỗi — {exc}"]
    found = []
    expected = f"{config.creative_id}-hook{variant.id}"
    if data.get("creative_id") != expected:
        found.append(f"{variant.meta}: creative_id là '{data.get('creative_id')}', mong đợi '{expected}'")
    title = re.sub(r"\s*#shorts\s*$", "", data.get("youtube", {}).get("title", ""), flags=re.I)
    norm = lambda s: re.sub(r"[^\w]+", " ", s.lower()).strip()  # noqa: E731
    if title and norm(title) != norm(variant.hook):
        found.append(f"{variant.meta}: tiêu đề “{title}” khác hook “{variant.hook}”")
    if "synthetic_media" not in data.get("youtube", {}):
        found.append(f"{variant.meta}: thiếu synthetic_media")
    return found


# --- commands --------------------------------------------------------------------------

def creative_dirs(paths: list[str]) -> list[Path]:
    dirs = []
    for p in paths:
        path = Path(p).resolve()
        if path.is_file():
            path = path.parent
        if not path.is_dir():
            raise UsageError(f"{p} không phải thư mục")
        dirs.append(path)
    return dirs


def write_png(layer: Layer, folder: Path, index: int) -> Path:
    path = folder / f"layer-{index:02d}.png"
    layer.image.save(path)
    return path


def layout_sheet(config: Config, info: MasterInfo | None, variants: list[Variant], duration: float | None) -> tuple[Path, list[str]]:
    """Review tiles for every variant before rendering; uses master frames when available."""
    zones = config.zones()
    problems: list[str] = []
    tiles = []
    vf = None
    if info:
        vf = base_filter(fit_mode(config, info), output_fps(config, info))
    for variant in variants:
        layers = build_layers(config, variant, duration)
        problems += [f"hook {variant.id} · {p}" for p in blocking(layers) + timing_issues(layers, duration)]
        times = key_times(layers, duration) if variant is variants[0] else [config.hook_duration / 2]
        for t in times:
            bg = grab_frame(info.path, t, vf, config.trim[0] if config.trim else 0.0) if info else layout.placeholder(f"{t:.1f}s")
            frame = layout.composite(bg, layers, t)
            tiles.append(layout.annotate(frame, zones, f"{variant.id.upper()} · {t:.1f}s", layers, t))
    sheet = layout.contact_sheet(tiles, f"{config.creative_id} · bố cục · " + ", ".join(z.label for z in zones))
    out = config.exports / "review" / f"{config.creative_id}-layout.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)
    return out, problems


def cmd_init(args) -> int:
    for directory in creative_dirs(args.dirs):
        path = directory / CONFIG_NAME
        if path.exists() and not args.force:
            print(f"bỏ qua {rel(path)} (đã có; dùng --force để ghi đè)")
            continue
        path.write_text(init_config(directory), encoding="utf-8")
        print(f"đã tạo {rel(path)}")
    return 0


def cmd_check(args) -> int:
    failed = False
    for directory in creative_dirs(args.dirs):
        print(f"\n{directory.name}")
        try:
            config = Config.load(directory)
            master = config.resolve_master()
            info = master_info(master) if master else None
            duration = output_duration(config, info)
            if info:
                print(f"  master  {rel(master)} · {info.describe()}")
                if info.hdr:
                    print("  ✗ master HDR (HLG/PQ) sẽ bị bạc màu khi xuất SDR — xem README mục HDR")
                    failed = True
                if duration and duration > 60:
                    print(f"  ⚠ dài {duration:.1f}s; brief nhắm 12–25s")
            else:
                print(f"  master  chưa có trong {rel(config.exports)} — kiểm tra bố cục trên nền giả")
            base_size = layout.style_from(config.hook_style, config.styles).size
            for variant in config.variants:
                hook = next(l for l in build_layers(config, variant, duration) if l.name == "hook")
                note = f"{hook.size}px" + (f" (thu nhỏ từ {base_size})" if hook.size != base_size else "")
                print(f"  hook {variant.id}  “{variant.hook}” · {note}")
                for w in meta_warnings(config, variant):
                    print(f"  ⚠ {w}")
            sheet, problems = layout_sheet(config, info, config.variants, duration)
            for p in problems:
                print(f"  ✗ {p}")
            failed |= bool(problems)
            print(f"  bố cục  {rel(sheet)}")
            if not problems:
                print("  ✓ mọi lớp chữ nằm trong vùng an toàn")
        except (UsageError, LayoutError) as exc:
            print(f"  ✗ {exc}")
            failed = True
    return 1 if failed else 0


def fingerprint(config: Config, master: Path, variant: Variant, draft: bool) -> str:
    h = hashlib.sha256()
    for part in (TOOL_VERSION, variant.id, variant.hook, str(draft), (REPO / "tools/render/safezones.toml").read_text(),
                 (config.dir / CONFIG_NAME).read_text(encoding="utf-8")):
        h.update(part.encode())
    files = [master] + [config.dir / s.file for s in config.images]
    if config.captions_file:
        files.append(config.dir / config.captions_file)
    if config.end_card and config.end_card.icon:
        files.append(config.dir / config.end_card.icon)
    for f in files:
        st = f.stat()
        h.update(f"{f.name}:{st.st_size}:{st.st_mtime_ns}".encode())
    return h.hexdigest()[:16]


def load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def render_one(config: Config, info: MasterInfo, variant: Variant, *, draft: bool, preview: bool, force: bool,
               loudness, manifest: dict) -> dict | None:
    """Render one variant; `loudness` is a callable so the master is only measured when something renders."""
    fps = output_fps(config, info)
    duration = output_duration(config, info)
    assert duration
    out = config.output(variant, draft)
    key = out.name
    stamp = fingerprint(config, info.path, variant, draft)
    if not force and out.is_file() and manifest.get(key, {}).get("fingerprint") == stamp:
        print(f"  hook {variant.id}  không đổi → giữ {rel(out)} (dùng --force để render lại)")
        return None

    layers = build_layers(config, variant, duration)
    problems = blocking(layers) + timing_issues(layers, duration)
    if problems:
        raise UsageError(f"hook {variant.id}: chữ lấn UI nền tảng hoặc sai thời gian:\n  - " + "\n  - ".join(problems)
                         + "\n  Chạy `render.py check` để xem bố cục.")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kv-render-") as tmp:
        pngs = [(layer, write_png(layer, Path(tmp), i)) for i, layer in enumerate(layers, 1)]
        partial = out.with_suffix(".partial.mp4")
        cmd = build_command(config, info, pngs, partial, fps=fps, duration=duration, loudness=loudness(),
                            draft=draft, title=variant.hook)
        try:
            run_ffmpeg(cmd, duration, f"hook {variant.id}")
        except BaseException:
            partial.unlink(missing_ok=True)
            raise
        partial.replace(out)

    spec, problems = verify(out, fps, duration)
    audio = measure_output(out)
    if config.loudness is not None and not draft and audio["integrated_lufs"] is not None and info.has_audio:
        if abs(audio["integrated_lufs"] - config.loudness) > 1.0:
            problems.append(f"loudness {audio['integrated_lufs']} LUFS lệch mục tiêu {config.loudness}")
    if audio["true_peak_dbtp"] is not None and audio["true_peak_dbtp"] > -0.5:
        problems.append(f"true peak {audio['true_peak_dbtp']} dBTP dễ bị méo khi nền tảng nén lại")

    review = config.exports / "review"
    review.mkdir(exist_ok=True)
    cover_at = variant.cover_at if variant.cover_at is not None else min(config.hook_duration / 2, duration / 2)
    cover = out.with_name(out.stem + "-cover.jpg")
    grab_frame(out, cover_at).save(cover, quality=92)

    zones = config.zones()
    tiles = [layout.annotate(grab_frame(out, t), zones, f"{t:.1f}s", layers, t) for t in key_times(layers, duration)]
    sheet = review / f"{out.stem}-sheet.jpg"
    layout.contact_sheet(tiles, f"{out.stem} · " + ", ".join(z.label for z in zones)).save(sheet, quality=88)

    preview_path = None
    if preview:
        preview_path = review / f"{out.stem}-safezones.mp4"
        overlay = Path(tempfile.mkstemp(suffix=".png")[1])
        layout.safezone_overlay(zones).save(overlay)
        result = subprocess.run(
            [need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", str(out), "-i", str(overlay),
             "-filter_complex", "[0:v][1:v]overlay=0:0,scale=540:960", "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "28", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(preview_path)],
            capture_output=True, text=True)
        overlay.unlink(missing_ok=True)
        if result.returncode:
            problems.append(f"không tạo được preview safe zone: {result.stderr.strip()[-200:]}")
            preview_path = None

    entry = {
        "creative_id": f"{config.creative_id}-hook{variant.id}",
        "variant": variant.id,
        "hook": variant.hook,
        "file": rel(out),
        "draft": draft,
        "sha256": sha256(out),
        **spec,
        **audio,
        "loudness_target": None if draft else config.loudness,
        "master": {"file": rel(info.path), "sha256": sha256(info.path), "probe": info.describe(),
                   "fit": fit_mode(config, info), "trim": list(config.trim) if config.trim else None},
        "cover": rel(cover),
        "review_sheet": rel(sheet),
        "safezone_preview": rel(preview_path) if preview_path else None,
        "platforms": config.platforms,
        "layers": [{"name": l.name, "text": l.text, "start": l.start, "end": l.end, "box": list(l.box),
                    "font_px": l.size} for l in layers],
        "meta": variant.meta,
        "warnings": problems + meta_warnings(config, variant),
        "fingerprint": stamp,
        "tool_version": TOOL_VERSION,
        "rendered_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    manifest[key] = entry
    mb = spec["bytes"] / 1024 / 1024
    lufs = audio["integrated_lufs"]
    print(f"  hook {variant.id}  ✓ {rel(out)} · {spec['duration']:.2f}s · {mb:.1f} MB · "
          f"{'—' if lufs is None else f'{lufs:.1f} LUFS'} · TP {audio['true_peak_dbtp'] or '—'} dBTP")
    print(f"          cover {cover.name} · sheet {rel(sheet)}" + (f" · preview {preview_path.name}" if preview_path else ""))
    for w in entry["warnings"]:
        print(f"          ⚠ {w}")
    return entry


def cmd_render(args) -> int:
    failed = False
    rendered: list[tuple[Config, dict]] = []
    for directory in creative_dirs(args.dirs):
        print(f"\n{directory.name}")
        try:
            config = Config.load(directory)
            master = config.resolve_master()
            if not master:
                raise UsageError(f"chưa có master. Đặt bản dựng sạch (không chữ) vào {rel(config.exports)}/master.mov")
            info = master_info(master)
            print(f"  master  {rel(master)} · {info.describe()}")
            if info.hdr and not args.allow_hdr:
                raise UsageError("master là HDR (HLG/PQ); bản SDR sẽ bị bạc màu. Xuất lại SDR (xem README mục HDR) "
                                 "hoặc thêm --allow-hdr nếu chấp nhận")
            variants = [v for v in config.variants if not args.variant or v.id in args.variant]
            if not variants:
                raise UsageError(f"không có biến thể {', '.join(args.variant)}; có {', '.join(v.id for v in config.variants)}")
            measured: list[Loudness | None] = []

            def loudness(config=config, master=master, info=info, measured=measured) -> Loudness | None:
                if config.loudness is None or not info.has_audio or args.draft:
                    return None
                if not measured:
                    measured.append(measure_loudness(config, master, config.loudness))
                    print(f"  audio   {measured[0].input_i:.1f} LUFS → {config.loudness:.0f} LUFS" if measured[0]
                          else "  audio   im lặng, giữ nguyên")
                return measured[0]
            manifest_path = config.exports / "render-manifest.json"
            manifest = load_manifest(manifest_path)
            for variant in variants:
                entry = render_one(config, info, variant, draft=args.draft, preview=args.preview, force=args.force,
                                   loudness=loudness, manifest=manifest)
                if entry:
                    rendered.append((config, entry))
                    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except (UsageError, LayoutError) as exc:
            print(f"  ✗ {exc}")
            failed = True
    finals = [(c, e) for c, e in rendered if not e["draft"] and e["meta"]]
    if finals:
        print("\nXem lại bản export trên điện thoại, rồi kiểm tra metadata YouTube (không gửi gì):")
        for config, entry in finals:
            print(f"  tools/youtube/.venv/bin/python tools/youtube/upload.py upload {entry['file']} "
                  f"--meta {rel(config.dir / entry['meta'])} --dry-run")
    return 1 if failed else 0


def cmd_safezones(args) -> int:
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    zones = layout.load_safezones()
    all_zones = list(zones.values())
    layout.safezone_overlay(all_zones).save(out / "safezones-all-1080x1920.png")
    for key, zone in zones.items():
        layout.safezone_overlay([zone]).save(out / f"safezones-{key}-1080x1920.png")
    print(f"đã ghi {len(zones) + 1} overlay vào {rel(out)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init", help="tạo render.toml từ bảng hook trong BRIEF.md")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--force", action="store_true", help="ghi đè render.toml đã có")
    p = sub.add_parser("check", help="kiểm tra cấu hình, master và vùng an toàn; xuất ảnh bố cục")
    p.add_argument("dirs", nargs="+")
    p = sub.add_parser("render", help="render các biến thể hook")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--variant", action="append", help="chỉ render biến thể này (lặp lại được)")
    p.add_argument("--draft", action="store_true", help="nhanh, chất lượng thấp hơn, không chuẩn hoá âm lượng")
    p.add_argument("--preview", action="store_true", help="thêm video 540×960 có vẽ vùng an toàn để xem trên điện thoại")
    p.add_argument("--force", action="store_true", help="render lại dù cấu hình và master không đổi")
    p.add_argument("--allow-hdr", action="store_true", help="chấp nhận master HDR (màu sẽ sai)")
    p = sub.add_parser("safezones", help="xuất PNG vùng an toàn để dùng trong app dựng video")
    p.add_argument("--out", default=str(REPO / "content/shared/social-kit/safezones"))
    args = parser.parse_args(argv)
    try:
        return {"init": cmd_init, "check": cmd_check, "render": cmd_render, "safezones": cmd_safezones}[args.command](args)
    except (UsageError, LayoutError) as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
