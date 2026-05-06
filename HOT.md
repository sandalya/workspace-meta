---
project: meta
updated: 2026-05-06
---

# HOT — meta

## Now

Off-device backup chain completed: PC pulls 14d daily via Task Scheduler with SSH key auth and throttle; Pi rotation changed from 7 to 3 days; backup/ converted to git repo (sandalya/pi5-backup) and pushed to GitHub.

## Last done

- Configured PC backup pull script (H:\pi_backups\pull-pi-backups.ps1) with 14-day retention and 20-hour throttle
- Set up SSH key auth (\~/.ssh/pi5_backup) for secure automated pulls
- Rotated Pi backup retention from 7 days → 3 days, removed daily-notify, kept weekly summary (Sundays 03:00)
- Verified end-to-end: 7 archives synced, md5 match confirmed, Task Scheduler launches at logon+2min
- Freed SD card space: 78% → 70%
- Created backup/ git repo with backup.sh, notify.sh, README.md, exclude.txt, .gitignore, .env.example
- Pushed to github.com/sandalya/pi5-backup

## Next

DR drill on spare SD when arrives. Extend backup.sh to include /etc/systemd/system, ~/.claude/settings.json, crontab, dpkg list.

## Blockers

None.

## Active branches

- Backup chain: PC pull (14d) + Pi rotation (3d) — complete
- GitHub repo sandalya/pi5-backup — live
- DR drill — pending spare SD arrival

## Open questions

- Which additional system files should backup.sh capture for full disaster recovery (systemd user services, settings, package list)?
- How to automate dpkg list export for quick rebuild on new OS?

## Reminders

- Backup chain now fully automated: no manual intervention needed
- Telegram alerts only on error (removed daily noise)
- Weekly summary Sundays 03:00 (check logs via systemctl status weekly-notify.timer)
- Spare SD arrival expected soon — schedule DR drill when ready
