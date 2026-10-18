"""Text/image layers drawn with Pillow, platform safe zones and review annotations.

Everything here works on the 1080×1920 output canvas. ffmpeg only composites the PNGs this
module produces, so the bounding boxes checked against safe zones are exactly what ships.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
HERE = Path(__file__).resolve().parent
SAFEZONES_FILE = HERE / "safezones.toml"
DEFAULT_FONT = "/System/Library/Fonts/SFNS.ttf"

# Colour emoji need a bitmap font Pillow cannot mix into a text run; burned-in text stays plain.
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U0000FE0F\U0000200D]"
)


class LayoutError(Exception):
    """Text that cannot be laid out: unsupported characters, too long, unknown style."""


# --- safe zones ------------------------------------------------------------------------

@dataclass(frozen=True)
class SafeZone:
    key: str
    label: str
    color: str
    top: int
    bottom: int
    left: int
    right: int

    @property
    def rect(self) -> tuple[int, int, int, int]:
        """The area no platform UI covers: (x0, y0, x1, y1)."""
        return self.left, self.top, W - self.right, H - self.bottom


def load_safezones(path: Path = SAFEZONES_FILE) -> dict[str, SafeZone]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return {
        key: SafeZone(key, v.get("label", key), v.get("color", "#ff3b30"),
                      int(v["top"]), int(v["bottom"]), int(v["left"]), int(v["right"]))
        for key, v in data.items()
    }


def combined(zones: list[SafeZone]) -> SafeZone:
    """The strictest margins across the chosen platforms."""
    return SafeZone(
        "combined", " + ".join(z.label for z in zones), "#ff3b30",
        max(z.top for z in zones), max(z.bottom for z in zones),
        max(z.left for z in zones), max(z.right for z in zones),
    )


def violations(box: tuple[int, int, int, int], zones: list[SafeZone]) -> list[str]:
    """Which platform UI a box runs into, and by how many pixels on each side."""
    x0, y0, x1, y1 = box
    found = []
    for zone in zones:
        sx0, sy0, sx1, sy1 = zone.rect
        sides = []
        if y0 < sy0:
            sides.append(f"trên {sy0 - y0}px")
        if y1 > sy1:
            sides.append(f"dưới {y1 - sy1}px")
        if x0 < sx0:
            sides.append(f"trái {sx0 - x0}px")
        if x1 > sx1:
            sides.append(f"phải {x1 - sx1}px")
        if sides:
            found.append(f"{zone.label}: lấn {', '.join(sides)}")
    return found


# --- styles ----------------------------------------------------------------------------

@dataclass(frozen=True)
class Style:
    size: int = 64
    weight: str = "Bold"
    font: str = DEFAULT_FONT
    font_index: int = 0
    color: str = "#ffffff"
    background: str | None = None      # per-line rounded box behind the text
    padding_x: int = 26
    padding_y: int = 14
    radius: int = 18
    stroke_width: int = 0
    stroke_color: str = "#000000"
    shadow: bool = False
    line_spacing: float = 1.0
    max_lines: int = 3
    max_width: int | None = None        # px; default = widest centred box the safe zone allows
    fade: float = 0.12                  # seconds of alpha fade in/out; 0 = hard cut


STYLES: dict[str, Style] = {
    # Native-looking TikTok/Reels text: dark text on white per-line pills.
    "hook": Style(size=74, weight="Bold", color="#111111", background="#ffffff",
                  padding_x=30, padding_y=16, radius=22),
    # Dialogue/voice subtitles: white with a heavy outline, readable on any footage.
    "caption": Style(size=62, weight="Bold", stroke_width=8, shadow=True, fade=0.0),
    # Small factual tag such as "Decoy vault · Veilnest Pro".
    "label": Style(size=46, weight="Semibold", background="#000000b3",
                   padding_x=24, padding_y=12, radius=16),
    # Big statement text without a box.
    "outline": Style(size=80, weight="Heavy", stroke_width=9, shadow=True),
    # End-card call to action.
    "cta": Style(size=50, weight="Bold", color="#ffffff", background="#0a84ff",
                 padding_x=34, padding_y=18, radius=999, max_lines=1),
}


def style_from(name: str, overrides: dict[str, dict] | None = None) -> Style:
    overrides = overrides or {}
    base = STYLES.get(name)
    if base is None and name not in overrides:
        raise LayoutError(f"style '{name}' không tồn tại; có sẵn: {', '.join(STYLES)}")
    base = base or Style()
    extra = overrides.get(name, {})
    unknown = set(extra) - set(Style.__dataclass_fields__)
    if unknown:
        raise LayoutError(f"[styles.{name}] có khoá lạ: {', '.join(sorted(unknown))}")
    return replace(base, **extra)


_FONTS: dict[tuple, ImageFont.FreeTypeFont] = {}


def load_font(style: Style, size: int | None = None) -> ImageFont.FreeTypeFont:
    size = size or style.size
    key = (style.font, style.font_index, style.weight, size)
    if key not in _FONTS:
        path = Path(style.font).expanduser()
        if not path.is_file():
            raise LayoutError(f"không tìm thấy font {path}")
        font = ImageFont.truetype(str(path), size, index=style.font_index)
        try:
            font.set_variation_by_name(style.weight)
        except (OSError, ValueError):
            pass  # static font: the file itself sets the weight
        _FONTS[key] = font
    return _FONTS[key]


def parse_color(value: str) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    if len(value) not in (6, 8) or not re.fullmatch(r"[0-9a-fA-F]+", value):
        raise LayoutError(f"màu '#{value}' phải ở dạng #rrggbb hoặc #rrggbbaa")
    rgba = [int(value[i:i + 2], 16) for i in range(0, len(value), 2)]
    return tuple(rgba + [255] * (4 - len(rgba)))  # type: ignore[return-value]


# --- text layout -----------------------------------------------------------------------

def wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Greedy word wrap; explicit newlines are kept. A single word wider than the box stays whole."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            trial = f"{current} {word}".strip()
            if current and font.getlength(trial) > width:
                lines.append(current)
                current = word
            else:
                current = trial
        lines.append(current)
    return lines


def even_wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Same number of lines as a greedy wrap, at the narrowest width that keeps that count."""
    lines = wrap(text, font, width)
    if len(lines) < 2:
        return lines
    lo, hi = 1, width
    while lo < hi:
        mid = (lo + hi) // 2
        if len(wrap(text, font, mid)) <= len(lines):
            hi = mid
        else:
            lo = mid + 1
    return wrap(text, font, lo)


def balanced_wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Break where the sentence breaks when that costs no extra line ("Two PINs. / Two different vaults."),
    otherwise wrap evenly so no line is left with a single dangling word."""
    if "\n" in text:
        return wrap(text, font, width)
    greedy = wrap(text, font, width)
    if len(greedy) < 2:
        return greedy
    phrases = [p for p in re.split(r"(?<=[.!?:;,—])\s+", text.strip()) if p]
    if len(phrases) > 1:
        by_phrase = [line for phrase in phrases for line in even_wrap(phrase, font, width)]
        if len(by_phrase) <= len(greedy):
            return by_phrase
    return even_wrap(text, font, width)


def default_max_width(zones: list[SafeZone]) -> int:
    """Widest box centred on the frame that stays clear of every platform's side UI."""
    zone = combined(zones)
    return 2 * min(W // 2 - zone.left, W - zone.right - W // 2)


@dataclass
class Rendered:
    image: Image.Image
    size: int
    lines: list[str]


def render_text(text: str, style: Style, max_width: int) -> Rendered:
    if not text.strip():
        raise LayoutError("text rỗng")
    if EMOJI.search(text):
        raise LayoutError(f"emoji không burn được vào video: {text!r}. Để emoji trong caption bài đăng.")
    pad_x = style.padding_x if style.background else style.stroke_width
    inner = max_width - 2 * pad_x
    size = style.size
    # Shrink up to 40% before giving up, so a slightly long hook still fits in max_lines.
    while True:
        font = load_font(style, size)
        lines = balanced_wrap(text, font, inner)
        too_wide = any(font.getlength(line) > inner for line in lines)
        if len(lines) <= style.max_lines and not too_wide:
            break
        if size <= style.size * 0.6:
            raise LayoutError(
                f"text quá dài cho {style.max_lines} dòng trong {max_width}px: {text!r}. Rút ngắn hoặc xuống dòng tay."
            )
        size -= 2

    ascent, descent = font.getmetrics()
    line_h = round((ascent + descent) * style.line_spacing)
    pad_y = style.padding_y if style.background else style.stroke_width
    row_h = line_h + 2 * pad_y
    widths = [int(font.getlength(line)) for line in lines]
    box_w = max(widths) + 2 * pad_x
    margin = 24 if style.shadow else 0  # room for the blurred shadow
    canvas = Image.new("RGBA", (box_w + 2 * margin, row_h * len(lines) + 2 * margin), (0, 0, 0, 0))

    if style.shadow:
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        for i, line in enumerate(lines):
            x = margin + (box_w - widths[i]) // 2
            y = margin + i * row_h + pad_y + 6
            sd.text((x, y), line, font=font, fill=(0, 0, 0, 170),
                    stroke_width=style.stroke_width, stroke_fill=(0, 0, 0, 170))
        canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))

    draw = ImageDraw.Draw(canvas)
    fill = parse_color(style.color)
    stroke = parse_color(style.stroke_color)
    if style.background:
        bg = parse_color(style.background)
        # Lines of a block overlap slightly so the pills read as one shape, like in-app text.
        overlap = min(style.radius, pad_y)
        for i, w in enumerate(widths):
            x0 = margin + (box_w - (w + 2 * pad_x)) // 2
            y0 = margin + i * row_h - (overlap // 2 if i else 0)
            y1 = margin + (i + 1) * row_h + (overlap // 2 if i < len(lines) - 1 else 0)
            draw.rounded_rectangle((x0, y0, x0 + w + 2 * pad_x, y1),
                                   radius=min(style.radius, row_h // 2), fill=bg)
    for i, line in enumerate(lines):
        x = margin + (box_w - widths[i]) // 2
        y = margin + i * row_h + pad_y
        draw.text((x, y), line, font=font, fill=fill,
                  stroke_width=style.stroke_width, stroke_fill=stroke)
    return Rendered(canvas, size, lines)


# --- layers ----------------------------------------------------------------------------

POSITIONS = ("top", "upper", "center", "lower", "bottom")


@dataclass
class Layer:
    name: str                      # e.g. "hook", "text 2", "caption 5"
    start: float
    end: float
    image: Image.Image
    x: int
    y: int
    fade: float = 0.0
    text: str = ""
    size: int | None = None        # final font size after auto-fit
    issues: list[str] = field(default_factory=list)
    content_box: tuple[int, int, int, int] | None = None   # full-frame layers: the part that must stay safe

    @property
    def box(self) -> tuple[int, int, int, int]:
        """Visible pixels only, so shadow padding does not count as a safe-zone hit."""
        if self.content_box:
            return self.content_box
        bbox = self.image.getbbox() or (0, 0, 0, 0)
        return self.x + bbox[0], self.y + bbox[1], self.x + bbox[2], self.y + bbox[3]

    def active(self, t: float) -> bool:
        return self.start <= t < self.end


def place(img: Image.Image, position: str | float, zones: list[SafeZone]) -> tuple[int, int]:
    """Centre horizontally; vertical slot is a named band of the combined safe area or a 0–1 fraction."""
    zone = combined(zones)
    _, top, _, bottom = zone.rect
    w, h = img.size
    x = (W - w) // 2
    gap = 32
    if isinstance(position, (int, float)):
        y = round(H * float(position) - h / 2)
    elif position == "top":
        y = top + gap
    elif position == "upper":
        y = round(top + (bottom - top) * 0.22 - h / 2)
    elif position == "center":
        y = round((top + bottom) / 2 - h / 2)
    elif position == "lower":
        y = round(top + (bottom - top) * 0.78 - h / 2)
    elif position == "bottom":
        y = bottom - gap - h
    else:
        raise LayoutError(f"position '{position}' không hợp lệ; dùng {', '.join(POSITIONS)} hoặc số 0–1")
    return x, y


def text_layer(name: str, text: str, start: float, end: float, style: Style,
               position: str | float, zones: list[SafeZone]) -> Layer:
    rendered = render_text(text, style, style.max_width or default_max_width(zones))
    x, y = place(rendered.image, position, zones)
    layer = Layer(name, start, end, rendered.image, x, y, style.fade, text, rendered.size)
    layer.issues = violations(layer.box, zones)
    if rendered.size < style.size:
        layer.issues.append(f"đã thu nhỏ chữ {style.size}→{rendered.size}px để vừa {style.max_lines} dòng")
    return layer


def image_layer(name: str, path: Path, start: float, end: float, width: int,
                position: str | float, zones: list[SafeZone], fade: float = 0.12) -> Layer:
    if not path.is_file():
        raise LayoutError(f"không tìm thấy ảnh {path}")
    img = Image.open(path).convert("RGBA")
    img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    x, y = place(img, position, zones)
    layer = Layer(name, start, end, img, x, y, fade, path.name)
    layer.issues = violations(layer.box, zones)
    return layer


def end_card_layer(start: float, end: float, zones: list[SafeZone], *, title: str,
                   subtitle: str = "", cta: str = "", icon: Path | None = None,
                   background: str = "#0b0b10", overrides: dict[str, dict] | None = None) -> Layer:
    """Full-frame branded end card: icon, app name, one line, CTA pill, centred in the safe area."""
    canvas = Image.new("RGBA", (W, H), parse_color(background))
    max_w = default_max_width(zones)
    parts: list[tuple[str, Image.Image]] = []
    if icon:
        if not icon.is_file():
            raise LayoutError(f"không tìm thấy icon {icon}")
        size = 300
        img = Image.open(icon).convert("RGBA").resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=round(size * 0.2237), fill=255)
        img.putalpha(Image.composite(img.getchannel("A"), mask, mask))
        # Hairline edge so a dark icon still reads against the dark card.
        ImageDraw.Draw(img).rounded_rectangle((0, 0, size - 1, size - 1), radius=round(size * 0.2237),
                                              outline=(255, 255, 255, 46), width=2)
        parts.append(("icon", img))
    parts.append(("title", render_text(title, style_from("end_title", overrides), max_w).image))
    if subtitle:
        parts.append(("subtitle", render_text(subtitle, style_from("end_subtitle", overrides), max_w).image))
    if cta:
        parts.append(("cta", render_text(cta, style_from("cta", overrides), max_w).image))
    # Space above each part: more air after the icon and before the CTA.
    space = {"icon": 0, "title": 44, "subtitle": 12, "cta": 56}
    gaps = [0] + [space[kind] for kind, _ in parts[1:]]
    total = sum(img.height for _, img in parts) + sum(gaps)
    _, top, _, bottom = combined(zones).rect
    y = round((top + bottom) / 2 - total / 2)
    x0, y0, x1 = W, y, 0
    for gap, (_, part) in zip(gaps, parts):
        y += gap
        x = (W - part.width) // 2
        canvas.alpha_composite(part, (x, y))
        x0, x1 = min(x0, x), max(x1, x + part.width)
        y += part.height
    layer = Layer("end card", start, end, canvas, 0, 0, 0.18, title, content_box=(x0, y0, x1, y))
    layer.issues = violations(layer.box, zones)
    return layer


STYLES["end_title"] = Style(size=84, weight="Heavy", fade=0.0)
STYLES["end_subtitle"] = Style(size=44, weight="Medium", color="#ffffffcc", max_lines=2, fade=0.0)


# --- review drawing --------------------------------------------------------------------

def composite(background: Image.Image, layers: list[Layer], t: float) -> Image.Image:
    frame = background.convert("RGBA").resize((W, H))
    for layer in layers:
        if layer.active(t):
            frame.alpha_composite(layer.image, (layer.x, layer.y))
    return frame


def safezone_overlay(zones: list[SafeZone], labels: bool = True) -> Image.Image:
    """Transparent 1080×1920 PNG: shaded union of covered areas plus each platform's safe outline."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    zone = combined(zones)
    x0, y0, x1, y1 = zone.rect
    shade = (255, 59, 48, 70)
    for rect in ((0, 0, W, y0), (0, y1, W, H), (0, y0, x0, y1), (x1, y0, W, y1)):
        draw.rectangle(rect, fill=shade)
    font = load_font(Style(size=30, weight="Semibold"))
    x = 24
    for z in zones:
        color = parse_color(z.color)
        draw.rectangle(z.rect, outline=color, width=4)
        if labels:  # legend along the bottom edge, inside the shaded area
            draw.text((x, H - 64), z.label, font=font, fill=color, stroke_width=3, stroke_fill=(0, 0, 0, 255))
            x += int(font.getlength(z.label)) + 36
    return overlay


def annotate(frame: Image.Image, zones: list[SafeZone], caption: str,
             layers: list[Layer] | None = None, t: float | None = None) -> Image.Image:
    """A review tile: frame + safe zones + red boxes around layers that hit platform UI."""
    out = frame.convert("RGBA").resize((W, H))
    out.alpha_composite(safezone_overlay(zones))
    draw = ImageDraw.Draw(out)
    for layer in layers or []:
        if t is not None and not layer.active(t):
            continue
        hit = any(not msg.startswith("đã thu nhỏ") for msg in layer.issues)
        draw.rectangle(layer.box, outline=(255, 59, 48, 255) if hit else (52, 199, 89, 255), width=5)
    font = load_font(Style(size=44, weight="Bold"))
    draw.rounded_rectangle((20, 20, 40 + int(font.getlength(caption)), 92), radius=16, fill=(0, 0, 0, 200))
    draw.text((30, 28), caption, font=font, fill=(255, 255, 255, 255))
    return out


def contact_sheet(tiles: list[Image.Image], title: str, columns: int = 4, tile_w: int = 360) -> Image.Image:
    tile_h = tile_w * H // W
    rows = (len(tiles) + columns - 1) // columns
    head = 90
    gap = 16
    sheet = Image.new("RGB", (columns * (tile_w + gap) + gap, head + rows * (tile_h + gap) + gap), (24, 24, 27))
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 24), title, font=load_font(Style(size=40, weight="Bold")), fill=(255, 255, 255))
    for i, tile in enumerate(tiles):
        r, c = divmod(i, columns)
        sheet.paste(tile.convert("RGB").resize((tile_w, tile_h), Image.LANCZOS),
                    (gap + c * (tile_w + gap), head + r * (tile_h + gap)))
    return sheet


def placeholder(label: str) -> Image.Image:
    """Stand-in background for checking layout before the master is filmed."""
    img = Image.new("RGB", (W, H), (44, 44, 52))
    draw = ImageDraw.Draw(img)
    # Rough iPhone screen so text placement reads against a realistic shape.
    draw.rounded_rectangle((150, 260, 930, 1660), radius=80, fill=(70, 70, 82), outline=(110, 110, 125), width=6)
    font = load_font(Style(size=40, weight="Medium"))
    text = f"chưa có master · {label}"
    draw.text(((W - font.getlength(text)) / 2, 940), text, font=font, fill=(160, 160, 175))
    return img
