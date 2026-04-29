#!/bin/bash
set -euo pipefail

# Pi5 Backup System — Main backup script
# Backs up: data/, .env, meta/, PROMPT.md, telethon sessions, .git directories
# Archives: tar.gz in backup/archives/ (rotate 7)
# Snapshots: rsync photos to backup/snapshots/photos/ (no rotation)

BASE="/home/sashok/.openclaw/workspace/backup"
WORKSPACE="/home/sashok/.openclaw/workspace"
LOG_FILE="$BASE/logs/backup.log"
LOCK_FILE="/tmp/pi5_backup.lock"
BACKUP_DATE=$(date +%Y-%m-%d)
START_TIME=$(date +%s)

# Colors for notify
NOTIFY_OK="✅"
NOTIFY_WARN="⚠️"
NOTIFY_ERR="❌"

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

# Rotate old archives (keep 7 days)
ARCHIVES_TO_DELETE=$(ls -1t "$BASE/archives"/*.tar.gz 2>/dev/null | tail -n +8 || true)
if [ -n "$ARCHIVES_TO_DELETE" ]; then
    echo "$ARCHIVES_TO_DELETE" | xargs rm -f
    echo "[$(date)] Rotated old archives (kept 7)" >> "$LOG_FILE"
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

# Notify success
NOTIFY_MSG="$NOTIFY_OK Pi5 backup OK
Date: $BACKUP_DATE
Archive: $ARCHIVE_SIZE
New photos: $NEW_PHOTOS
Duration: ${DURATION}s"
"$BASE/notify.sh" "$NOTIFY_MSG"

exit 0
