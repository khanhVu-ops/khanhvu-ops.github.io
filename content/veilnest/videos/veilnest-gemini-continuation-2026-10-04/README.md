# Veilnest — continuation kit for the supplied Gemini video

> Nhập vào Studio Hub ngày 18/10/2026. Đây là tài liệu sản xuất ngày 04/10, chưa phải bản quảng cáo final. Trạng thái hiện tại: [chỉ mục Veilnest](../../README.md). ZIP handoff trùng lặp chỉ có tại máy nguồn và không được track trong Git. Các đường dẫn source Swift dưới đây thuộc repo IOS-Vault.

Prepared from `gemini_generated_video_38e8ea4b.mp4` (original supplied separately; not included in this repository) (10.005 seconds, 720×1280, 24 fps, AAC audio). The original is unchanged. Visual inspection found the opening conversation and phone return, followed by a very brief calculator, PIN, and end card; there is no readable photo-vault reveal. Spoken words have not been independently transcribed, so keep the original dialogue rather than replacing it with an assumed transcript.

## Recommended edit: about 18 seconds

Reuse the existing opening rather than asking the model to repeat the joke. The hard cut to the original floating phone begins at source frame 167 (6.958 seconds). Keep the preceding 167 frames, ending on the owner holding her phone, then replace the rushed source ending.

| Final time | Picture | Purpose |
|---|---|---|
| 0–6.958s | Supplied video opening, original speech and handover | Setup, joke, owner receives phone |
| 6.958–7.958s | New clip B: over-shoulder calculator | Viewer recognizes the disguise |
| 7.958–9.458s | Hold Calculator title for 1.5s | Show the real cover-exit gesture |
| 9.458–11.458s | Separate PIN screen, six masked taps | Explain private access |
| 11.458–14.958s | Vault PHOTOGRAPHS held for 3.5s | Explain the app's actual benefit |
| 14.958–17.958s | Existing Veilnest icon, product line, CTA | Brand recall and next step |

This is a recommended cut, not a request to stretch 10 seconds to 18 with slow motion. Clip B is newly generated motion. Its first 0.5s and last 1.5s are handles; retain B 0.5–8.5s. The final output is 431 frames at 24 fps (~17.958s). Continuity means coherent action and a motivated camera cut; it does not require a physically implausible camera orbit or a dissolve between two different phone positions.

## Generate clip B in Gemini

1. Use a new video-generation request. Attach `clip-a-keep-0-6.96s.mp4` as prior scene context, plus these FOUR images from `assets/`: `over-shoulder-reference.png`, `screen-calculator.png`, `screen-pin.png`, `screen-vault.png`.
2. Paste all of `GEMINI_PROMPT.txt`. Request ONLY the next ten seconds; do not regenerate the opening or the end card.
3. If your interface does not accept the video, attach these FIVE images instead: `clip-a-last-frame.png`, `over-shoulder-reference.png`, `screen-calculator.png`, `screen-pin.png`, `screen-vault.png`, then use `GEMINI_IMAGE_ONLY_PROMPT.txt`.
4. The screen references are controlled marketing reconstructions, not screenshots of the installed app. The six album photographs are AI-created fictional demo media. Replace the screens with actual app captures before claiming pixel-exact product footage. The interaction is based on current app behavior: long press the Calculator TITLE, then a separate PIN screen when the vault session is locked. The calculator itself does not authenticate typed PIN digits.
5. Review clip B: same owner/phone/room, hands physically plausible, long press in the correct place, all six dots, and at least 3.5 seconds of recognizable photos. If Gemini shifts these timings, adjust the trim to preserve these beats; do not blindly cut off the reveal.
6. If text/buttons distort, use `CONTROLLED_SCREEN_PROMPT.txt` to generate a blank-screen plate. Track and composite `screen-demo-8s.mp4` onto the phone, masking the finger in front. The supplied assembly script concatenates completed clips; it does not track or replace the phone screen automatically.

## Assets provided

| Asset | Role |
|---|---|
| `clip-a-keep-0-6.96s.mp4` | Ready trimmed original opening, with audio |
| `assets/clip-a-last-frame.png` | Exact retained last frame at 6.9167s; pose continuity |
| `assets/identity-room-reference.png` | Extracted people, wardrobe, room reference |
| `assets/over-shoulder-reference.png` | New AI camera/hand/phone reference; its screen is intentionally blank |
| `assets/screen-calculator.png` | Flat, correctly typeset cover-screen reference |
| `assets/screen-pin.png` | Separate PIN-screen reference; six empty dots |
| `assets/screen-vault.png` | Vault-grid reference with six AI demo photos |
| `assets/demo-photo-sheet.png` | Six fictional personal-memory photos, same character identities |
| `screen-demo-8s.mp4` | Clean screen animation for optional manual phone compositing: 1.5s calculator, 2s PIN, 4.5s vault. Trim its last second if placing after B's 1s calculator establishment |
| `assets/veilnest-icon.png` | Existing project icon, copied from the prior production kit |
| `assets/end-card.png`, `clip-c-end-card-3s.mp4` | Ready brand ending; typography is software-rendered |
| `continuation-captions.srt` | English captions for the new product explanation; no invented transcript for the original dialogue |
| `assemble.py` | Local final assembly once clip B exists |

Generated bitmap references used the built-in image generation tool. UI and typography are drawn as new graphics; FFmpeg composites the photo sheet and existing icon. Reference prompts are saved in `IMAGE_PROMPTS.md`. No new AI motion video has been generated by this kit.

## Assemble after downloading B

```bash
# From this creative directory (Python 3, FFmpeg and ffprobe required)
python3 assemble.py --continuation /absolute/path/to/new-gemini-video.mp4
```

The imported script expects FFmpeg/ffprobe at `/opt/homebrew/bin/`, and the render helpers use macOS fonts. These dependencies have not been revalidated during the import.

Default B trim is 0.5–8.5s. Override `--start` if the generated action shifts. Output: `veilnest-18s.mp4`, 720×1280 at 24 fps; preserve the source's actual resolution. The script retains opening speech, keeps B audio if present, and adds the 3s ending. Import the SRT for explanation overlays. Carry B ambience under the end card and fade it in your editor if desired. The original opening's visible Gemini mark is retained.

No paid video run, account upload, or publishing is performed. The deliverable is a ready prompt/asset kit for producing B, not a finished new motion sequence.
