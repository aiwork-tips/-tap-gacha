# Tap Gacha hosting migration checklist (development note)

Status: PLAN ONLY; no production changes.

Current hosting: GitHub Pages, https://aiwork-tips.github.io/-tap-gacha/
Target: future custom domain or alternate static hosting, to be chosen.

## RC02 code audit
- HTML/CSS/JS/assets are static files and can be deployed to other static hosting.
- JS script-01.js uses localStorage with SAVE_KEY and legacy keys tapgacha_pt, tapgacha_power, tapgacha_collection, gV2.
- SAVE_KEY's concrete value and migration/export schema must be reviewed before implementation.
- Browsers isolate localStorage by origin; changing domains does NOT automatically transfer saves.

## Required before public migration
1. Finish RC02 asset migration and run functional regression tests.
2. Preserve save keys and add tested JSON export/import, with version and schema validation.
3. Ensure all asset URLs are relative and avoid GitHub-specific hardcoded paths.
4. Deploy candidate to a staging domain and test on iPhone Safari.
5. Verify new-domain import, old-domain export, and failure/rollback cases.
6. Keep old site accessible during transition and provide clear save-transfer instructions.

No merge to main until tests pass.
