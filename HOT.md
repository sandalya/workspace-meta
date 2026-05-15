---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Реалізовано token tracker write-side для всіх 5 ботів (Sam, Garcia, household_agent, abby-v2, insilver-v3). Обгорнено client.messages.create у shared/agent_base.py, додано model= параметр для per-call pricing (haiku vs sonnet). Sam /stats тепер живий, Garcia отримав власний tracker. 23/23 тестів pass.

## Last done

- shared/agent_base.py: wrapper на client.messages.create + set_default_tracker() — один виклик покриває всі прямі API calls
- shared/token_tracker.py: get_stats() фільтрує по self.agent, track_raw() отримав model= параметр
- Sam/main.py: set_default_tracker(_cost_tracker) — /stats тепер живий
- Garcia/main.py: власний tracker + set_default_tracker додано
- household_agent: додано трекінг до summarize_session() (1 untracked call)
- abby-v2 та insilver-v3: вже повністю tracked
- Unit-тестування: 23/23 pass (Sam coverage)

## Next

Перезапустити sam.service і garcia.service щоб зміни вступили в силу, потім перевірити /stats в Sam. Потім — token_tracker write-side на ed та інші проекти, або дизайн Sam NBLM Інтервенція 2 (content_gen pipeline log aggregation).

## Blockers

None.

## Active branches

- suggest_backlog_strikes: live у продакшені, smoke test + reason-quality моніторинг
- httpx logging suppression: 6/6 ботів live, токени ротовані
- backup.sh system-snapshot: live, real-run verified
- morning_digest: systemd timer 09:00, перевірка 2026-05-16
- shared/ sym-link: live (commit 5b41001)
- Sam NBLM Інтервенція 1: DONE, Інтервенція 2+ на черзі
- token_tracker write-side: live для 5 ботів, ready для systemd restart

## Open questions

- Яка точність reason-текстів у suggest_backlog_strikes при варіативних контекстах?
- Чи token tracker integration вплине на latency /stats відповідей?
- Які регресії можуть виникнути з 4 chkp fixes при наступних strike-операціях?
- BACKLOG rotation policy для abby images (759M) + sam audio (827M)?
- Потреба tmux-restore.sh для восстановлення сесій на Pi5 reboot?

## Reminders

- household_agent токен ротовано 2026-05-15 — монітор аномалій завтра
- morning_digest systemd timer verify 2026-05-16 о 09:00 (перший run)
- Backup chain: PC 14-day + Pi 3-day, weekly digest Sundays 03:00 (активна)
- DR drill очікує spare SD карти (фізична поставка)
- httpx suppression: усі 6 ботів live, якість перевірена
- shared/ library: active (sam 11, garcia 7, insilver 1, digest 2 imports) — не архів
- backup.sh system-snapshot: real-run tested, all config captured
- Sam NBLM Inter 1: DONE (uuid probe), Inter 2–5 на черзі
- sam.service + garcia.service restart потребує (token_tracker write-side activation)
