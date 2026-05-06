---
project: meta
updated: 2026-05-06
---

# HOT — meta

## Now

Ісправлено страйк пункту 1 вручну + додано новий beклог item про replace(,1) баг при першому матчу.

## Last done

- Вручну виправлено BACKLOG.md П.1 (неправильно сторайкнутий)
- Додано BACKLOG пункт про replace(,1) баг: коли FRAGMENT матчиться кілька разів, replace(,1) замість всіх
- Виявлено 3 класи strikethrough багів: silent-skip (не знайшло), multi-match (замінив перший, зігнорував решту), replace(,1) (bug у парсингу)

## Next

Розширити meta/chkp/tests/ тестовими кейсами: silent-skip (BACKLOG item без матча), multi-match (дублікат рядків у BACKLOG), replace(,1) (FRAGMENT який матчиться 2+ рази), ~~closed~~ strikethrough парсинг.

## Blockers

None.

## Active branches

- Backup chain: PC pull (14d retention) + Pi rotation (3d) — automated, live
- Logging security: httpx suppression live (abby-v2, ed-bot); garcia/sam clean; household_agent, insilver-v3 pending
- chkp.py backlog validation: pre-flight checks live, fail-loud з fuzzy hints
- Strikethrough enforcement: dual-location (CLAUDE.md + BACKLOG.md) посилено
- Test expansion: silent-skip, multi-match, replace(,1), ~~closed~~ cases

## Open questions

- Чи тримається strikethrough fix? Моніторити 2-3 сесії перед переходом на [CLOSED].
- Які інші dotfiles резервити: systemd/user/, crontab, dpkg list, git config?
- abby images (759M) + sam audio (827M) — rotation policy відкладене.

## Reminders

- BACKLOG.py replace() має баг: replace(FRAGMENT, 1) замість replace(FRAGMENT) — fix потрібен
- Strikethrough правило дублюється (CLAUDE.md + BACKLOG.md) для надійності
- chkp.py валідація: fail loud перед API call, не мовчазно skip
- httpx INFO logging: suppression live, audit старих journalctl за leaks
- Backup chain повністю автоматизована, DR drill on spare SD arrival
