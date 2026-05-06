---
project: meta
updated: 2026-05-06
---

# HOT — meta

## Now

Посилено правило про strikethrough у двох місцях: CLAUDE.md (секція Backlog) та BACKLOG.md header додано візуальний STOP блок із прикладами і алгоритмом. Виправлено невірний шлях /workspace/BACKLOG.md → /workspace/meta/BACKLOG.md у CLAUDE.md. CC-тест підтвердив що закреслене більше не повертається як активне TODO.

## Last done

- Посилено header rule про strikethrough у CLAUDE.md (агент-документація, секція Backlog) — деталізовано коли й як закреслювати
- Посилено правило у BACKLOG.md header — додано візуальний STOP блок з прикладами невалідних форматів та алгоритмом обробки
- Виправлено невірний шлях /workspace/BACKLOG.md → /workspace/meta/BACKLOG.md у посиланнях CLAUDE.md
- Запущено CC-тест: summarize active items — закреслені пункти не повернулися як активні, тест PASS

## Next

Якщо за тиждень-два трапиться що Claude повертає закреслене як активне — додавати маркер не-markdown (## [CLOSED] Title замість ~~) як додатковий сігнал. Інакше спостерігати 2-3 сесії, чи утримується фікс.

## Blockers

Нone.

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
