---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Постмортем chkp/backlog виявив системний дрейф: AI у чаті не звіряє 'що зробили' з активними пунктами беклогу перед chkp, тому --backlog-strike просто не передається. Дрібна механіка (multi-match, replace,1) закрита Батчем 1; потреба semantic solution — suggest_backlog_strikes() з другим Haiku call для автоматичного маппінгу сесії на BACKLOG пункти.

## Last done

- Постмортем chkp/backlog:識別 root cause дрейфу (AI не звіряє, не передає флаги)
- Доказ: 0674dd4 (household_agent filter-repo 240M→612K) — чекпоінт є, strike флага 11 днів
- CC бриф готовий: suggest_backlog_strikes() після Haiku-генерації, другий Haiku call для mapping, UX блок y/n/edit/skip, --no-backlog-suggest opt-out
- 8 нових pytest케이스 написано

## Next

Скинути CC бриф у наступну CC-сесію (suggest_backlog_strikes feature), після імплементації — smoke test на дрібній сесії що закриває реальний пункт BACKLOG.

## Blockers

None.

## Active branches

- httpx logging suppression: live на 2/6 ботів (abby-v2, household_agent), 4 на черзі (ed, garcia, insilver-v3, sam)
- chkp.py robustness: 4 fixes + 22 нові unit-тести (48/48 pass), готово до продакшину
- morning_digest: systemd timer live 09:00 щодня, Telegram доставка підтверджена
- shared/ library: аудит завершено, BACKLOG пункт коректний (активна бібліотека)
- token tracker: audit підтверджує non-critical статус
- chkp suggest_backlog_strikes: design етап, на імплементацію

## Open questions

- Чи suggest_backlog_strikes() буде ефективна для 90% use-cases, чи потреба більш складної heuristics?
- Потреба household_agent sudo restart, чи auto-restart через systemd достатній після токен ротації?
- Які регресії можуть виникнути з 4 chkp fixes на live даних (multi-match контекст, whitespace strip)?
- Token tracker write-side expansion для 6 ботів, чи достатньо digest + garcia sampling?

## Reminders

- household_agent токен ротовано (BotFather, 2026-05-15) — монітор аномальної активності
- Backup chain готовий, DR drill чекає spare SD карти
- BACKLOG rotation policy для abby images (759M) + sam audio (827M) на наступну сесію
- Strikethrough rule (CLAUDE.md + BACKLOG.md): спостерігати 2-3 сесії, потім [CLOSED] markup
- httpx suppression потреба на 4 ботах (ed, garcia, insilver-v3, sam) перед наступним чекпоінтом
- shared/ BACKLOG пункт видалено (активна бібліотека)
- Token tracker non-critical: action не потреба без per-bot billing вимоги