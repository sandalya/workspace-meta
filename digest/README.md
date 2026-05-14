# morning_digest

Daily BACKLOG.md digest delivered to Telegram at 09:00 via Sam bot.

**Pipeline:** READ → PARSE → SYNTHESIZE (Haiku 4.5) → FORMAT → SEND

---

## Setup

### 1. Create `.env`

```bash
cd /home/sashok/.openclaw/workspace/meta/digest
```

Create a file named `.env` with these three keys:

```
SAM_BOT_TOKEN=<copy from sam/.env>
OWNER_CHAT_ID=<copy from sam/.env>
ANTHROPIC_API_KEY=<your key for digest Haiku calls>
```

> `.env` is covered by `meta/.gitignore` — it will not be committed.

### 2. Run tests

```bash
python3 -m pytest tests/ -v
```

### 3. Smoke-test (no AI, no Telegram)

```bash
python3 morning_digest.py --dry-run --no-ai
```

### 4. Full dry-run (with Haiku)

```bash
python3 morning_digest.py --dry-run
```

### 5. Install systemd timer

**User-level (recommended for Pi5 interactive sessions):**

```bash
mkdir -p ~/.config/systemd/user
cp morning_digest.service morning_digest.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now morning_digest.timer
```

**System-wide (runs even without a logged-in session):**

```bash
sudo cp morning_digest.service morning_digest.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now morning_digest.timer
```

> `Persistent=true` in the timer ensures it fires at boot if Pi5 was off at 09:00.

---

## CLI flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Print formatted message to stdout; do not send to Telegram |
| `--no-ai` | Skip Haiku synthesize; send raw BACKLOG items as-is |
| `--from-file PATH` | Read BACKLOG from a custom path (bypasses git-based done detection) |

---

## Debugging

```bash
# Timer / service status
systemctl --user status morning_digest.timer
systemctl --user status morning_digest.service

# Last run logs
journalctl --user -u morning_digest.service -n 50

# Manual run (with output)
cd /home/sashok/.openclaw/workspace/meta/digest
python3 morning_digest.py --dry-run --no-ai
```

---

## BACKLOG format

The parser expects priority sections with these headers:

```
## P0 — Hot         (or ## P0, ### P0 — ..., etc.)
## P1 — Soon
## P2 — Later
```

Items are the **bullet points** (`- item`) within each section.

**Fallback mode:** if no P0/P1/P2 sections are found, all active `##` headings
are collected as P1 items. The current `BACKLOG.md` uses topic-based headings —
the fallback keeps the digest useful until priority sections are added.

**Done вчора:** headings that gained `~~...~~` in the last 24 h (via `git log`).
Fallback (when git unavailable): all `~~closed~~` headings in the file.

---

## Notes

- BACKLOG.md is **read-only** — this script never writes to it.
- Token usage logged to `shared/token_log.jsonl` under the `digest` agent.
- `httpx` INFO logging is suppressed to prevent token leaks in journalctl.
- The `.env` in this directory is isolated from all other bots.
