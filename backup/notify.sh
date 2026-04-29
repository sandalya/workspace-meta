#!/bin/bash
set -u

# Telegram notification helper for Pi5 Backup System
# Usage: ./notify.sh "Message text"
# .env must have TELEGRAM_TOKEN and OWNER_CHAT_ID

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "[$(date)] ERROR: .env not found at $ENV_FILE" >> "$SCRIPT_DIR/logs/backup.log"
    exit 0  # Don't break backup, just warn
fi

# Read values safely without executing .env
TELEGRAM_TOKEN=$(grep '^TELEGRAM_TOKEN=' "$ENV_FILE" | cut -d= -f2-)
OWNER_CHAT_ID=$(grep '^OWNER_CHAT_ID=' "$ENV_FILE" | cut -d= -f2-)

if [ -z "$TELEGRAM_TOKEN" ] || [ -z "$OWNER_CHAT_ID" ]; then
    echo "[$(date)] ERROR: TELEGRAM_TOKEN or OWNER_CHAT_ID not set in .env" >> "$SCRIPT_DIR/logs/backup.log"
    exit 0
fi

MESSAGE="$1"

# Send to Telegram (10s timeout, silent on fail)
HTTP_CODE=$(curl -s --max-time 10 -w "%{http_code}" -o /dev/null -X POST \
    "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="$OWNER_CHAT_ID" \
    -d text="$MESSAGE" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" != "200" ]; then
    echo "[$(date)] WARNING: Telegram notification failed (HTTP $HTTP_CODE): $MESSAGE" >> "$SCRIPT_DIR/logs/backup.log"
fi

# Always exit 0 to not break backup pipeline
exit 0
