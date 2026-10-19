# KV Apps studio repository

- `website/` is the entire GitHub Pages artifact. Keep existing root public URLs stable, especially legal pages and `app-ads.txt`. Never deploy the repository root.
- `docs/social/ACCOUNTS.md` is the source of truth for account ownership, verified URLs and setup status. Never invent account completion, reserved handles, publications or performance metrics.
- Store app creative masters under `content/<app>/videos/<creative-id>/`. Channel logs link to masters rather than duplicating media. Maintain app indexes and the content calendar when adding creatives.
- This is a public repository. Do not commit credentials, recovery codes, dates of birth, private analytics exports or account-registration screenshots.
- Imported October 2026 Veilnest packs are production references, not finished ads. Preserve their status and provenance; original IOS-Vault copies were left intact. Duplicate ZIPs and the duplicate `continuation-kit/` folder are local-only and gitignored.
- Before publishing website changes, run `python3 tools/check-site.py`, inspect the diff and verify the Pages deployment. Update `docs/website/README.md` if paths or deployment behavior change.
- `tools/youtube/upload.py` uploads private by default. Never run it without the owner asking for that specific upload, never make a video public or scheduled on their behalf, and never commit `.env`, `.secrets/` or tokens.
- The dashboard App Store page (`tools/dashboard/appstore.py`) writes to App Store Connect only after the owner reviews the planned operations and confirms. Never run its apply functions or call the ASC API with write methods on your own, never submit for review, change prices or release, and never commit `.secrets/appstore/` or the `ASC_*` values.
- Documentation is Vietnamese; public website copy is English. This repo is plain static HTML and does not use the iOS architecture/build workflow.
