Проект: meta

Стан: chkp v3.5 з auto-backlog-suggest у продакшені. Додано другий Haiku call що пропонує закрити BACKLOG пункти після HOT генерації (y/n/edit/skip UX, 30s timeout). 9 нових тестів (54/54 pass). Фікс empty volatile block у call_anthropic().

Чи готово до smoke test? Переконатись що suggest_backlog_strikes() з'являється при y і страйкує коректно. Також: 4 robustness fixes у apply_backlog_flags (multi-match контекст, whitespace strip) готові до live validation.

Монітор: household_agent токен ротовано (BotFather 2026-05-15), httpx suppression live на 2/6 ботів, morning_digest timer 09:00 щодня OK.

Beкдаун: BACKLOG rotation policy (abby 759M, sam 827M), tmux-restore.sh, 4 ботів потребують httpx suppression, BACKLOG hygiene workflow.

Шерфи HOT.md + WARM.md перед началом.