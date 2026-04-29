# Pi5 Backup System

Daily local backup of openclaw workspace to disk.

## Structure

- `backup.sh` — main script, runs daily at 03:00
- `notify.sh` — Telegram notifier helper
- `.env` — secrets (create from `.env.example`)
- `exclude.txt` — tar exclusion patterns
- `archives/` — daily tar.gz files (keep 7 days)
- `snapshots/photos/` — rsync mirror of insilver photos
- `logs/backup.log` — execution history

## What's backed up

**tar archives:**
- `data/` folders from all active bots
- `.env` files
- `.git/` directories (git history)
- `meta/` full directory (chkp.py, notes)
- `PROMPT.md` and tripartite memory files (HOT/WARM/COLD)
- telethon `*.session` files
- global `~/.claude/CLAUDE.md`, `~/.bashrc`

**rsync snapshots (no rotation):**
- `insilver-v3/data/photos/` (without --delete to prevent accidents)

## Manual run

```bash
cd ~/.openclaw/workspace/backup
./backup.sh
```

## Systemd

```bash
sudo systemctl status pi5-backup.timer
sudo systemctl list-timers | grep pi5
```

## Restore

```bash
# Extract tar
tar -xzf archives/2026-04-28.tar.gz -C /tmp/restore/

# Copy photos
cp -r snapshots/photos/ /target/
```

## Setup

1. Copy `.env.example` to `.env`
2. Add TELEGRAM_TOKEN and OWNER_CHAT_ID to `.env`
3. Install systemd timer (see main docs)
