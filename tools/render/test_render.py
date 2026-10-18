"""Tests for render.py/layout.py. Unit tests are offline; the end-to-end test needs ffmpeg and
renders a 3-second synthetic master in a temporary folder."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout  # noqa: E402
import render  # noqa: E402

BRIEF = """# Video brief — 2026-10-18-demo-en-v1

| Trường | Giá trị |
|---|---|
| Hook 0–2s | Xem bảng biến thể bên dưới |

## Biến thể hook

| Biến thể | Hook | Metadata YouTube |
|---|---|---|
| A | Two PINs. Two different vaults. | `youtube-a.toml` |
| B | A fake PIN for nosy people | `youtube-b.toml` |

## Kịch bản
"""

CONFIG = """
creative_id = "2026-10-18-demo-en-v1"
[[variant]]
id = "a"
hook = "Two PINs. Two different vaults."
meta = "youtube-a.toml"
[[variant]]
id = "b"
hook = "A fake PIN for nosy people"
[[text]]
text = "Decoy vault · Veilnest Pro"
start = 1.0
end = 2.5
style = "label"
[end_card]
start = 2.5
title = "Veilnest"
cta = "Search “Veilnest” on the App Store"
"""

META = """
creative_id = "2026-10-18-demo-en-v1-hooka"
[youtube]
title = "Two PINs. Two different vaults. #Shorts"
synthetic_media = false
"""


def creative(text=CONFIG) -> Path:
    root = Path(tempfile.mkdtemp())
    folder = root / "2026-10-18-demo-en-v1"
    folder.mkdir()
    (folder / "render.toml").write_text(text, encoding="utf-8")
    (folder / "BRIEF.md").write_text(BRIEF, encoding="utf-8")
    (folder / "youtube-a.toml").write_text(META, encoding="utf-8")
    return folder


class ConfigTests(unittest.TestCase):
    def test_parses_variants_layers_and_defaults(self):
        config = render.Config.load(creative())
        self.assertEqual([v.id for v in config.variants], ["a", "b"])
        self.assertEqual(config.loudness, -14.0)
        self.assertEqual(config.platforms, ["tiktok", "reels", "shorts"])
        self.assertEqual(config.end_card.title, "Veilnest")
        self.assertTrue(config.output(config.variants[0]).name.endswith("-hooka.mp4"))
        self.assertTrue(config.output(config.variants[0], draft=True).name.endswith("-hooka-draft.mp4"))

    def test_collects_every_error(self):
        bad = 'creative_id = "other"\nloudness = 3\nfit = "zoom"\n[[variant]]\nid = "A!"\n[[text]]\ntext = "x"\nstart = 3\nend = 1\n'
        with self.assertRaises(render.UsageError) as ctx:
            render.Config.load(creative(bad))
        message = str(ctx.exception)
        for fragment in ("khác tên thư mục", "loudness", "fit", "id phải", "thiếu hook", "start < end"):
            self.assertIn(fragment, message)

    def test_loudness_false_disables_normalisation(self):
        config = render.Config.load(creative(CONFIG.replace('creative_id', 'loudness = false\ncreative_id', 1)))
        self.assertIsNone(config.loudness)

    def test_init_reads_hook_table(self):
        folder = creative()
        hooks = render.hooks_from_brief(BRIEF)
        self.assertEqual(hooks[0], ("a", "Two PINs. Two different vaults.", "youtube-a.toml"))
        text = render.init_config(folder)
        self.assertIn('hook = "A fake PIN for nosy people"', text)
        (folder / "render.toml").write_text(text, encoding="utf-8")
        self.assertEqual(len(render.Config.load(folder).variants), 2)

    def test_meta_cross_check(self):
        config = render.Config.load(creative())
        self.assertEqual(render.meta_warnings(config, config.variants[0]), [])
        config.variants[0].hook = "Something else"
        self.assertTrue(any("khác hook" in w for w in render.meta_warnings(config, config.variants[0])))


class SrtTests(unittest.TestCase):
    def test_parses_cues_and_strips_tags(self):
        cues = render.parse_srt("1\n00:00:00,150 --> 00:00:01,550\n<i>Lemme</i> see\n\n2\n00:00:02.1 --> 00:00:03,550\nok\n")
        self.assertEqual(len(cues), 2)
        self.assertAlmostEqual(cues[0].start, 0.15)
        self.assertEqual(cues[0].text, "Lemme see")
        self.assertAlmostEqual(cues[1].start, 2.1)


class LayoutTests(unittest.TestCase):
    zones = list(layout.load_safezones().values())

    def test_breaks_at_sentence_end(self):
        style = layout.style_from("hook")
        lines = layout.render_text("Two PINs. Two different vaults.", style, layout.default_max_width(self.zones)).lines
        self.assertEqual(lines, ["Two PINs.", "Two different vaults."])

    def test_default_positions_are_safe_everywhere(self):
        for position in layout.POSITIONS:
            layer = layout.text_layer("t", "A fake PIN for nosy people", 0, 1, layout.style_from("hook"), position, self.zones)
            self.assertEqual([i for i in layer.issues if "thu nhỏ" not in i], [], position)

    def test_flags_text_under_platform_ui(self):
        layer = layout.text_layer("t", "Too low", 0, 1, layout.style_from("caption"), 0.92, self.zones)
        self.assertTrue(any("TikTok" in i and "dưới" in i for i in layer.issues))

    def test_shrinks_then_refuses_long_text(self):
        style = layout.style_from("hook")
        long = "Your Hidden album opens with your phone passcode and everyone knows it"
        layer = layout.text_layer("t", long, 0, 1, style, "upper", self.zones)
        self.assertLess(layer.size, style.size)
        with self.assertRaises(layout.LayoutError):
            layout.render_text(long * 3, style, 780)

    def test_rejects_emoji(self):
        with self.assertRaises(layout.LayoutError):
            layout.render_text("Two PINs 🔐", layout.style_from("hook"), 780)

    def test_vietnamese_diacritics_stay_inside_the_box(self):
        img = layout.render_text("Album Ẩn trên iPhone", layout.style_from("outline"), 780).image
        top_row_alpha = max(img.getpixel((x, 0))[3] for x in range(img.width))
        self.assertEqual(top_row_alpha, 0)  # nothing clipped at the top edge

    def test_end_card_checks_content_not_background(self):
        layer = layout.end_card_layer(0, 1, self.zones, title="Veilnest", cta="Search “Veilnest” on the App Store")
        self.assertEqual(layer.issues, [])
        self.assertLess(layer.box[3] - layer.box[1], layout.H // 2)


class CommandTests(unittest.TestCase):
    def test_filter_graph(self):
        folder = creative()
        config = render.Config.load(folder)
        info = render.MasterInfo(folder / "m.mov", 1179, 2556, 60.0, 15.0, False, "h264")
        layers = render.build_layers(config, config.variants[0], 15.0)
        pairs = [(l, Path(f"/tmp/{i}.png")) for i, l in enumerate(layers)]
        cmd = render.build_command(config, info, pairs, Path("/tmp/out.mp4"), fps=60, duration=15.0,
                                   loudness=None, draft=False)
        graph = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("gblur", graph)                      # 1179×2556 is not 9:16 → blurred fill
        self.assertIn("anullsrc", " ".join(cmd))           # no audio → silent track
        self.assertIn("-map_metadata", cmd)                # GPS/device metadata dropped
        self.assertEqual(graph.count("overlay=x="), len(layers))
        self.assertIn("between(t,0.000,2.000)", graph)     # hook from the very first frame

    def test_fps_and_fit_choice(self):
        config = render.Config.load(creative())
        vfr = render.MasterInfo(Path("m"), 1080, 1920, 59.2, 10, True, "hevc")
        self.assertEqual(render.output_fps(config, vfr), 60)
        self.assertEqual(render.fit_mode(config, vfr), "scale")


@unittest.skipUnless(shutil.which("ffmpeg"), "cần ffmpeg")
class EndToEndTests(unittest.TestCase):
    def test_render_variant(self):
        folder = creative()
        (folder / "exports").mkdir()
        master = folder / "exports/master.mov"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                        "testsrc2=size=1080x1920:rate=30:duration=3", "-f", "lavfi", "-i",
                        "sine=frequency=330:duration=3,volume=0.1", "-c:v", "libx264", "-preset", "ultrafast",
                        "-c:a", "aac", str(master)], check=True)
        args = Namespace(dirs=[str(folder)], variant=["a"], draft=False, preview=False, force=False, allow_hdr=False)
        self.assertEqual(render.cmd_render(args), 0)
        manifest = json.loads((folder / "exports/render-manifest.json").read_text())
        entry = manifest["2026-10-18-demo-en-v1-hooka.mp4"]
        self.assertEqual((entry["width"], entry["height"], entry["fps"]), (1080, 1920, 30.0))
        self.assertAlmostEqual(entry["integrated_lufs"], -14.0, delta=1.0)
        self.assertEqual(entry["warnings"], [])
        self.assertTrue((folder / "exports/2026-10-18-demo-en-v1-hooka-cover.jpg").is_file())
        # Unchanged inputs → skipped, manifest untouched.
        self.assertEqual(render.cmd_render(args), 0)
        self.assertEqual(json.loads((folder / "exports/render-manifest.json").read_text()), manifest)


if __name__ == "__main__":
    unittest.main()
