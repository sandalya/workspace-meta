---
project: meta
updated: 2026-05-06
---

# HOT — meta

## Now

Implemented chkp.py validate_backlog_flags() pre-flight check: fail loud with exit 2 and fuzzy hints (difflib.get_close_matches) when --backlog-strike or --backlog-add cannot match BACKLOG.md. Validates before Haiku call, preventing wasted API tokens. 26/26 pytest PASS (19 old + 7 new).

## Last done

- validate_backlog_flags() pre-flight check added to chkp.py
- _check_backlog_match() helper implemented (single source of truth for strike/add validation)
- difflib.get_close_matches fuzzy matching: top 3 results, cutoff 0.4
- Catches mismatched BACKLOG headers before API call (no token waste)
- 7 new unit tests added (26/26 PASS total)
- Manual smoke test confirmed: yesterday's silent skip bug (commit 3e67fa5+00defa1) now caught with correct fuzzy hint

## Next

Backup.sh extension: capture /etc/systemd/system, ~/.claude/settings.json, crontab, dpkg list export (~30 min). Then DR drill (blocked on spare SD arrival).

## Blockers

None.

## Active branches

- Backup chain: PC pull (14d retention to H:\pi_backups) + Pi rotation (3d) — complete, automated
- sandalya/pi5-backup GitHub repo — live with backup.sh, notify.sh, exclude.txt, README.md
- DR drill — pending spare SD arrival
- Logging security: httpx token leak in journalctl suppressed on abby-v2, ed-bot; garcia/sam already clean; household_agent, insilver-v3 remain to patch
- chkp.py backlog validation — pre-flight check live, ready for production

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
- chkp.py backlog validation prevents silent failures: fail loud with fuzzy hints before wasting tokens
