---
project: meta
updated: 2026-05-05
---

# HOT — meta

## Now

Налаштовано acceptEdits + allow/deny rules в ~/.claude/settings.json, alias cld тепер з --permission-mode acceptEdits, перевірено що один файл settings без local override.

## Last done

- Налаштовано acceptEdits + allow/deny rules у ~/.claude/settings.json
- Оновлено alias cld з --permission-mode acceptEdits
- Верифіковано що один файл settings достатній без локальних override

## Next

Тест 'відійти на 15 хвилин' на реальній задачі з беклогу sam або insilver-v3-dev — поміряти скільки prompts накопичується.

## Blockers

Немає.

## Active branches

- ~/.claude/settings.json інтеграція з acceptEdits (завершено)
- alias cld з --permission-mode (завершено)
- Тест накопичення prompts при паузі (планується)

## Open questions

- Скільки prompts насправді накопичується за 15 хвилин паузи на реальній задачі?
- Чи deny rules достатніх для захисту prod insilver-v3 та sam?

## Reminders

- Auto mode на акаунті поки недоступний (не з'являється в Shift+Tab, /help не згадує)
- Deny rules: prod insilver-v3, .env, push в main, sudo, journalctl без grep, rm -rf критичних шляхів
- Запланований тест на реальній задачі — вибрати sam або insilver-v3-dev