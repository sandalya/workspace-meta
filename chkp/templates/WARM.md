---
project: {PROJECT_NAME}
updated: {DATE}
---

# WARM — {PROJECT_NAME}

## Триярусна пам'ять — структура проекту

```yaml
last_touched: {DATE}
tags: [infrastructure, memory]
status: active
```

Проект використовує три файли для управління контекстом:
- **HOT.md** — переписується щосесії, поточний крок і результати (~60 рядків).
- **WARM.md** — архітектура, рішення, відкриті питання (~400 рядків, оновлюється інкрементально).
- **COLD.md** — append-only історія, архіви завершених фаз.

Структура прийнята {DATE}. Скрипт `chkp3` автоматизує оновлення через Haiku (fallback Sonnet). Claude-інстанції читають HOT+WARM на старті сесії (Rule Zero в MEMORY.md).

## Архітектура

{ARCHITECTURE_OVERVIEW}

## Компоненти

{COMPONENTS}

## Ключові рішення

{KEY_DECISIONS}

## Інтеграції

{INTEGRATIONS}

## Open questions

{OPEN_QUESTIONS}

