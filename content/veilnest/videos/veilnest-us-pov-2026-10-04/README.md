# Veilnest — “Financially responsible”

> Nhập vào Studio Hub ngày 18/10/2026. Đây là tài liệu sản xuất ngày 04/10, chưa phải bản quảng cáo final. Trạng thái hiện tại: [chỉ mục Veilnest](../../README.md). ZIP handoff trùng lặp chỉ có tại máy nguồn và không được track trong Git. Các đường dẫn source Swift dưới đây thuộc repo IOS-Vault.

Production preparation for a 15-second English-language US TikTok / Reels comedy ad. October 4, 2026.

## Review files
- preview.mp4: 15-second vertical **animatic** using AI reference imagery, animated reconstructed UI, captions, and original synthesized timing sounds. This is a pacing preview, not the final moving-actor ad. Spoken dialogue is not included yet.
- storyboard.html: visual shot board, local video player, dialogue, and production notes.
- SCRIPT.md: exact English dialogue, timing, editing instructions, and three opening hooks.
- VIDEO_PROMPTS.md: character continuity, actor clip prompts, voice direction, and assembly instructions.
- captions.srt: English dialogue subtitles. Re-time against generated speech for the final cut.
- assets/: AI reference image, reconstructed UI, and existing brand icon.
- render_preview.py: reproducible renderer; requires Pillow, ffmpeg, and ffprobe.
- serve_preview.py: local server with MP4 byte-range support for shot seeking. Run `python3 serve_preview.py` from this directory and open `http://127.0.0.1:8766/storyboard.html`.

## Product behavior checked locally
The initial conversation described entering a secret PIN directly into the calculator. **The checked-out code does not implement that behavior.** Calculator digit presses perform arithmetic; they do not authenticate a PIN.

The product supports a functioning calculator cover. A **1.5-second hold on the “Calculator” title** exits the cover. In the locked-vault case, the app then presents the separate Veilnest lock screen; entering the PIN there unlocks the vault. This demo assumes a locked session and calculator cover already active. It does not imply every app launch opens a calculator.

Local evidence:
- Features/Camouflage/CamouflageCoverView.swift: calculatorHeader has onLongPressGesture(minimumDuration: 1.5, perform: onExit).
- Features/Camouflage/CamouflageCoverViewModel.swift: digit updates the arithmetic display; exitRequested invokes onExit.
- App/Session/PrivacyLifecycleCoordinator.swift: camouflageExitRequested clears active cover.
- App/iOSVault.swift: coverContent presents LockScreenView for an initialized locked vault after cover removal.

Production uses **hold title → separate lock-screen PIN → private vault**. The UI is a simplified reconstruction informed by the local app and its English reference images; this pack does not change the app.

## Generation status
AI image generation is available. Moving-actor generation through the discovered Weave connection returns UNAUTHORIZED / reauthentication required. No video-model run was started and no Weave credit spend was performed. Once restored, quote each concrete run; Weave requires explicit structured cost approval for every paid run.

## Production defaults
1080 × 1920, 9:16, 30 fps, exactly 15.0 seconds. Two fictional adults, casual American apartment, natural US English, dry friendly humor. Interface and subtitles are composited separately. Final dialogue and overlays are English.

The final ad still needs AI actor motion, synchronized spoken audio, and finished demo thumbnails before publishing. Preview thumbnails are abstract placeholders. It uses no physical filming or simulator recording.

Proposed caption: **“Finally, a calculator I actually use. 👀 Veilnest for iOS.”**

This is an original creative concept; virality and conversion are untested. No external marketing research or platform-performance claims are used.
