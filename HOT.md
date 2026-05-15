---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Household_agent .git аудит завершено: 376K після cleanup (gallery-dl/pinterest 252MB видалені через filter-repo ~4 травня). Беклог-пункт від 29.04 застарів — видалено .git/filter-repo/analysis (340K).

## Last done

- household_agent .git аудит: 376K фінальний розмір
- Беклог-пункт про 239M видалено як застарілий (gallery-dl/pinterest уже почищено)
- .git/filter-repo/analysis видалено (340K додаткова економія)
- Підтверджено: filter-repo cleanup проведено ~4 травня, беклог не оновлено

## Next

Повернутись до Влада/Ксюші наступної сесії для voice extraction task Влада (~2h) або antypastka #24 на іншому BACKLOG пункті.

## Blockers

None.

## Active branches

- httpx logging suppression: live на 2/6 ботів (abby-v2, household_agent), 4 на черзі (ed, garcia, insilver-v3, sam)
- chkp.py robustness: 4 fixes + 22 нові unit-тести (48/48 pass), готово до продакшину
- morning_digest: systemd timer live 09:00 щодня, Telegram доставка підтверджена
- shared/ library: аудит завершено, BACKLOG пункт коректний (активна бібліотека, не мертвий код)
- token tracker: audit підтверджує non-critical статус для live ops

## Open questions

- Чи shared/ usage залишиться стабільною, або garcia refactor (PodcastModule наслідування) потребує polyrepo planning?
- Потреба household_agent sudo restart, чи auto-restart через systemd достатній після токен ротації?
- Які регресії можуть виникнути з 4 chkp fixes на live даних (multi-match контекст, whitespace strip)?
- Чи всі 6 ботів мають однакову httpx suppression pattern, або аудит кожного окремо?
- Token tracker write-side expansion для 6 ботів, чи достатньо digest + garcia sampling?

## Reminders

- household_agent токен ротовано (BotFather, 2026-05-15) — монітор аномальної активності
- Backup chain готовий, DR drill чекає spare SD карти
- BACKLOG rotation policy для abby images (759M) + sam audio (827M) на наступну сесію
- Strikethrough rule (CLAUDE.md + BACKLOG.md): спостерігати 2-3 сесії, потім [CLOSED] markup
- httpx suppression потреба на 4 ботах (ed, garcia, insilver-v3, sam) перед наступним чекпоінтом
- shared/ BACKLOG пункт видалено (активна бібліотека: 11+7+1+2 imports)
- Token tracker non-critical: action не потреба без per-bot billing вимоги