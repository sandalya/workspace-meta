#!/bin/bash
set -euo pipefail

# Pi5 Backup System — Main backup script
# Backs up: data/, .env, meta/, PROMPT.md, telethon sessions, .git directories
# Archives: tar.gz in backup/archives/ (rotate 3, PC pulls daily)
# Snapshots: rsync photos to backup/snapshots/photos/ (no rotation)

BASE="/home/sashok/.openclaw/workspace/backup"
WORKSPACE="/home/sashok/.openclaw/workspace"
SNAPSHOT_DIR="$BASE/system-snapshot"
LOG_FILE="$BASE/logs/backup.log"
LOCK_FILE="/tmp/pi5_backup.lock"
BACKUP_DATE=$(date +%Y-%m-%d)
START_TIME=$(date +%s)

# Colors for notify
NOTIFY_OK="✅"
NOTIFY_WARN="⚠️"
NOTIFY_ERR="❌"

send_weekly_summary() {
    ARCHIVE_COUNT=$(find "$BASE/archives" -name "*.tar.gz" -mtime -7 2>/dev/null | wc -l | tr -d ' ')

    WEEKLY_SIZE="0"
    mapfile -t _wfiles < <(find "$BASE/archives" -name "*.tar.gz" -mtime -7 2>/dev/null)
    if [ "${#_wfiles[@]}" -gt 0 ]; then
        WEEKLY_SIZE=$(du -sch "${_wfiles[@]}" 2>/dev/null | tail -1 | cut -f1)
    fi

    SD_USAGE=$(df -h / | awk 'NR==2 {print $5 " (" $3 " / " $2 ")"}')

    # Use OK-entry line numbers as run boundaries (each successful backup writes "OK |")
    BOUNDARY=$(grep -n " OK |" "$LOG_FILE" 2>/dev/null | tail -7 | head -1 | cut -d: -f1 || true)
    if [ -n "$BOUNDARY" ]; then
        ERRORS_WEEK=$(tail -n +"$BOUNDARY" "$LOG_FILE" | grep -c "❌" || true)
    else
        ERRORS_WEEK=$(grep -c "❌" "$LOG_FILE" 2>/dev/null || true)
    fi
    ERRORS_WEEK="${ERRORS_WEEK:-0}"

    WEEKLY_MSG="📊 Pi5 Backup — тижневий звіт
✅ Архіви: $ARCHIVE_COUNT/7 за останні 7 днів
💾 Сумарний розмір: $WEEKLY_SIZE
📈 SD: $SD_USAGE
⚠️ Помилок за тиждень: $ERRORS_WEEK"

    "$BASE/notify.sh" "$WEEKLY_MSG"
}

# Ensure logs directory exists
mkdir -p "$BASE/logs" "$BASE/archives" "$BASE/snapshots/photos"

# Lock: prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
    MSG="$NOTIFY_ERR Backup already running. Lock: $LOCK_FILE"
    echo "[$(date)] $MSG" >> "$LOG_FILE"
    "$BASE/notify.sh" "$MSG"
    exit 1
fi
trap 'rm -f "$LOCK_FILE"' EXIT
touch "$LOCK_FILE"

# Disk space check (warn if <500MB)
AVAIL_KB=$(df "$BASE" | tail -1 | awk '{print $4}')
if [ "$AVAIL_KB" -lt 512000 ]; then
    MSG="$NOTIFY_WARN Low disk space: $((AVAIL_KB / 1024))MB available"
    echo "[$(date)] $MSG" >> "$LOG_FILE"
    "$BASE/notify.sh" "$MSG"
    # Continue anyway
fi

# Build whitelist of files/dirs to backup
WHITELIST=(
    # abby-v2
    "$WORKSPACE/abby-v2/data"
    "$WORKSPACE/abby-v2/.env"
    "$WORKSPACE/abby-v2/.git"
    # household_agent
    "$WORKSPACE/household_agent/data"
    "$WORKSPACE/household_agent/.env"
    "$WORKSPACE/household_agent/memory"
    "$WORKSPACE/household_agent/.git"
    # sam
    "$WORKSPACE/sam/data"
    "$WORKSPACE/sam/.env"
    "$WORKSPACE/sam/.git"
    # insilver-v3
    "$WORKSPACE/insilver-v3/data"
    "$WORKSPACE/insilver-v3/.env"
    "$WORKSPACE/insilver-v3/.git"
    # ed
    "$WORKSPACE/ed/data"
    "$WORKSPACE/ed/.env"
    "$WORKSPACE/ed/.git"
    # garcia
    "$WORKSPACE/garcia/data"
    "$WORKSPACE/garcia/.env"
    "$WORKSPACE/garcia/.git"
    # meta (whole directory)
    "$WORKSPACE/meta"
    # kit (if exists)
    "$WORKSPACE/kit/.env"
    # root workspace
    "$WORKSPACE/.git"
    # Global CLAUDE.md
    "$HOME/.claude/CLAUDE.md"
    # Shell rc files
    "$HOME/.bashrc"
    "$HOME/.bash_aliases"
    # Claude Code settings (allow/deny rules)
    "$HOME/.claude/settings.json"
    # System snapshot (collected below)
    "$SNAPSHOT_DIR"
)

# Add all meta/ HOT/WARM/COLD/PROMPT.md files
for dir in "$WORKSPACE"/{abby-v2,household_agent,sam,insilver-v3,ed,garcia}; do
    if [ -d "$dir/meta" ]; then
        WHITELIST+=("$dir/meta/HOT.md" "$dir/meta/WARM.md" "$dir/meta/COLD.md")
    fi
    if [ -f "$dir/PROMPT.md" ]; then
        WHITELIST+=("$dir/PROMPT.md")
    fi
done

# Find and add telethon *.session files
while IFS= read -r session_file; do
    WHITELIST+=("$session_file")
done < <(find "$WORKSPACE" -name "*.session" 2>/dev/null || true)

# System snapshot — collect infra state needed for full DR recovery
# Must run BEFORE EXISTING_PATHS filter so $SNAPSHOT_DIR exists when checked
mkdir -p "$SNAPSHOT_DIR"
echo "[$(date)] Collecting system snapshot..." >> "$LOG_FILE"
cp /etc/systemd/system/*.service "$SNAPSHOT_DIR/" 2>/dev/null || true
cp /etc/systemd/system/*.timer   "$SNAPSHOT_DIR/" 2>/dev/null || true
crontab -l > "$SNAPSHOT_DIR/crontab.txt" 2>/dev/null || echo "# no crontab" > "$SNAPSHOT_DIR/crontab.txt"
dpkg --get-selections > "$SNAPSHOT_DIR/packages.txt" 2>/dev/null || true
pip3 freeze > "$SNAPSHOT_DIR/pip_global.txt" 2>/dev/null || true
echo "[$(date)] System snapshot: $(ls "$SNAPSHOT_DIR" | wc -l) files" >> "$LOG_FILE"

# Filter whitelist: skip paths that don't exist
EXISTING_PATHS=()
for path in "${WHITELIST[@]}"; do
    if [ -e "$path" ]; then
        EXISTING_PATHS+=("$path")
    else
        echo "[$(date)] SKIP (not found): $path" >> "$LOG_FILE"
    fi
done

# Create tar archive
ARCHIVE="$BASE/archives/$BACKUP_DATE.tar.gz"
echo "[$(date)] Starting tar archive: $ARCHIVE" >> "$LOG_FILE"

TAR_EXIT=0
tar --exclude-from="$BASE/exclude.txt" -czf "$ARCHIVE" "${EXISTING_PATHS[@]}" 2>>"$LOG_FILE" || TAR_EXIT=$?
if [ $TAR_EXIT -gt 1 ]; then
    # exit 0 = success, exit 1 = warnings (OK), exit 2+ = real error
    MSG="$NOTIFY_ERR Tar failed (exit $TAR_EXIT)"
    echo "[$(date)] $MSG" >> "$LOG_FILE"
    "$BASE/notify.sh" "$MSG"
    exit 1
fi

if [ ! -f "$ARCHIVE" ]; then
    MSG="$NOTIFY_ERR Tar archive not created"
    echo "[$(date)] $MSG" >> "$LOG_FILE"
    "$BASE/notify.sh" "$MSG"
    exit 1
fi

ARCHIVE_SIZE=$(du -h "$ARCHIVE" | cut -f1)
echo "[$(date)] Archive created: $ARCHIVE_SIZE" >> "$LOG_FILE"

# Verify tar integrity
if ! tar -tzf "$ARCHIVE" > /dev/null 2>&1; then
    MSG="$NOTIFY_ERR Tar integrity check failed"
    echo "[$(date)] $MSG" >> "$LOG_FILE"
    "$BASE/notify.sh" "$MSG"
    exit 1
fi
echo "[$(date)] Tar integrity verified" >> "$LOG_FILE"

# Rsync photos snapshot (no --delete to protect source)
echo "[$(date)] Starting rsync for photos..." >> "$LOG_FILE"
rsync_output=$(rsync -a --stats "$WORKSPACE/insilver-v3/data/photos/" "$BASE/snapshots/photos/" 2>&1 || true)
NEW_PHOTOS=$(echo "$rsync_output" | grep -oP "Number of regular files transferred: \K[0-9]+" || echo "0")
echo "[$(date)] Rsync completed: $NEW_PHOTOS new files" >> "$LOG_FILE"

# Rotate old archives (keep 3 days)
ARCHIVES_TO_DELETE=$(ls -1t "$BASE/archives"/*.tar.gz 2>/dev/null | tail -n +4 || true)
if [ -n "$ARCHIVES_TO_DELETE" ]; then
    echo "$ARCHIVES_TO_DELETE" | xargs rm -f
    echo "[$(date)] Rotated old archives (kept 3)" >> "$LOG_FILE"
fi

# Rotate log if >10MB
LOG_SIZE=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
if [ "$LOG_SIZE" -gt 10485760 ]; then
    mv "$LOG_FILE" "$LOG_FILE.old"
    echo "[$(date)] Log rotated" > "$LOG_FILE"
fi

# Calculate duration
DURATION=$(($(date +%s) - START_TIME))

# Log success
LOG_MSG="[$BACKUP_DATE] OK | archive=$ARCHIVE_SIZE | new_photos=$NEW_PHOTOS | ${DURATION}s"
echo "$LOG_MSG" >> "$LOG_FILE"

# Weekly summary on Sundays
if [ "$(date +%u)" = "7" ]; then
    send_weekly_summary
fi

exit 0
