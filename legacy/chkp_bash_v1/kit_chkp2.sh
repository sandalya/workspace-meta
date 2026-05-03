#!/bin/bash
# chkp2 — checkpoint з триярусною пам'яттю (HOT / WARM / COLD)
#
# Експериментальна версія, поки тільки для Sam.
# Після валідації (тиждень-два) — замінить chkp.
#
# Використання:
#   chkp2 sam "що зробили" "наступний крок" "контекст"
#
# Відмінність від chkp:
#   - Перевіряє що HOT.md / WARM.md / MEMORY.md існують
#   - Нагадує виконати ритуал трьох файлів ПЕРЕД комітом
#   - Коментар коміту містить посилання на HOT.md

set -e

PROJECT="$1"
WHAT_DONE="$2"
NEXT_STEP="$3"
CONTEXT="$4"

WORKSPACE="/home/sashok/.openclaw/workspace"

# --- Guards ---

if [ -z "$PROJECT" ] || [ -z "$WHAT_DONE" ] || [ -z "$NEXT_STEP" ] || [ -z "$CONTEXT" ]; then
    echo "Usage: chkp2 <project> \"<what done>\" \"<next step>\" \"<context>\""
    echo ""
    echo "Example:"
    echo "  chkp2 sam \"Renderer v2 — counters added\" \"Build keyboard stub\" \"Phase 2 pinned\""
    exit 1
fi

if [ "$PROJECT" != "sam" ]; then
    echo "❌ chkp2 is experimental — currently supports only 'sam'."
    echo "   For other projects use classic 'chkp'."
    echo ""
    echo "   If you want to migrate $PROJECT to three-tier memory,"
    echo "   start a session: create $WORKSPACE/$PROJECT/{HOT,WARM,COLD,MEMORY}.md"
    exit 2
fi

PROJECT_DIR="$WORKSPACE/$PROJECT"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project dir not found: $PROJECT_DIR"
    exit 3
fi

# --- Check three-tier files exist ---

MISSING=()
for f in HOT.md WARM.md COLD.md MEMORY.md; do
    if [ ! -f "$PROJECT_DIR/$f" ]; then
        MISSING+=("$f")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "❌ Missing three-tier files in $PROJECT_DIR:"
    for f in "${MISSING[@]}"; do
        echo "   - $f"
    done
    echo ""
    echo "   Create them first, then run chkp2 again."
    exit 4
fi

# --- Ritual reminder ---

echo "================================================"
echo "  chkp2 — three-tier memory ritual for $PROJECT"
echo "================================================"
echo ""
echo "Before commit, Claude should have done:"
echo "  [1] Rewritten HOT.md (Now / Last done / Next / Blockers)"
echo "  [2] Reviewed WARM.md — updated last_touched on changed blocks,"
echo "      added new blocks if needed, moved cooled blocks to COLD"
echo "  [3] Appended to COLD.md if any block was archived"
echo ""
echo "Current state:"
echo "  HOT.md  : $(wc -l < "$PROJECT_DIR/HOT.md") lines"
echo "  WARM.md : $(wc -l < "$PROJECT_DIR/WARM.md") lines"
echo "  COLD.md : $(wc -l < "$PROJECT_DIR/COLD.md") lines"
echo ""

# --- Git commit + push ---

cd "$PROJECT_DIR"

# Find git root (project dir or parent)
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    cd "$WORKSPACE"
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ No git repo found in $PROJECT_DIR or $WORKSPACE"
        exit 6
    fi
fi

git add -A

COMMIT_MSG="chkp2($PROJECT): $WHAT_DONE

Next: $NEXT_STEP
Context: $CONTEXT

See $PROJECT/HOT.md for current state."

git commit -m "$COMMIT_MSG" || {
    echo "⚠️  Nothing to commit (working tree clean?)"
    exit 0
}

git push

echo ""
echo "✅ chkp2 done."
echo "   Commit: $(git rev-parse --short HEAD)"
echo "   Next session: read $PROJECT/HOT.md + $PROJECT/WARM.md first."
