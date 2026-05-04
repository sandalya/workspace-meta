---
project: meta
updated: 2026-05-04
---

# HOT — meta

## Now

BACKLOG cleanup цикл #2: закрито 3 пункти (chkp3 max_tokens + xclip + abby-v1 repo). Commit e1f5439 силенціював xclip stdout помилки. Беклог готовий для P2: Sam NBLM Інтервенція 1 (dangling UUID) або InSilver pre-commit hook варіант (б).

## Last done

**2026-05-04** — BACKLOG cleanup #2 (~30 хв):

- **Пункт 3 закритий (chkp3 max_tokens):** Верифіковано що max_tokens=2000 актуальний в chkp.py, достатній для повних HOT/WARM відповідей. Потреба підвищення до 4096 не визначена, залишено як есть.
- **Пункт 5 закритий (chkp xclip validation):** Commit e1f5439 додав xclip guard — DISPLAY check перед викликом + stderr=DEVNULL. На SSH без X11 (Pi5) мовчазно повертає False без noise. Протестовано на Pi5 (headless), працює.
- **Пункт (abby-v1 repo):** Верифіковано що abby-v1 локально не потребуємо (код давно архівний), GitHub repo готовий до видалення у Settings → Danger Zone.
- **Список 1-16 статус:** пункти 1-2 (commit cdf1af6 — чkp инфра) + 3-5 (commit e1f5439 + 7cd3f8b — дрібниці + xclip) закриті. Лишилось 11 пунктів. Беклог оптимізований для P2.

## Next

1. **abby-v1 GitHub repo deletion** (~5 хв) — Settings → Danger Zone, ввести `sandalya/abby-v1`, confirm. Перевірити локальний бекап.

2. **PATH binary verifikation на не-meta** (~20 хв) — garcia, abby-v2, ed: `chkp --help` → v3.4, потім cross-project `cd ed && chkp garcia` → перевірити guard поведінку.

3. **Legacy скрипти видалення** (~10 хв) — після підтвердження: kit/chkp.sh, kit/chkp2.sh, meta/legacy/chkp_bash_v1/chkp.sh. chkp.py.bak залишити.

4. **Вибір наступного пункту беклогу** — OR пункт 8 (InSilver pre-commit hook fix, варіант б: залишити тільки існуючі тести) OR пункт 11 (Sam manual stop in-flight task — перевірити Bonus B1+B2).

5. **Sam NBLM Інтервенція 1** (~30 хв, після vidval beклогу) — dangling UUID detection в `sam/core/content_gen/backends/nblm.py`, метод `get_or_create_notebook`. UUID 0daaf506, 2d0285dd. Рішення: `probe source list -n --json` + fallthrough create. Тест: restart sam.service.

## Blockers

Немає критичних. abby-v1 потребує ручної GitHub операції (Settings), інші пункти локальні.

## Active branches

- meta: main (v3.4 PATH binary stable, дрібниці цикл завершено)
- insilver-v3-dev: dev (pre-push patterns актуалізовані)
- sam: main (очікує Inter 1 + restart)
- abby-v1: main (на видалення)
- ed, workspace-meta, garcia, abby-v2: main (різні стани)

## Open questions

- Чи abby-v1 видалити локальний checkout у workspace~
- Пункт 8 або пункт 11 — який далі?
- Чи набути на не-meta перевірка видалить legacy скрипти сьогодні чи пізніше?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: `tmux-restore.sh` (2026-05-06).
- kit міграція на HOT/WARM/COLD — коли буде час.
- legacy/.gitignore синхронізація у всіх проектах.