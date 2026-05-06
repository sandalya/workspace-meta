---
project: meta
updated: 2026-05-06
---

# HOT — meta

## Now

Додано до BACKLOG задачу на розширення chkp тестів: silent-skip, multi-match, replace(,1), ~~closed~~ strikethrough парсинг.

## Last done

- Аналіз apply_backlog_flags(): виявлено 3 класи багів (silent-skip, multi-match, replace(,1))
- Дефіновано тестові кейси для robustness validation
- Додано BACKLOG пункт про розширення meta/chkp/tests/

## Next

Запустити нову сесію в meta/ для написання тестів: (a) silent-skip (BACKLOG item без матча), (b) multi-match (FRAGMENT матчиться 2+ рази), (c) replace(,1) (баг з першим матчем), (d) ~~closed~~ strikethrough парсинг.

## Blockers

Нема.

## Active branches

- Backup chain: PC pull (14d retention) + Pi rotation (3d) — automated, live
- Logging security: httpx suppression live (abby-v2, ed-bot); garcia/sam clean; household_agent, insilver-v3 pending
- chkp.py backlog validation: pre-flight checks live, fail-loud з fuzzy hints
- Strikethrough enforcement: dual-location (CLAUDE.md + BACKLOG.md) посилено
- Test expansion: silent-skip, multi-match, replace(,1), ~~closed~~ cases — NEXT SPRINT

## Open questions

- Чи тримається strikethrough fix? Моніторити 2-3 сесії перед переходом на [CLOSED].
- Які інші dotfiles резервити: systemd/user/, crontab, dpkg list, git config?
- abby images (759M) + sam audio (827M) — rotation policy відкладене.

## Reminders

- BACKLOG.py replace() має баг: replace(FRAGMENT, 1) замість replace(FRAGMENT) — fix потрібен у спринті
- Strikethrough правило дублюється (CLAUDE.md + BACKLOG.md) для надійності
- chkp.py валідація: fail loud перед API call, не мовчазно skip
- httpx INFO logging: suppression live на 2/6 ботів, audit старих journalctl за leaks
- Backup chain повністю автоматизована, DR drill на приїзд запасної SD карти
