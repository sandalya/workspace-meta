---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Змінено _SUGGEST_SYSTEM промпт на українську мову, фіксили empty volatile block bug у call_anthropic (400 error з porожнім volatile + cacheable >= 1024 tokens). Smoke test пройшов — suggest_backlog_strikes() коректно пропонує й страйкає. 54/54 pytest pass.

## Last done

- Переписаний _SUGGEST_SYSTEM промпт у chkp.py: reason поле тепер українською (мовна консистентність)
- Фікс empty volatile block: call_anthropic тепер явно перевіряє len(volatile_block) перед передачею у Haiku (уникаємо 400 API error)
- Валідація: smoke test + ручна перевірка на реальних даних (Сашко)
- Unit-тестування: 54/54 pytest PASS (48 robustness + 6 suggest_backlog_strikes)
- Пропозиція strikes: y-блок коректно применяє, false positives відсутні

## Next

Моніторити якість reason-текстів у наступних реальних сесіях (переконатись що семантична якість пропозицій стабільна при варіативних контекстах). Потім масштабування suggest_backlog_strikes на 6 проектів після першого тижня smoke test на insilver-v3/sam.

## Blockers

None.

## Active branches

- suggest_backlog_strikes: live у продакшені, smoke test + reason-quality мониторинг
- httpx logging suppression: 2/6 ботів live (abby-v2, household_agent), 4 на черзі (ed, garcia, insilver-v3, sam)
- chkp.py robustness: 4 fixes + 22 unit-тести (48/48 pass), live validation in progress
- morning_digest: systemd timer 09:00, перевірка завтра
- shared/ sym-link: live (commit 5b41001), активна бібліотека

## Open questions

- Яка точність reason-текстів у suggest_backlog_strikes на різних типах контексту (NBLM, logging, cleanup)?
- Потреба household_agent sudo restart, чи auto-restart через systemd достатній після токен ротації?
- Які регресії можуть виникнути з 4 chkp fixes на live даних (multi-match контекст, whitespace strip)?
- Чи all 4 ботів (ed, garcia, insilver-v3, sam) повинні мати однакову httpx suppression?

## Reminders

- household_agent токен ротовано (BotFather, 2026-05-15) — монітор аномалій
- morning_digest timer verify завтра 09:00 (첫번째 實行)
- httpx suppression на ed, garcia, insilver-v3, sam перед наступним checkpoint
- Backup chain: PC 14-day + Pi 3-day, weekly Sundays 03:00 (активна)
- DR drill чекає spare SD карти
- BACKLOG rotation: abby images (759M) + sam audio (827M) — на наступну сесію
