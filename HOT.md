---
project: meta
updated: 2026-05-04
---

# HOT — meta

## Now

GitHub abby-v1 repo deletion completed. Prompt caching baseline smoke test 1 setup done. Sprint A infrastructure stable (chkp v3.4 PATH binary, max_tokens=2000, xclip guard verified). Backlog 11/16 pункти remaining. Active sequence: PATH binary verification на не-meta (garcia, abby-v2, ed) → legacy скрипти видалення → Sam NBLM Інтервенція 1.

## Last done

**2026-05-04** — Finalization before P2 transition (~1.5 год):

- **abby-v1 GitHub deletion:** Settings → Danger Zone, ввід `sandalya/abby-v1`, confirmed. Локальний бекап перевірено.
- **Prompt caching smoke test 1 baseline:** Додано claude.yaml інструкція (MEMORY.md rule #42). Подготовка для cache_creation_input_tokens > 0 верифікації на першому claude.ai запиті. Метрика готова. Документація шаблон у notes/PROMPT-CACHING.md (на заповнення після першого запиту).
- **Sprint A summary:** chkp max_tokens=2000 (OK), xclip DISPLAY guard (OK на Pi5 headless), abby-v1 GitHub (deleted). BACKLOG очищено (1-5 пункти DONE, 11 remaining). Інфра стабільна.

## Next

1. **PATH binary verification на не-meta** (~25 хв) — garcia, abby-v2, ed:
   - Для кожного: `chkp --help` → перевірити v3.4 у output
   - Cross-project тест: `cd ed && chkp garcia` → guard повинна бути мовчазною (не в ed-dev)
   - Документувати результати у WARM

2. **Legacy скрипти видалення** (~10 хв) — коли PATH binary верифікація OK:
   - kit/chkp.sh (v1 reference)
   - kit/chkp2.sh (test v2)
   - meta/legacy/chkp_bash_v1/chkp.sh (копія v1)
   - Залишити: chkp.py.bak (git історія)

3. **Prompt caching first call на claude.ai** (~20 хв) — коли буде наступна claude-сесія на інші проекти:
   - Додати інструкцію в prompt
   - Перевірити response_metadata: cache_creation_input_tokens > 0
   - Записати результат у notes/PROMPT-CACHING.md

4. **Sam NBLM Інтервенція 1** (~30 хв) — после PATH binary cleanup:
   - File: sam/core/content_gen/backends/nblm.py, method: get_or_create_notebook
   - Проблема: UUID 0daaf506 (rag_retrieval-1) на неіснуючих notebook'ах
   - Рішення: `probe source list -n --json` перед reuse, інвалідація nblm_notebook_id на RPC fail
   - Тест: sam.service restart, manual check у sam/notebooks

## Blockers

Немає. Усі пункти незалежні, можна паралельно (PATH на трьох проектах одночасно).

## Active branches

- meta: main (v3.4 PATH stable, abby-v1 видалено, готово до legacy cleanup + P2)
- insilver-v3-dev: dev (pre-push patterns OK)
- sam: main (очікує Inter 1 dangling UUID fix)
- garcia, abby-v2, ed: main (чекають PATH binary верифікації)

## Open questions

- Чи cache_creation_input_tokens показується в claude.ai в response section чи тільки при API inspect?
- Видалити kit/legacy скрипти одним commit'ом чи per-project?
- Чи потреба .gitignore update у kit після видалення chkp.sh, chkp2.sh?
- Чи abby-v1 локальна папка (~/openclaw/workspace/abby-v1/) розглядається как окремий проект чи просто видалити вручну?

## Reminders

- Prompt caching baseline документувати у notes/PROMPT-CACHING.md після першого real запиту
- Kit міграція на HOT/WARM/COLD структуру — коли PATH binary cleanup завершено
- tmux-restore.sh на Pi5 — TODO 2026-05-06
- Синхронізувати .gitignore у всіх проектах (SESSION.md, legacy скрипти запети)