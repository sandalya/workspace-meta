---
project: meta
updated: 2026-05-04
---

# HOT — meta

## Now

Sprint A завершено за один SSH-крок. Smoke-test 4/4 зелений. Беклог очищено: видалено NBLM-05-02 (28 рядків), реорганізовано Sam NBLM як 5 Інтервенцій. Активна послідовність: abby-v1 видалення → PATH binary перевірка на не-meta (garcia, abby-v2, ed) → legacy скрипти видалення → Sam NBLM Інтервенція 1 (dangling UUID).

## Last done

**2026-05-04** — Sprint A completion + BACKLOG cleanup #2 (~2.5 год):

- **Pre-push hook patterns (insilver-v3-dev):** Звужено whitelist до incoming/+clients/, видалено blanket digit-fallback що ловив static/. Telegram client-ID формат: [0-9]{9,}_.*. Комітовано у .git/hooks/pre-push.
- **Beklog audit (5 пунктів):**: 
  - Пункт 3 (chkp3 max_tokens): Верифіковано max_tokens=2000 достатній, залишено як есть.
  - Пункт 5 (chkp xclip): Commit e1f5439 додав DISPLAY check + stderr=DEVNULL, протестовано на Pi5 headless, працює.
  - abby-v1 repo: Верифіковано архівний, готовий до GitHub видалення.
  - CLAUDE.md: Текст коректний, уточнення у commit 99330fa.
  - insilver pre-commit hook: Перевірено, коректний (раніше переписаний).
- **BACKLOG реорганізація:** Видалено superseded NBLM-05-02 (28 рядків), переведено Sam NBLM в послідовність 5 Інтервенцій, класифіковано DONE (1-3) / TODO (4-7).
- **Статус беклогу:** Пункти 1-5 закриті, лишилось 11 пунктів. Беклог оптимізований для P2.
- **Дрібниці з попередніх сесій:** PROMPT.md flow (перед git add), xclip guard з stderr=DEVNULL, chkp guard рефакторинг для cross-project workflow.

## Next

1. **abby-v1 GitHub repo deletion** (~5 хв) — Settings → Danger Zone, ввести `sandalya/abby-v1`, confirm. Перевірити локальний бекап.

2. **PATH binary verification на не-meta** (~20 хв) — garcia, abby-v2, ed: `chkp --help` → v3.4, потім cross-project `cd ed && chkp garcia` → перевірити guard поведінку без warning.

3. **Legacy скрипти видалення** (~10 хв) — після підтвердження v3.4: kit/chkp.sh, kit/chkp2.sh, meta/legacy/chkp_bash_v1/chkp.sh (окрім chkp.py.bak). Синхронізувати .gitignore у всіх проектах (додати SESSION.md).

4. **Sam NBLM Інтервенція 1** (~30 хв) — dangling UUID detection в `sam/core/content_gen/backends/nblm.py`, метод `get_or_create_notebook`. UUID 0daaf506, 2d0285dd. Рішення: `probe source list -n --json` + fallthrough create. Тест: restart sam.service.

## Blockers

Немає критичних. abby-v1 потребує ручної GitHub операції (Settings), інші пункти локальні.

## Active branches

- meta: main (v3.4 PATH binary stable, дрібниці цикл завершено, готово до P2)
- insilver-v3-dev: dev (pre-push patterns актуалізовані)
- sam: main (очікує Inter 1)
- abby-v1: main (на видалення)
- ed, garcia, abby-v2: main (чекають PATH binary верифікації)

## Open questions

- Видалити abby-v1 локальний checkout у workspace разом з GitHub репо або окремо?
- PATH binary верифікація на не-meta створить дублі legacy скриптів в .gitignore чи видалити фізично?
- Чи потреба окремих legacy гілок у проектах або повне видалення?
- kit міграція на HOT/WARM/COLD — коли буде час?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: `tmux-restore.sh` (2026-05-06).
- kit міграція на HOT/WARM/COLD — коли буде час.
- legacy/.gitignore синхронізація у всіх проектах (додати SESSION.md).
- Перевірити .env дублікати у проектах — локальні копії на очищення?
