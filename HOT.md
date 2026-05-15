---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Перевірено auto-backlog-suggest фічу: Haiku пропонує закрити беклог пункти що покриваються контекстом сесії (## Now/Last done). Smoke test готовий до запуску на реальних даних.

## Last done

- Перевіреено фічу suggest_backlog_strikes() з 54/54 unit-тестами PASS
- UX блок (y/n/edit/skip) з 30s timeout інтегрований
- Валідація proposed strikes на true матчі у BACKLOG
- --no-backlog-suggest flag для opt-out готовий
- Готово до smoke test на реальному чекпоінті

## Next

Продовжити розробку: smoke test на реальному чекпоінті (переконатись що пропозиція з'являється, y коректно страйкує, false positives відсутні). Після верифікації — масштабування на 6 проектів.

## Blockers

None.

## Active branches

- suggest_backlog_strikes: 54/54 unit-тестів, smoke test на реальних даних NEXT
- httpx logging suppression: live на 2/6 ботів (abby-v2, household_agent), 4 на черзі
- chkp.py robustness: 4 fixes + 22 unit-тести (48/48 pass), live validation pending
- morning_digest: systemd timer 09:00 daily, перевірка завтра

## Open questions

- Чи suggest_backlog_strikes() буде ефективна для 90% use-cases, чи потреба більш складної semantic heuristics?
- Потреба household_agent sudo restart, чи auto-restart через systemd достатній після токен ротації?
- Які регресії можуть виникнути з 4 chkp fixes (multi-match контекст, whitespace strip) на live даних?
- Чи all 4 ботів (ed, garcia, insilver-v3, sam) повинні мати однакову httpx suppression pattern як abby-v2/household_agent?

## Reminders

- household_agent токен ротовано (BotFather, 2026-05-15) — монітор аномальної активності
- Backup chain готовий: PC daily pull 14-day + Pi local 3-day, weekly summary Sundays 03:00
- DR drill чекає spare SD карти для тестування restore procedure
- BACKLOG rotation policy для abby images (759M) + sam audio (827M) на наступну сесію
- httpx suppression потреба на ed, garcia, insilver-v3, sam перед наступним чекпоінтом
- morning_digest timer verify завтра 09:00
- shared/ sym-link (meta/shared) live, 5b41001, активна бібліотека (не на видалення)
