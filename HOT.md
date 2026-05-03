---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

Починаємо Sam NBLM Інтервенцію 1 (dangling UUID detection у `get_or_create_notebook`). Цикл дрібниць і чkp guard рефакторинг завершені попередньої сесії.

## Last done

**2026-05-03** — Цикл дрібниць + чkp guard + PATH binary стабілізація (~4 год):

- **PATH binary v3.4 валідація** (~1.5 год): Усі чекпоінти (meta, insilver-v3, insilver-v3-dev) виконані через `/home/sashok/.local/bin/chkp` шим. Верифіковано: `bash -c chkp --help` показує v3.4 (--backlog-strike, --sonnet). SESSION.md артефакт видалено, .gitignore оновлено. xclip guard (DISPLAY check) + PROMPT.md flow (перед git add) перевірено.
- **chkp guard рефакторинг** (~10 хв): warn про dev-каталог тільки коли cwd == args.project + '-dev'. Cross-project (cd insilver-v3-dev && chkp meta) — мовчазний. Рішення мінімізує false positives при Model A потоці.
- **insilver-v3-dev pre-push patterns** (~20 хв): видалено blanket .jpg бан, замінено на специфічні шляхи (data/photos/incoming/, data/photos/clients/) + TG client-ID regex [0-9]{9,}_.*. Причина: security cleanup 2026-04-29.
- **CLAUDE.md, PROMPT.md, xclip guard** (~50 хв, попередня сесія): дрібниці закрито. Готово до P2.
- **legacy скрипти — статус** (~30 хв): kit/chkp.sh, kit/chkp2.sh, meta/chkp.sh перенесені в meta/legacy/chkp_bash_v1/. chkp.py.bak залишено. SESSION.md видалено. Потреба фінального видалення legacy папки (як наступний крок, коли підтвердимо що v3.4 працює на не-meta проектах).

## Next

1. **Sam NBLM Інтервенція 1** (~30 хв) — **детектування dangling UUID в `get_or_create_notebook`:**
   - файл: `sam/core/content_gen/backends/nblm.py`, метод `get_or_create_notebook`
   - проблема: UUID 0daaf506, 2d0285dd referencias на notebook'и що не існують (RPC false match або null result)
   - рішення: перед reuse робимо `probe source list -n --json`, перевіряємо результат не null, інвалідуємо `nblm_notebook_id` якщо fail, fallthrough на create
   - перевірка: `sam.service restart`, manual test у sam/notebooks
   - розблокує: rag_retrieval-1 (UUID 0daaf506)

2. **Перевірити PATH binary на не-meta проектах** (~15 хв) — тестувати `chkp` на garcia, abby-v2, ed (реальні проекти), видалити legacy скрипти за підтвердженням.

3. **git upstream у insilver-v3-dev** (~5 хв) — перевірити чи `git push` без set-upstream нормально для Model A, або додати `git push -u origin dev`.

4. **Синхронізувати .gitignore** — SESSION.md + legacy/ шляхи, дублювати до всіх проектів.

## Blockers

Немає. Готово до P2.

## Active branches

- meta: main (v3.4 PATH binary, guard рефакторинг, legacy in archive)
- insilver-v3-dev: dev (pre-push patterns, без upstream?)
- sam: main (очікує restart + notebook recovery)
- ed, workspace-meta: main (публічні, web_fetch memory)
- abby-v2, garcia, household_agent, kit: main (приватні, ручна пам'ять)

## Open questions

- Чи `git push` без set-upstream нормально для Model A (insilver-v3-dev)?
- Чи legacy скрипти на видалення прямо тепер, чи залишити для審計?
- Чи перевірка на Pi5 (SSH без X11) потребує окремого тесту, чи достатньо locl validation?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: `tmux-restore.sh` за вікна (2026-05-06).
- sam.service restart — на черзі після P2 (dangling UUID).
- kit migration на HOT/WARM/COLD — коли буде час.
- chkp v3.4 перевірка на не-meta проектах — видалення legacy очікується (2026-05-04).
- PROMPT.md верифікація: після чекпоінту git status має бути чистим.
- cross-project workflow: cd insilver-v3-dev && chkp meta — тестовано на meta, потреба перевірки на не-meta.
