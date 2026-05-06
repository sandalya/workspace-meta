---
project: meta
updated: 2026-05-06
---

# HOT — meta

## Now

Backlog audit 2026-05-06: закрито 7 DONE пунктів, залишилось 5 TODO + 4 PARTIAL + 2 UNCLEAR для розбору.

## Last done

- Пройшов backlog 2026-05-06, застрайкав 7 завершених пунктів
- П.1 transcription позначено done, але Ed блок 12_voice_consistency не створено
- П.8a/8b застрайкані окремим коммітом
- Ідентифікував PARTIAL пункти що потребують уточнення

## Next

Розібратись з PARTIAL пунктами 3 (shared/), 6 (agentic ingest), 7 (NBLM /nbstatus), 17 (wait-loop) — конвертувати в чіткі TODO або закрити

## Blockers

None.

## Active branches

- Backup chain: PC pull (14d retention to H:\pi_backups) + Pi rotation (3d) — complete, automated
- sandalya/pi5-backup GitHub repo — live with backup.sh, notify.sh, exclude.txt, README.md
- DR drill — pending spare SD arrival
- Logging security: httpx token leak suppressed abby-v2, ed-bot; garcia/sam clean; household_agent, insilver-v3 to patch
- chkp.py backlog validation pre-flight — live, production-ready
- Strikethrough rule enforcement — dual-location enforcement (CLAUDE.md + BACKLOG.md) live

## Open questions

- Чи тримається strikethrough fix? Спостерігати 2-3 сесії перед переходом на [CLOSED] маркер.
- Які інші файли systemd/dotfiles потребують резервної копії: ~/.config/systemd/user/, crontab, dpkg list, git config?
- Абby images (759M) + sam audio (827M) — rotation policy відкладене.

## Reminders

- Backup chain повністю автоматизована: PC pull 14d, Pi local 3d, Telegram on error only
- httpx INFO logging leak tokens — patched abby-v2, ed; garcia/sam/household_agent/insilver-v3 to verify
- meggi CPU-only venv (497M), faster-whisper verified
- .u2net consolidated: isnet-general-use.onnx (171M) для rembg
- chkp.py backlog validation: fail loud з fuzzy hints перед API call
- Strikethrough правило дублюється у двох місцях для надійності (CLAUDE.md header + BACKLOG.md header)