---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

Сесія чекпоінту: додано xclip guard у meta/chkp/chkp.py. copy_to_clipboard тепер перевіряє os.environ.get('DISPLAY') перед викликом xclip; якщо нема DISPLAY — одразу return False без шуму. Додано stderr=DEVNULL на Popen як defense-in-depth. Файл: meta/chkp/chkp.py, статус: скомітовано. Поточна черга: послідовність дрібниць беклогу (~1 год, 5 пунктів по 5-15 хв): PROMPT.md commit (не комітиться в поточному flow), CLAUDE.md дрібнота, insilver pre-commit hook, pre-push patterns. Після дрібниць — Sam NBLM Інтервенція 1 (dangling UUID, 30 хв) як перший P2.

## Last done

**2026-05-03** — chkp xclip guard (10 хв):

- **Додано perевірка DISPLAY:** copy_to_clipboard() викликає os.environ.get('DISPLAY'), якщо None — return False без виклику xclip.
- **Defense-in-depth:** stderr=DEVNULL на Popen щоб перехопити 'Can't open display: (null)' помилки.
- **Файл:** meta/chkp/chkp.py, функція copy_to_clipboard().
- **Очікувана поведінка на SSH без X11:** НЕ буде 'Error: Can't open display: (null)' у виводі — тільки тихий fallback (return False).
- **Комітовано** у meta main.

## Next

1. **PROMPT.md commit** (5 хв) — перевірити що chkp.py НЕ комітить PROMPT.md, якщо робить — додати в .gitignore або логіку skip.
2. **CLAUDE.md дрібнота** (5-10 хв) — невеликі оновлення для кларифікації правил (якщо потребна).
3. **insilver pre-commit hook** (15 хв) — налаштування pre-commit перевірок для insilver-v3 проекту.
4. **pre-push patterns** (15 хв) — визначення шаблонів для pre-push перевірок у workspace.
5. **Sam NBLM Інтервенція 1** (30 хв) — фіксити dangling UUID у 2 notebooks (0daaf506, 2d0285dd), restart sam.service.

## Blockers

Немає. Послідовність дрібниць чітка, xclip guard готовий до перевірки на SSH (Pi5 без X11).

## Active branches

- meta: main (xclip guard скомітовано)
- sam: main (потребує restart + notebook recovery на P2)
- ed, workspace-meta: main (public, web_fetch chain active)
- insilver-v3, abby-v2, garcia, household_agent, kit: main (приватні, ручна читання)

## Open questions

- Чи xclip guard робитиме коректно при тестуванні на SSH без X11 (Pi5)?
- Чи PROMPT.md потребує коміту або це автогенерований файл що не слід відслідковувати?
- Чи pre-commit hooks однакові для всіх проектів чи per-project налаштування?
- Чи pre-push patterns синхронізуються у workspace/.env або локально в кожному проекті?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи.
- chkp v3.4 (PATH binary) — перевірка на не-meta проектах, видалення legacy скрипів очікується (2026-05-04).
- sam.service restart — важливо на черзі після дрібниць (зламані notebooks 0daaf506, 2d0285dd).
- kit migration — коли буде час, дати інструкцію для HOT/WARM/COLD переходу.