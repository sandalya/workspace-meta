---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

Сесія чекпоінту: фікс PROMPT.md flow у chkp.py. Раніше PROMPT.md писався ПІСЛЯ git commit і залишався modified у working tree між сесіями. Тепер PROMPT.md пишеться ПЕРЕД git add -A, тому потрапляє до чекпоінт-комміту і git status після чекпоінту чистий. Видалено дублювання prompt= у output. Файл: meta/chkp/chkp.py, статус: скомітовано. Зафіксовано: xclip guard (DISPLAY check + stderr=DEVNULL) готовий до тестування на SSH без X11 (Pi5). Поточна черга: 3 дрібниці беклогу (~35 хв, 3 пункти по 5-15 хв): CLAUDE.md дрібнота, insilver pre-commit hook, pre-push patterns. Після дрібниць — Sam NBLM Інтервенція 1 (dangling UUID, 30 хв) як перший P2.

## Last done

**2026-05-03** — chkp PROMPT.md commit flow fix (10 хв):

- **PROMPT.md timing:** Переміщено запис PROMPT.md з post-commit (після git commit) на pre-add (перед git add -A). Результат: PROMPT.md потрапляє у чекпоінт-коміт через `git add -A`, а не залишається modified у working tree.
- **Дублікація видалена:** Раніше буква copy_to_clipboard викликалася й при write_prompt_md, й у copy flow, це давало дублі prompt= у output. Тепер один раз через write_prompt_md.
- **Очікувана поведінка:** `chkp` завершується з чистим `git status` — PROMPT.md уже у комміті, не modified. Між сесіями немає затримуваних файлів.
- **Файл:** meta/chkp/chkp.py, функція main() (зміна в порядку операцій після generate_ai_response).
- **Комітовано** у meta main.

**Попередня сесія: 2026-05-03** — chkp xclip guard (10 хв):
- Додано DISPLAY check у copy_to_clipboard(), stderr=DEVNULL на Popen.
- Очікувана поведінка на SSH без X11: мовчазний fallback, без 'Can't open display' помилок.

## Next

1. **CLAUDE.md дрібнота** (5-10 хв) — невеликі уточнення правил, якщо потребна.
2. **insilver pre-commit hook** (15 хв) — налаштування pre-commit перевірок для insilver-v3 (lint, format, secrets).
3. **pre-push patterns** (15 хв) — визначення шаблонів для pre-push перевірок у workspace (branch naming, commit msg).
4. **Sam NBLM Інтервенція 1** (30 хв) — фіксити dangling UUID у 2 notebooks (0daaf506, 2d0285dd), restart sam.service.

## Blockers

Немає. PROMPT.md flow стабілізований, xclip guard готовий до перевірки на Pi5 SSH, дрібниці чітко визначені.

## Active branches

- meta: main (PROMPT.md commit flow скомітовано)
- sam: main (потребує restart + notebook recovery на P2)
- ed, workspace-meta: main (public, web_fetch chain active)
- insilver-v3, abby-v2, garcia, household_agent, kit: main (приватні, ручна читання)

## Open questions

- Чи PROMPT.md потребує окремого коміту з message або автоматична інтеграція у чекпоінт достатня?
- Чи xclip guard робитиме коректно при тестуванні на SSH без X11 (Pi5)?
- Чи pre-commit hooks однакові для всіх проектів чи per-project налаштування?
- Чи pre-push patterns синхронізуються у workspace/.env або локально в кожному проекті?
- Чи CLAUDE.md дрібнота значна чи косметична правка?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи.
- chkp v3.4 (PATH binary) — перевірка на не-meta проектах, видалення legacy скрипів очікується (2026-05-04).
- sam.service restart — важливо на черзі після дрібниць (зламані notebooks 0daaf506, 2d0285dd).
- kit migration — коли буде час, дати інструкцію для HOT/WARM/COLD переходу.
- PROMPT.md верифікація: після чекпоінту git status має бути чистим, PROMPT.md уже у комміті.