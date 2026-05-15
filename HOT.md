---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Додано auto-backlog-suggest у chkp.py: другий Haiku call пропонує закрити BACKLOG пункти що покриваються сесійним контекстом. UX: y/n/edit/skip з 30с timeout, --no-backlog-suggest flag, 9 нових pytest тестів (54/54 pass).

## Last done

- Реалізовано suggest_backlog_strikes() — другий Haiku call після HOT генерації
- Інтерактивний режим: y (apply all) / n (skip all) / e (edit manually) / s (select subset) з 30s timeout
- --no-backlog-suggest flag для opt-out у automation
- Валідація proposed strikes перевіряє на true матчі у BACKLOG (не hallucinate)
- Фікс: empty volatile block у call_anthropic() (раніше повертав None)
- 9 нових unit-тестів у test_backlog_suggest.py (54/54 pass локально)
- Дизайн: Haiku max_tokens=1000, JSON структура (line/text/action), no-changes обробка

## Next

Smoke test у реальному chkp: переконатись що пропозиція з'являється при y і страйкує коректно

## Blockers

None.

## Active branches

- httpx logging suppression: live на 2/6 ботів (abby-v2, household_agent), 4 на черзі (ed, garcia, insilver-v3, sam)
- chkp.py robustness: 4 fixes (multi-match, replace edge case, validation, test expansion) + 22 нові unit-тести (48/48 pass), готово до продакшину
- morning_digest: systemd timer live 09:00 щодня, Telegram доставка підтверджена
- chkp suggest_backlog_strikes: feature імплементовано v3.5, готово до smoke test

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
