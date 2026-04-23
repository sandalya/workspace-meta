---
project: {PROJECT_NAME}
---

# MEMORY — {PROJECT_NAME}

## Rule Zero

**ПЕРЕД відповіддю на будь-яке питання про стан проекту {PROJECT_NAME} — першим ділом запитати у Саші вміст HOT.md + WARM.md.** Не відповідати з пам'яті, не вгадувати.

Команда для Саші: `cat /home/sashok/.openclaw/workspace/{PROJECT_DIR}/HOT.md /home/sashok/.openclaw/workspace/{PROJECT_DIR}/WARM.md`

## Триярусна пам'ять

- **HOT.md** — ~60 рядків, переписується щосесії. Поточний фокус, останнє що робили, наступний крок, блокери.
- **WARM.md** — ~400 рядків, інкрементальні оновлення. Архітектура, рішення, стан компонентів, відкриті питання.
- **COLD.md** — append-only історія. Завершені фази, міграції, рефакторинги в хронологічному порядку.

## Чекпоінт

Оновлення через `chkp3 {PROJECT_NAME} "що зробили" "наступний крок" "контекст"`. Haiku генерує оновлення, Sonnet fallback при складних змінах (`--sonnet`).

## Правила роботи

- SSH/файли за правилами з userMemories (`cat > /tmp/patch.py`, без base64, без scp для .md).
- API keys — маскувати до останніх 4 символів.
- {PROJECT_SPECIFIC_RULES}
