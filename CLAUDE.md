# Sasha — workspace root

Ти працюєш з Sasha: Senior CG Artist (Houdini/USD/ACES/Arnold, Plarium),
паралельно будує AI/agentic проєкти з ціллю переходу в AI/CV за 1-2 роки.

## Структура воркспейсу
Це корінь, а не проєкт. Підпапки — окремі проєкти (боти, дрон-рекон і т.д.),
кожен зі своїм CLAUDE.md. Якщо потрібно працювати з конкретним проєктом —
заходь у відповідну підпапку, читай локальний CLAUDE.md.

## Перед початком роботи
- Якщо задача стосується кількох проєктів одночасно — спочатку дивись
  @~/.openclaw/workspace/meta/BACKLOG.md (крос-проектний беклог).
- Конвенції чкп і пам'яті HOT/WARM/COLD — у .claude/rules/, читай їх
  як стандартний робочий процес, а не як опціональну довідку.

## Language
Separate interface language from model thinking language. System prompts, instructions, HOT/WARM/COLD memory, and all internal context → English (cheaper tokens, more precise reasoning). User-facing responses → Ukrainian. Response language is determined by the user's input language, not the system prompt language.

## Що НЕ робити
- Не плутай корінь воркспейсу з окремим git-репо проєкту.
- Не пиши код прямо в кореневій директорії.
