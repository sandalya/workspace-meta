---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

Цикл дрібниць закрито (5 з 5 пунктів за ~1 год як планували). Завершено:
- **pre-push patterns** (15 хв) — insilver-v3-dev/.git/hooks/pre-push: видалено blanket .jpg/.jpeg/.png, замінено на специфічні шляхи (data/photos/incoming/, data/photos/clients/) + Telegram client-ID формат [0-9]{9,}_.*. data/photos/static/ тепер дозволено.
- **CLAUDE.md дрібнота** (5 хв) — закрита (commit 99330fa).
- **insilver pre-commit hook** — перевірено, працює (раніше переписаний, беклог-пункт застарів).
- **xclip guard** + **PROMPT.md flow** — готові до перевірки (попередня сесія).

## Last done

**2026-05-03** — Цикл дрібниць беклогу (60 хв):

- **pre-push patterns у insilver-v3-dev** (15 хв): Замість blanket .jpg/.jpeg/.png видалено, добавлено специфічні шляхи: `data/photos/incoming/` та `data/photos/clients/` + Telegram client-ID формат `[0-9]{9,}_.*` (мінімум 9 цифр, потім підкреслення). `data/photos/static/` явно дозволено (білий список). Pre-push hook тепер чистіший, зменшена ймовірність false positives.
- **CLAUDE.md дрібнота** (5 хв): Дрібні уточнення правил. Commit 99330fa.
- **insilver pre-commit hook перевірка** (5 хв): Hook уже переписано раніше, працює коректно. Беклог-пункт був застарілим.
- **Попередня сесія (2026-05-03):** chkp PROMPT.md flow fix (10 хв) + xclip guard (10 хв), разом 20 хв за дві мікро-сесії.

## Next

1. **Sam NBLM Інтервенція 1** (30 хв) — детектування dangling UUID в get_or_create_notebook (notebooks 0daaf506, 2d0285dd), restart sam.service. Перший живий P2 з беклогу після дрібниць.
2. **Перевірити dev upstream в insilver-v3-dev** (5-10 хв) — `git push` без upstream: є питання чи це нормально для Model A чи треба `git push -u origin dev`.
3. **Перевірити PATH binary на не-meta проектах** (15 хв) — протестувати `chkp` на реальному проекті (не meta), видалити legacy скрипти (kit/chkp.sh, kit/chkp2.sh, meta/chkp.sh), синхронізувати .gitignore.
4. **Розпочати kit міграцію** (за часом) — HOT/WARM/COLD структура для kit.

## Blockers

Немає. Дрібниці закрито, готово до P2. Питання про git upstream інформаційне, не блокер.

## Active branches

- meta: main (дрібниці + chkp комітовано)
- insilver-v3-dev: dev (pre-push patterns скомітовано, без upstream?)
- sam: main (потребує restart + notebook recovery на P2)
- ed, workspace-meta: main (публічні, web_fetch memory active)
- abby-v2, garcia, household_agent, kit: main (приватні, ручна памʼять)

## Open questions

- Чи `git push` без set-upstream нормально для Model A (insilver-v3-dev) чи треба явна конфігурація?
- Чи ручне тестування PATH binary на не-meta проектах виявить inшу проблему?
- Чи чекпоінт через chkp для не-meta проектів коректно робить per-project commits?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи.
- sam.service restart — на черзі після P2 (dangling UUID).
- kit migration на HOT/WARM/COLD — коли буде час, дати інструкцію.
- chkp v3.4 перевірка на не-meta — видалення legacy скрипів очікується (2026-05-04).
- PROMPT.md верифікація: після чекпоінту git status має бути чистим.
