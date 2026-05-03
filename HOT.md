---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

chkp v3.4 — PATH binary шим стабілізований. Усі звернення (PuTTY, CC, subshell, cron) тепер йдуть на v3.4 через Python shim у ~/.local/bin/chkp. Legacy bash v1 видалена. Потреба фінальної верифікації на не-meta проекті (sam/insilver/garcia/abby) — чи commit_backlog коректно робить окремий коміт у meta repo.

## Last done

**2026-05-03** — інфра-фікс PATH binary: стабілізація v3.4 (40 хв):

- **Створено Python shim** — `/home/sashok/.local/bin/chkp` замість bash v1 скрипту.
- **Верифікація на meta** — `bash -c chkp --help` показує v3.4 з --backlog-strike, --backlog-add, --sonnet.
- **Очищено legacy** — kit/chkp.sh, kit/chkp2.sh, meta/chkp.sh перенесені в meta/legacy/chkp_bash_v1/.
- **SESSION.md видалено** — артефакт старого v1 запуску, додане в .gitignore.
- **WARM оновлено** — memory rule про chkp під v3.4, backlog-flags workflow задокументовано.

## Next

1. **Перевірити v3.4 на не-meta проекті** — запустити `chkp <project>` на sam/insilver/garcia/abby, перевірити що commit_backlog коректно створює окремий коміт у meta repo для такого проекту.
2. **Видалити legacy skrypty** — якщо v3.4 працює стабільно на не-meta, видалити:
   - `/home/sashok/workspace/kit/chkp.sh` (v1 reference)
   - `/home/sashok/workspace/kit/chkp2.sh` (тест v2)
   - `meta/chkp.py.bak` (backup v3.0, 15K, 23.04) — на тепер залишити, git історія все має
3. **Синхронізувати .gitignore в усіх проектах** — чи SESSION.md, .bak, legacy/ вже там (або потреба batch-update).
4. **Документувати PATH binary вибір** — notes/chkp-binary-vs-script.md для майбутніх розробників.

## Blockers

Немає. Готово до тестування на не-meta.

## Active branches

- meta: main (v3.4 з PATH binary, WARM обновлено, legacy/ структуровано)
- kit: main (legacy chkp.sh залишається для reference)
- Усі 9 проектів на main, синхронізовані з GitHub
- Remote dev: Pi5 через Tailscale + Termius

## Open questions

- Чи commit_backlog коректно працює для не-meta проектів (окремий коміт у meta)?
- Чи потреба збережувати meta/chkp.sh для документації або видалити як технічний борг?
- Чи є інші legacy скрипти в workspace що потребують cleanup?
- Чи синхронізовані .gitignore файли в усіх проектах під один стандарт?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи, використовувати для тестування нових фіч в реальних умовах.
- chkp v3.4 (PATH binary) — задокументувати у notes/ для майбутніх розробників (як вибір між alias vs binary).
- Розглянути systemd service для auto-update BACKLOG assistant через timer (периодичний `chkp meta --backlog-only`).
- chkp.py.bak (15K, 23.04, v2 до триярусної памʼяті) залишений у chkp/ — git історія вже має все, але .bak не заважає на тепер.
