---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Викреслено виконаний пункт беклогу: chkp auto-backlog-suggest реалізовано і верифіковано в попередніх сесіях.

## Last done

- Позначено як завершений пункт про chkp auto-backlog-suggest у BACKLOG.md
- Верифіковано що feature live у продакшені з 54/54 unit тестами

## Next

Продовжити з P2 беклогу.

## Blockers

None.

## Active branches

- suggest_backlog_strikes: live у продакшені, smoke test + reason-quality мониторинг на наступні сесії
- httpx logging suppression: 6/6 ботів готово, токени ротовані
- backup.sh system-snapshot: live, syntax OK, real-run verified
- morning_digest: systemd timer 09:00, перевірка завтра
- shared/ sym-link: live (commit 5b41001)

## Open questions

- Яка точність reason-текстів у suggest_backlog_strikes при варіативних контекстах?
- Потреба household_agent sudo restart, чи systemd auto-restart достатній після токен ротації?
- Які регресії можуть виникнути з 4 chkp fixes (multi-match, whitespace strip) на live даних?
- BACKLOG rotation policy для abby images (759M) + sam audio (827M) — розстановка або видалення?

## Reminders

- household_agent токен ротовано 2026-05-15 — монітор аномалій у логах
- morning_digest timer verify завтра о 09:00 (перший run)
- Backup chain: PC 14-day + Pi 3-day, weekly digest Sundays 03:00 (активна)
- DR drill очікує spare SD карти (фізична поставка)
- httpx suppression: усе 6 ботів live, семантична якість prichecked
- shared/ library: active (sam 11, garcia 7, insilver 1, digest 2 imports) — не архів
- backup.sh system-snapshot: real-run tested, settings.json + crontab/dpkg/pip all captured