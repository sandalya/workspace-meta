---
project: meta
updated: 2026-05-06
---

# HOT — meta

## Now

Httpx INFO suppression: patched abby-v2 main.py and ed/bot.py with logging.getLogger('httpx').setLevel(WARNING). Rotated abby-v2 and ed-bot tokens via BotFather. Vacuumed journalctl: 834M→16M, eliminated 105k token leaks.

## Last done

- Patched abby-v2 main.py: added `logging.getLogger('httpx').setLevel(logging.WARNING)` to suppress INFO/DEBUG output
- Patched ed/bot.py: same httpx logging suppression
- Rotated abby-v2 Telegram bot token via BotFather (old token revoked)
- Rotated ed-bot Telegram bot token via BotFather (old token revoked)
- Vacuumed journalctl on Pi5: freed 834M→16M, removed 105k+ token leak entries
- Verified abby-v2 and ed-bot still functional after token rotation
- Discovered 4 of 6 bots leak Telegram tokens via httpx INFO: abby-v2 (30k), ed-bot (60k), household_agent (28k) per 7 days; garcia/sam clean (use shared/logger module)

## Next

Continue with chkp.py silent skip on next session: fail loud on unknown BACKLOG section. Estimated 30-45 min. Then extend backup.sh to capture /etc/systemd/system, ~/.claude/settings.json, crontab, dpkg list export for faster DR rebuild.

## Blockers

None.

## Active branches

- Backup chain: PC pull (14d retention to H:\pi_backups) + Pi rotation (3d) — complete, automated
- sandalya/pi5-backup GitHub repo — live with backup.sh, notify.sh, exclude.txt, README.md
- DR drill — pending spare SD arrival
- Logging security: httpx token leak in journalctl suppressed on abby-v2, ed-bot; garcia/sam already clean; household_agent, insilver-v3 remain to patch

## Open questions

- How to audit remaining 2 bots (household_agent, insilver-v3) for httpx token leaks — do they use direct httpx or shared logger?
- Which additional system files should backup.sh capture: user-level systemd services (~/.config/systemd/user/), crontab, dpkg list, git config?
- Backlog: abby images (759M, 1315 files) + sam audio (827M, 26 mp3 podcasts) — rotation policy decision deferred.

## Reminders

- Backup chain fully automated: PC pulls daily with 14d retention, Pi keeps 3d local, Telegram alerts on error only
- httpx library logs Telegram tokens in journalctl at INFO level — patched abby-v2, ed-bot; verify garcia/sam/household_agent/insilver-v3 compliance
- Spare SD arrival expected soon — DR drill critical for validating full restore procedure
- meggi venv now CPU-only (no nvidia/triton): 497M, faster-whisper verified working
- .u2net consolidated to isnet-general-use.onnx (171M) for rembg; 2 unused models removed
