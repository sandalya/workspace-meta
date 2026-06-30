---
---
# chkp — інструмент керування беклогом/пам'яттю

chkp (v3.4+) — Sasha's CLI tool для WARM diff-режиму (`warm_ops`) та
пропозицій по беклогу.

- `suggest_backlog_strikes()` — другий Haiku-виклик, пропозиції по очищенню беклогу.
- `validate_backlog_flags()` — fuzzy-перевірка флагів беклогу перед записом.
- Тести — `meta/chkp/tests/`.

Деталі дивись у @~/.openclaw/workspace/meta/chkp/ перш ніж пропонувати зміни.

## Як виконувати чекпоінт за запитом

Коли я кажу "зроби chkp для <project>" або "зачекпойнть <project>":
1. Сформулюй what_done/next_step/context на основі реального контексту
   поточної сесії (diff-и, коміти, обговорення) — не вигадуй.
2. Спочатку запусти з `--dry-run`, покажи мені вивід.
3. Після мого підтвердження — запусти без --dry-run.
4. Команда: `python3 ~/.openclaw/workspace/meta/chkp/chkp.py <project> "..." "..." "..."`
   (або `chkp <project> ...` якщо alias підхопився в shell-сесії, де працює CC)
