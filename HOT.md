---
project: meta
updated: 2026-05-06
---

# HOT — meta

## Now

SD card cleanup completed: freed ~11G (78%→60%), rebuilt meggi venv from 3.0G→497M on CPU-only PyTorch. Rotated leaked Telegram token via BotFather after it appeared in journalctl httpx logs.

## Last done

- SD card space optimization: pip cache (3G), npm cache (1.8G), unused .u2net models (1.1G) removed
- meggi venv rebuild without nvidia/triton deps, verified faster-whisper CPU-only still works
- Telegram token rotation via BotFather (token found in journalctl URL logging via httpx)
- requirements.txt added to household_agent/ for reproducibility
- .u2net trimmed to isnet-general-use.onnx (171M, used by abby-v2 rembg)

## Next

DR drill on spare SD when arrives. Extend backup.sh to capture /etc/systemd/system, ~/.claude/settings.json, crontab, dpkg list for faster rebuilds. Suppress httpx INFO logging across all bots to prevent future token leaks.

## Blockers

None.

## Active branches

- Backup chain: PC pull (14d to H:\pi_backups) + Pi rotation (3d) — complete, automated
- sandalya/pi5-backup GitHub repo — live with backup.sh, notify.sh, exclude.txt
- DR drill — pending spare SD arrival
- Logging security: httpx token leak in journalctl needs suppression across all bots

## Open questions

- Which additional system files should backup.sh capture for full disaster recovery (systemd user services, settings, package list)?
- How to automate dpkg list export + systemd service list for quick rebuild on new OS?
- Backlog: abby images (759M, 1315 files) + sam audio (827M, 26 mp3 podcasts) — rotation policy decision deferred to next session

## Reminders

- Backup chain fully automated: no manual intervention needed
- Telegram alerts only on error (removed daily-notify noise, weekly summary Sundays 03:00)
- httpx library logging Telegram tokens in journalctl — suppress INFO level across all bots
- Spare SD arrival expected soon — DR drill critical for validating restore procedure
- meggi venv now CPU-only (no nvidia/triton): 497M, faster-whisper verified working
- .u2net consolidation: kept only isnet-general-use.onnx (171M), removed 2 unused models
