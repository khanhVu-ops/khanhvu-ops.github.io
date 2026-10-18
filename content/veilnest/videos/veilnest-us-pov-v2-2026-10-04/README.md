# Veilnest — Financially responsible / V2

> Nhập vào Studio Hub ngày 18/10/2026. Đây là tài liệu sản xuất ngày 04/10, chưa phải bản quảng cáo final. Trạng thái hiện tại: [chỉ mục Veilnest](../../README.md). ZIP handoff trùng lặp chỉ có tại máy nguồn và không được track trong Git. Các đường dẫn source Swift dưới đây thuộc repo IOS-Vault.

Revision prepared October 4, 2026 for a 15-second English-language US TikTok / Reels creative.

## What changed
The conversation now has clear prop continuity: **owner → friend → owner**. Friend's line responds to the calculator he actually receives. “Then pay me back” immediately answers “I'm financially responsible” while he returns the phone. The owner unlocks the vault only after friend turns away. The UI remains in the same room instead of switching to a detached demo background. Branding follows the completed story.

## Review
- preview.mp4: 15-second 1080 × 1920 / 30 fps animatic, not a finished actor video.
- storyboard.html: shot board and playable beat links.
- SCRIPT.md: locked timeline, dialogue, camera and sound continuity.
- VIDEO_PROMPTS.md: preferred continuous actor scene and split fallback with explicit phone ownership.
- captions.srt: English dialogue timing for the preview.
- assets/: three AI continuity stills, recreated UI, review frames, actual brand icon.
- render_preview.py: reproduction with Pillow + ffmpeg.
- serve_preview.py: run python3 serve_preview.py --port 8767, then open http://127.0.0.1:8767/storyboard.html.
- production-pack.zip: complete handoff.

The preview marks handovers with separate AI stills and pans/zooms; it cannot show actual hand movement or facial speech. Review annotations are not final ad copy. Vault thumbnails are abstract placeholders. Actor motion, synchronized speech and final photo thumbnails still need completion.

## Actual product flow
Calculator cover is already active in a locked session. Hold Calculator title for 1.5 seconds → separate lock screen → PIN → private vault. Calculator digits are arithmetic; they do not authenticate a PIN. The edit does not promise automatic calculator launch.
Evidence: Features/Camouflage/CamouflageCoverView.swift (calculatorHeader hold), CamouflageCoverViewModel.swift (digit and exitRequested), App/Session/PrivacyLifecycleCoordinator.swift (cover removal), App/iOSVault.swift (lock-screen presentation).
UI is a simplified reconstruction, not an app change.

## Generation
Reference image generation is available. The discovered Weave connection needs reauthentication. No paid video-model run or Weave credit spend has occurred. Quote and obtain structured approval for each paid run once restored.

Proposed post caption: “Some photos are just for you. Veilnest for iOS.”
No performance or virality claims have been tested.
