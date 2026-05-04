---
project: meta
updated: 2026-05-04
---

# HOT — meta

## Now

BACKLOG cleanup: видалено superseded NBLM-05-02 секцію + реорганізовано Sam NBLM tech debt (DONE → TODO послідовність). Наступний крок: abby-v1 GitHub repo deletion, потім швидкі чекпоінти (max_tokens, xclip).

## Last done

**2026-05-04** — BACKLOG cleanup + Sam NBLM реорганізація (~45 хв):

- **BACKLOG видалено NBLM-05-02** (~5 хв): Superseded секція з 28 рядків видалена (раніше була як застаріла фаза). Беклог тепер компактніший, фокус на активних пунктах.
- **Sam NBLM tech debt переорганізовано** (~20 хв): Переформатовано як послідовність 5 Інтервенцій (Сесія 1 = Inter 1 за структурою). Залежності актуалізовані: DONE (пункти 1,2,3 тепер DONE з попередніх циклів чkp/security), TODO (пункти 4,5,6,7 активні на черзі). Добавлено BLOCKED статус для деяких шляхів залежності. Запис у WARM.md під «Sam NBLM tech debt — série підзадач».
- **Залежності consolidation** (~10 хв): Перевірено що Inter 1 (dangling UUID) розблокує rag_retrieval-1; міграція на WARM як reference для прогресу. Потреба тестування на live restart sam.service.
- **Beклог ready для P2**: Sam NBLM Inter 1 (dangling UUID detection) може стартувати одразу після abby-v1 видалення.

## Next

1. **abby-v1 GitHub repo deletion** (~5 хв) — Settings → Danger Zone, ввести `sandalya/abby-v1`, confirm delete. Потреба перевірки що локальні бекапи є та код не потребуємо.

2. **chkp3 max_tokens quick fix** (~5 хв) — за списком BACKLOG пункт 4: перевірити що max_tokens=2000 актуальний в chkp.py, якщо треба підвищити до 4096 для повніших HOT/WARM за потребою.

3. **chkp xclip validation** (~10 хв) — BACKLOG пункт 5: перевірити xclip guard на Pi5 (SSH без X11), переконатися DISPLAY check не спричинює повільнення на non-SSH.

4. **Тестування PATH binary на не-meta проектах** (~15 хв) — garcia, abby-v2, ed: `chkp --help`, перевірити версія v3.4, тестуємо cross-project (cd ed && chkp garcia).

5. **Видалення legacy скрипів** (~5 хв) — після підтвердження v3.4 на не-meta: kit/chkp.sh, kit/chkp2.sh, meta/legacy/chkp_bash_v1/. chkp.py.bak залишити для git історії.

6. **Sam NBLM Інтервенція 1** (~30 хв, після abby-v1) — dangling UUID detection в `sam/core/content_gen/backends/nblm.py`, метод `get_or_create_notebook`. Проблема: UUID 0daaf506, 2d0285dd. Рішення: `probe source list -n --json` + fallthrough create. Тест: `sam.service restart`, manual test.

## Blockers

Немає критичних. abby-v1 потребує ручної GitHub операції (Settings), далі перевірка не-meta потребує SSH доступу до інших машин (всі локальні).

## Active branches

- meta: main (v3.4 PATH binary, guard рефакторинг, legacy в архіві)
- insilver-v3-dev: dev (pre-push patterns)
- sam: main (очікує restart після Inter 1)
- abby-v1: main (на видалення)
- ed, workspace-meta: main (публічні, web_fetch)
- abby-v2, garcia: main (приватні)

## Open questions

- Чи abby-v1 видалити разом з локальним checkout'ом у workspace, чи тримати backup?
- Чи max_tokens=2000 достатній для HOT/WARM або підвищити за потребою?
- Чи xclip на Pi5 без X11 потребує окремої перевірки, чи достатньо DISPLAY check?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: `tmux-restore.sh` (2026-05-06).
- kit міграція на HOT/WARM/COLD — коли буде час.
- legacy/.gitignore синхронізація у всіх проектах.
- chkp v3.4 дефінітивна перевірка на non-meta (garcia, ed, abby-v2) — критично для доверу.
