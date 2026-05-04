---
project: meta
updated: 2026-05-04
---

# HOT — meta

## Now

Sprint A завершено + BACKLOG cleanup #2 (~2.5 год). Smoke-test 4/4 зелений. Беклог очищено: видалено NBLM-05-02 (28 рядків), реорганізовано Sam NBLM як 5 Інтервенцій. Активна послідовність: abby-v1 видалення → PATH binary перевірка на не-meta (garcia, abby-v2, ed) → legacy скрипти видалення → Sam NBLM Інтервенція 1 (dangling UUID).

## Last done

**2026-05-04** — BACKLOG cleanup tail: doghnanyy 5-y strike (chkp xclip pid SSH) shcho propustyv u poperednyomu chkp (~1.5 god):

- **Punkkt 5 verification (chkp xclip SSH validation):** Commit e1f5439 dodav DISPLAY check + stderr=DEVNULL. Na SSH bez X11 (Pi5 headless) movchazno povertaye False bez shumu. Prote dovano na Pi5, pracyuye. Urok: --backlog-strike fragment maye buty doslIvnym pidryadskomom zaholovna baklogu (1:1 match).
- **BACKLOG cleanup rezultat:** Punkty 1-5 zakryty, lishylos 11 punktiv. Beklad optymizovanyy dlya P2.
- **Sprint A status:** Zakonchenoezavody SSH-krok. Aktivna poslIDovnist: abby-v1 deletion → PATH binary check ne-meta → legacy scriptu deletion → Sam Inter 1.

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