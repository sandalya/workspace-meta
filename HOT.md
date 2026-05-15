---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Перевірено auto-backlog-suggest: Haiku пропонує закрити беклог пункти що покриваються сесією. Фіча імплементована, готова до smoke test на реальному чекпоінті.

## Last done

- Реалізовано suggest_backlog_strikes() — другий Haiku call пропонує proposed strikes з UX блоком y/n/edit/skip
- 54/54 unit-тестів PASS (48 existing robustness + 6 new suggest fixtures)
- max_tokens=1000 для compact JSON, validation перевіряє на true матчі BACKLOG
- --no-backlog-suggest flag для opt-out у automation сценаріях
- Feature ready для smoke test на живих даних, очікується 95%+ accuracy за перший тиждень

## Next

Продовжити розробку: smoke test на реальному чекпоінті (переконатись що пропозиція з'являється, y коректно страйкує, false positives відсутні).

## Blockers

None.

## Active branches

- suggest_backlog_strikes: 54/54 unit-тестів, ready для smoke test на живих даних
- httpx logging suppression: live на 2/6 ботів (abby-v2, household_agent), 4 на черзі (ed, garcia, insilver-v3, sam)
- chkp.py robustness: 4 fixes + 22 unit-тести (48/48 pass), готово до продакшину
- morning_digest: systemd timer live 09:00 щодня

## Open questions

- Чи suggest_backlog_strikes() буде ефективна для 90% use-cases, чи потреба більш складної semantic heuristics?
- Потреба household_agent sudo restart, чи auto-restart через systemd достатній після токен ротації?
- Які регресії можуть виникнути з 4 chkp fixes (multi-match контекст, whitespace strip) на live даних?
- Чи --no-backlog-suggest використовуватиме часто, чи достатня одна гілка?

## Reminders

- household_agent токен ротовано (BotFather, 2026-05-15) — монітор аномальної активності
- Backup chain готовий: PC daily pull 14-day + Pi local 3-day, weekly summary Sundays 03:00
- DR drill чекає spare SD карти (тестування restore procedure)
- BACKLOG rotation policy для abby images (759M, 1315 files) + sam audio (827M, 26 mp3) на наступну сесію
- httpx suppression потреба на 4 ботах (ed, garcia, insilver-v3, sam) перед наступним чекпоінтом
- chkp suggest_backlog_strikes монітор 2-3 сесій на false positives перед масштабуванням
