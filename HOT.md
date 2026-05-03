---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

Беклог-очистка завершена: викинуто 5 застарілих секцій (3 CLOSED P1.x, 1 SUPERSEDED Sam queue, abby-v1 GitHub deletion). Поточна черга: послідовність дрібниць ~1 год (5 пунктів P-низький, кожен 5-15 хв). Перший: chkp xclip guard у meta/chkp/chkp.py (try/except навколо xclip виклику, перевірка os.environ.get DISPLAY). Після них — Sam NBLM Інтервенція 1 (dangling UUID, 30 хв) як перший P2 з живих.

## Last done

**2026-05-03** — беклог-очистка (30 хв):

- **Викинуто 5 застарілих секцій:** 3 CLOSED P1.x від 03.05, 1 SUPERSEDED Sam queue від 02.05, abby-v1 GitHub deletion (вже видалено вручну).
- **План на наступні дрібниці узгоджено:** chkp xclip fix, CLAUDE.md дрібнота, chkp PROMPT.md commit, insilver pre-commit, pre-push patterns.
- **Контекст послідовності:** 5 пунктів P-низький (~1 год), кожен 5-15 хв. Першим P2: Sam NBLM Інтервенція 1 (dangling UUID, 30 хв).

## Next

1. **chkp xclip guard** (5-10 хв) — спробувати додати try/except навколо xclip виклику в meta/chkp/chkp.py, перевірка os.environ.get('DISPLAY') перед викликом. Ціль: soft-fail якщо xclip недоступний (headless режим).
2. **CLAUDE.md дрібнота** (5-10 хв) — невеликі оновлення для кларифікації правил.
3. **chkp PROMPT.md commit** (5 хв) — коміт оновленої підказки.
4. **insilver pre-commit** (5-10 хв) — налаштування pre-commit hook.
5. **pre-push patterns** (5 хв) — визначення шаблонів для pre-push перевірок.
6. **Sam NBLM Інтервенція 1** (30 хв) — фіксити dangling UUID у 2 notebooks (0daaf506, 2d0285dd), restart sam.service.

## Blockers

Немає. Послідовність дрібниць чітка, Sam чекає на черзі.

## Active branches

- meta: main (чищено, готово для дрібниць)
- sam: main (потребує restart + notebook recovery на P2)
- ed, workspace-meta: main (public, web_fetch chain active)
- insilver-v3, abby-v2, garcia, household_agent, kit: main (приватні, ручна читання)

## Open questions

- Чи xclip на Pi5 доступний чи потреба fallback на системний буфер?
- Чи pre-commit hooks однакові для всіх проектів чи per-project?
- Чи PROMPT.md commit потребує force-push на meta або звичайний push?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи.
- chkp v3.4 (PATH binary) — перевірка на не-meta проектах, видалення legacy скрипів очікується (2026-05-04).
- sam.service restart — важливо на черзі після дрібниць (зламані notebooks 0daaf506, 2d0285dd).
- kit migration — коли буде час, дати інструкцію для HOT/WARM/COLD переходу.
